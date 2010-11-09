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

USAGE_FP      = os.path.dirname(Config.getScriptLocation())+os.sep+"usage.txt"

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

	retVal = None
	argPath = FSUtil.resolveSymlink(os.path.expanduser(argPath))

	if LOG.isDebug(1):
		LOG.ndebug(1,"Initialize ROOT directory from path '%s'",argPath)

	if os.path.isfile(argPath):

		Config.setConfigFName(os.path.basename(argPath))

		argPath = os.path.dirname(argPath)
		retVal = True

	if os.path.isdir(argPath):
		if os.getcwd() != argPath:
			os.chdir(argPath)
			Config.setProjectDir(os.getcwd())
		retVal = True

	return retVal

def checkPaths(list,autoRemove=True):
	for k,v in list:
		if not os.path.exists(k):
			LOG.warn("!!! NOT EXIST '%s'",k)
			list.remove((k,v))

	return list

def parseArguments(arguments):

	try:
		opts, args = getopt.getopt(arguments, "hp:ve:d:", \
				["help","version","testingMode","provider=","exec=","debug=","mainClass","testingMode"])

		if LOG.isTrace:
			LOG.trace('OPTIONS   : %s', opts)
			LOG.trace('ARGS      : %s', args)

		for o,a in opts:

			if LOG.isDebug(2):
				LOG.ndebug(2,"Parsing option %s <=> %s",o,a)

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


		return args

	except getopt.GetoptError, e :
		LOG.warn("Cmdl options %s",e)
		printUsage()
		exitScript(2)

PROCESS = None

def trapHandler(signal,stackFrame):
	if LOG.isDebug():
		LOG.debug("sig:%d",signal)

#######################################
#                                     #
# This is Entry point for this script #
#                                     #
#######################################

def main(rawArgs):

	if len(rawArgs)>0:
		if initConfigurationFile(rawArgs[0]):
			rawArgs = rawArgs[1:]

	# Read config should be before cmdl parsing
	# Allow us to overriding parameters defined in config file
	# Is useful for testing app, when i wants quick change variable

	readConfig(Config.getConfigFName())

	Config.update()

	args = parseArguments(rawArgs)

	argumentsToApp = Keys.USER_ARGS_TO_APP.fromEnv()+' '+Utils.toString(args)

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

		execArgs += " "+Config.getMainClass()+" "+argumentsToApp

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
		LOG.debug("User args: '%s'",argumentsToApp)

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

		LOG.debug("The application has finished work ! [exitcode:%d]",process.returncode)


if __name__ == "__main__":
	main(sys.argv[1:])
	exitScript()
