# -*- coding: utf-8 -*-

#
# Author: Grzegorz (vara) Warywoda
# Since: 2010-11-05 22:20:20 CET
#

import os
import sys
import commands
import time
import logging
import getopt
import optparse

from utils.Utils import OSUtil, FSUtil, Timer
from logger.RunAppLogger import RALogger
from Configuration import Config,Keys, env

RALogger.initialize()
RALogger.setRootDebugLevel()

LOG = logging.getLogger("runapp")

VERSION       = "1.0.0"

SCRIPT_HOME   = os.path.dirname(FSUtil.resolveSymlink(sys.argv[0]))
USAGE_FP      = os.path.dirname(SCRIPT_HOME)+os.sep+"usage.txt"

def exitScript(exitCode=0):
	wait = Keys.iValue(Keys.WAIT_ON_EXIT)
	if wait and wait>0:
		LOG.debug("Wait on exit %d" , wait)
		time.sleep(wait)

	exit(exitCode)

def readConfig():

	if os.path.exists(Config.getConfigFP()) :

		commentChar = Config.getCommentChar()

		file = open(Config.getConfigFP(),'r')
		fLines = file.readlines()
		file.close()

		for line in fLines:
			line = line.strip()
			if not len(line) == 0:
				index = line.find(commentChar)
				if index != -1:
					line = line[:index]

				if not len(line) == 0:
					index = line.index('=')
					key = line[:index]
					val = line[index+1:]

					env.put(key,val)

	else:
		LOG.warn("Config file '%s' not exist",Config.getConfigFP())
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
	print argPath
	if os.path.isfile(argPath):
		Config.setConfigFP(os.path.basename(argPath))
		argPath = os.path.dirname(argPath)
		retVal = True

	if os.path.isdir(argPath):
		os.chdir(argPath)

		if LOG.isEnabledFor(logging.DEBUG):
			LOG.debug("Directory changed to : %s", os.getcwd())
		retVal = True

	return retVal

#######################################
#                                     #
# This is Entry point for this script #
#                                     #
#######################################

def main(arguments):
	START_TIME_MS = Timer.time()

	if len(arguments)>0:
		if initConfigurationFile(arguments[0]):
			arguments = arguments[1:]

	try:
		opts, args = getopt.getopt(arguments, "hp:c:ve:", ["help","version","testingMode","provider=","conf=","exec="])

		LOG.debug('OPTIONS   : %s', opts)
		LOG.debug('ARGS   : %s', args)

		for o,a in opts:

			LOG.debug("Parsing option %s <=> %s",o,a)

			if o in ("-h", "--help"):
				printUsage()
				exitScript()

			elif o in ("-v", "--version"):
				print "v",VERSION
				exitScript()

			elif o in ("-p", "--provider"):
				Config.setProvider(a)

			elif o in ("-c", "--conf"):

				Config.setConfigFP(a)

			elif o in ("-e", "--exec"):

				Config.setExecTool(a)

			else:
				print "Not found or path {%s}" % o

	except getopt.GetoptError, e :
		LOG.warn("Cmdl options %s",e)
		printUsage()
		exitScript(2)

	if not Config.getJavaBinPath():
		LOG.error("Java not found, set JAVA_HOME in envirioment variables")
		exitScript()

#	LOG.debug("Script Home: %s ",SCRIPT_HOME)
	LOG.info("Path to java : %s", Config.getJavaBinPath())
#	LOG.info("Java-Version : %s",commands.getoutput(JAVA_BIN + " -version"))

	print Keys.retrieveValue("M2")
	readConfig()
	print Keys.retrieveValue("M2")

	LOG.info("Elapsed time of preparing of boot application %dms",Timer.time(START_TIME_MS))

	if not Config.isTestingMode():
		LOG.info("RUN APP")

if __name__ == "__main__":
	main(sys.argv[1:])
	exitScript()
