# -*- coding: utf-8 -*-

#
# Author: Grzegorz (vara) Warywoda
# Since: 2010-11-05 22:20:20 CET
#

import os
import sys
import commands
import time
import getopt
import optparse
from logger import RALogging
from logger.RALogging import RALogger
import subprocess
import signal

RALogging.initialize()

from utils import Utils
from utils.Utils import OSUtil, FSUtil, Timer
from configuration.Configuration import Config,Keys, env
from configuration.Parser import ParserManger

START_TIME_MS = Timer.time()

VERSION       = "1.0.0"

USAGE_FP      = os.path.dirname(Config.getScriptRootPath())+os.sep+"usage.txt"

#RALogger.setRootDebugLevel()

LOG = RALogging.getLogger("runapp")
#LOG.setLevel(RALogging.DEBUG)

def exitScript(exitCode=0):
	wait = Keys.iValue(Keys.WAIT_ON_EXIT)
	if wait and wait>0:

		if LOG.isDebug(2):
			LOG.ndebug(2,"Wait on exit %d" , wait)

		time.sleep(wait)

	exit(exitCode)

def readConfig2(path,parserName="bash-parser"):
	if os.path.exists(path) :

		parser = ParserManger.getParserByName(parserName)
		if parser:
			parser.setAutoUpdateEnv(False)
			parser.open(path)
			results = parser.results()
			return results
		else:
			LOG.warn("Parser '%s' not found !",parserName)

	else:
		LOG.warn("Config file '%s' not exist",path)

def readConfig(path,parserName="bash-parser"):

	if os.path.exists(path) :

		parser = ParserManger.getParserByName(parserName)
		if parser:
			parser.open(path)
			results = parser.results()
			return results
		else:
			LOG.warn("Parser '%s' not found !",parserName)

	else:
		LOG.warn("Config file '%s' not exist",path)


def __toCommandLineString(list,separator=':'):
	cmdLine = ""

	if list:
		for (k,v) in list:
			cmdLine += k
			if v:
				cmdLine+="="+v
			cmdLine+=separator

	return cmdLine
#
# Print info about this script
#
def printInfo():
	print "Author: Grzegorz (vara) Warywoda\nContact: war29@wp.pl\nrunapp v%s\n" % VERSION

def printUsage():
	printInfo()
	file = open(USAGE_FP,'r')
	content = file.read()
	file.close()
	print "%s" % content

def initConfigurationFile(argPath):

	argPath = FSUtil.resolveSymlink(os.path.expanduser(argPath))

	if LOG.isDebug(1):
		LOG.ndebug(1,"Initialize ROOT directory from path '%s'",argPath)

	if os.path.isfile(argPath):

		Config.setConfigFName(os.path.basename(argPath))

		argPath = os.path.dirname(argPath)

	if os.path.isdir(argPath):
		if os.getcwd() != argPath:
			os.chdir(argPath)


def parseArguments(arguments):

	try:
		opts, args = getopt.getopt(arguments, "hp:ve:d:", \
				["help","version","testingMode","provider=","exec=","debug=","mainClass","testingMode"])

		if LOG.isTrace():
			LOG.trace('OPTIONS   : %s', opts)
			LOG.trace('ARGS      : %s', args)

		return opts , args

	except getopt.GetoptError, e :
		LOG.warn("Cmdl options %s",e)
		printUsage()
		exitScript(2)

def initializeCMDLOptions(opts):

	for o,a in opts:

		if LOG.isDebug(2):
			LOG.ndebug(2,"Parsing option '%s' <=> '%s'",o,a)

		if o in ("-h", "--help"):
			printUsage()
			exitScript()

		elif o in ("-v", "--version"):
			print "v",VERSION
			exitScript()

		elif o in ("-p", "--provider"):
			Config.setProvider(a)

		elif o in ("--mainClass",):
			Config.setMainClass(a)

		elif o in ("--testingMode",):
			Config.setTestingMode(True)

		elif o in ("-e", "--exec"):

			Config.setExecTool(a)

		elif o in ("-d","--debug"):
			RALogger.setRootDebugLevel(a)

		else:
			LOG.warn("Not found or path {%s}" , o)

def trapHandler(signal,stackFrame):
	if LOG.isDebug():
		LOG.debug("sig:%d",signal)

def __isOption(val):
	""" Test if current argumnet is commnad line option
	"""
	test = False
	if val:
		test = val[0] == '-'

	return test

def resolveNonOptionFromList(val):

	""" Find first non-option value and return them with his index number.
	 	If value has not been found then the function will return null, other wise will
	 	return tuple containing two elements sequentially : (non-option , index).
	"""
	index = 0
	objNonOptionEnt = None
	objEndMarkEnt = None
	separator = "--"
	for arg in val:

		if arg == separator: #Can override in next round
			if LOG.isDebug(4):
				LOG.ndebug(4,"Encountered to mark the end of arguments on %d index.",index)
			objEndMarkEnt = index

			if objNonOptionEnt: # If we have extracted non-option then we have nothing to do
				break

		if not objNonOptionEnt: # blocked opportunity override
			if __isOption(arg) == False:
				objNonOptionEnt = (arg,index)
				if LOG.isDebug(4):
					LOG.ndebug(4,"Found non-option value => %s",objNonOptionEnt)

		index +=1

	#If found, see whether value should be replaced by separator
	if objNonOptionEnt:

		if not objEndMarkEnt and \
				objNonOptionEnt[1]>0 and \
						objNonOptionEnt[1]<len(val)-1:

			val[objNonOptionEnt[1]] = separator
			if LOG.isDebug(4):
				LOG.ndebug(4,"Replaced non-option value with '%s'",separator)
		else:
			val.pop(objNonOptionEnt[1])
			if LOG.isDebug(4):
				LOG.ndebug(4,"Only removed non-option value")


	return objNonOptionEnt


#######################################
#                                     #
# This is Entry point for this script #
#                                     #
#######################################

def main(rawArguments):

	# Project/root directory can be set on a different ways.
	# On the first place from command line arguments.
	#
	# Search directory in array of arguments.
	# Examined cases:
	#	1. runapp ~/dir -opts -- -appOpts  => ['-opts', '--', '-appOpts']
	#   2. runapp -opts ~/dir -- -appOpts  => ['-opts', '--', '-appOpts'] 
	#   3. runapp -opts -- ~/dir -appOpts  => ['-opts', '--', '-appOpts']
	#   4. runapp -opts -- -appOpts ~/dir  => ['-opts', '--', '-appOpts']
	#   5. runapp -opts ~/dir
	#	6. runapp  ... ( without dir )
	#	7. runapp -opts ~/dir -appOpts     => ['-opts', '--', '-appOpts']
	#
	#   Try find first encountered non-option value and split them.
	#		Then will be wrong in case 7 (-appOpts will be joined to -opts )
	#		sol: Replace found value with end mark char(separator) only then if end mark will not found.
	#			bug: runapp ~/dir -opts => runapp -- -opts !!!
	#		And its index is greater then zero.
	#			e.q  runapp -opts ~/dir ...
	#
	# to case 1. Default parser recognize it as a the arguments for the external application (all to appArguments)
	#		conclusion is that non-option value will be treated as end mark
	#

	val = resolveNonOptionFromList(rawArguments)

	if val:
		initConfigurationFile(val[0])
	
	Config.setProjectDir(os.getcwd())

	appOptions, appArguments = parseArguments(rawArguments)

	# Read config should be before cmdl parsing
	# Allow us to overriding parameters defined in config file
	# Is useful for testing app, when i wants quick change variable

	readConfig(Config.getConfigFName())

	# After loaded configuration, some environments may have changed
	# synchronize configuration with env.
	Config.update()

	initializeCMDLOptions(appOptions)

	appArguments = Keys.USER_ARGS_TO_APP.fromEnv()+' '+Utils.toString(appArguments)

	if not Config.getJavaBinPath():
		LOG.error("Java not found, set JAVA_HOME in envirioment variables")
		exitScript()

	if not Config.getMainClass():
		LOG.error("Main class not found. Please set 'MAINCLASS' variable.")
		exitScript(2)

	dependency = __toCommandLineString(readConfig2(Config.getDependencyFName(),"bash-path-parser"))
	jvmArgs = __toCommandLineString(readConfig2(Config.getJVMArgsFP()),' ')

	provider = Config.getProvider().lower()

	execPath = None
	execArgs = None

	if provider == "java":

		execPath = Config.getJavaBinPath()
		execArgs = jvmArgs

		if len(dependency) > 1:
			execArgs += " -cp "+dependency

		execArgs += " "+Config.getMainClass()+" "+appArguments

	elif provider == "maven":
		LOG.warn("Maven provider not implenebted yet !")
		exitScript(0)
	else:
		LOG.error("Unrecongnized provider %s !",provider)
		exitScript(2)

	if LOG.isDebug():

		LOG.debug("Exec tool: '%s'",Config.getExecTool())
		LOG.debug("Exec path: '%s'",execPath)
		LOG.debug("JVM Parameters: '%s'",jvmArgs)
		LOG.debug("Main class: '%s'",Config.getMainClass())
		LOG.debug("User args: '%s'",appArguments)

	LOG.info("Elapsed time of preparing of boot application %dms",Timer.time(START_TIME_MS))

	if not Config.isTestingMode():

		workingTime = Timer.time()
		cmd = Utils.toString( (Config.getExecTool(),execPath,execArgs))
		process = subprocess.Popen(cmd, shell=True)

		if LOG.isDebug():
			LOG.debug("Created new process with PID:%d.",process.pid)

		signal.signal(signal.SIGINT,trapHandler)

		process.wait()

		LOG.info("Application working time: %d",Timer.time(workingTime))

		if LOG.isDebug():
			LOG.debug("The application has finished work ! [exitcode:%d]",process.returncode)


if __name__ == "__main__":
	main(sys.argv[1:])
	exitScript()
