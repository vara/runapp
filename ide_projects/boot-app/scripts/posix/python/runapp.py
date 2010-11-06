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

from utils.Utils import OSUtil, FSUtil, Timer
from logger.RunAppLogger import RALogger

RALogger.initialize()
RALogger.setRootDebugLevel()

LOG = logging.getLogger("runapp")

# Definition of global variables
#
# SCRIPT_HOME   -- Path to directory where is this script placed
# JAVA_BIN      -- path to java executable file
# WAIT_ON_EXIT  -- wait, before exit script
# TESTING_MODE  -- don't call main program
# PROVIDER      -- java|maven (Default:java)
# DEBUG         -- number of debug level (default:None)
# EXEC_TOOL     -- Tool for execution JVM

# CONFIG_FP     -- Path to configuration file
# DEPENDENCY_FP -- Path to dependency file path
# JVM_ARGS_FP   -- Path to file with jvm arguments

# MAINCLASS     -- Boot class
# PROJECT_DIR   -- Path to root directory calling project
# M2_REPOSITORY -- Path to maven repository
# USER_ARGS_TO_APP --All arguments passed by user
#
# COMMENTCHAR   -- Used in configuration files
# USAGE_FP      -- Path to file with text for usage information

COMMENTCHAR   = '#'
USER_DIR      = os.path.expanduser('~')
CWD           = os.getcwd()
WAIT_ON_EXIT  = 1
PROVIDER      = "java" #HARD CODE FIXME: after implement maven boot util
SCRIPT_HOME   = os.path.dirname(FSUtil.resolveSymlink(sys.argv[0]))

CONFIG_FP     = os.getenv("CONFIG_FP","runapp.conf")
DEPENDENCY_FP = os.getenv("DEPENDENCY_FP","runapp.dep")
JVM_ARGS_FP   = os.getenv("JVM_ARGS_FP","runapp.jvmargs")

TESTING_MODE  = os.getenv("TESTING_MODE")
USAGE_FP      = os.path.dirname(SCRIPT_HOME)+os.sep+"usage.txt"

def exitScript():

	LOG.debug("Wait on exit %d" , WAIT_ON_EXIT)
	time.sleep(WAIT_ON_EXIT)
	exit()

def resolveJavaPath() :

	for value in ("JAVA_HOME","JRE_HOME","JDK_HOME") :
		if os.getenv(value) != None:
			_javaBin = os.getenv(value)
			break
	#_javaBin = None
	if _javaBin == None:
		if OSUtil.isLinux() or OSUtil.isMac():
			_javaBin = commands.getoutput('which java')
		elif OSUtil.isWin():
			try:
				from _winreg import ConnectRegistry,OpenKey,QueryValueEx,CloseKey, HKEY_LOCAL_MACHINE

				LOG.debug("Try to resolve java path from windows registry")
				aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
				aKey1 = OpenKey(aReg, r"SOFTWARE\JavaSoft\Java Runtime Environment")
				JRTVersion = QueryValueEx(aKey1,"CurrentVersion")
				if JRTVersion:
					LOG.debug("JRE ver. %s",JRTVersion[0])
					aKey2 = OpenKey(aKey1, JRTVersion[0])
					regVal = QueryValueEx(aKey2,"JavaHome")
					CloseKey(aKey2)
					if regVal :
						_javaBin = regVal[0]
				LOG.debug("Resolved java path is %s",_javaBin)

				CloseKey(aKey1)
				CloseKey(aReg)

			except ImportError:
				LOG.warn("Module _winreg not found, module needed for resolving Java installation path!")

	if _javaBin !=  None:
		suffix = os.sep+"bin"+os.sep+"java"
		if not _javaBin.endswith(suffix):
			_javaBin += suffix
		_javaBin = FSUtil.resolveSymlink(_javaBin)

	return _javaBin

def readConfig():
	for prefix in ("",CWD+os.sep,USER_DIR+os.sep):
		conf_fp = prefix+CONFIG_FP
		if LOG.isEnabledFor(logging.DEBUG):
			LOG.debug( "ConfigFP:%s",conf_fp)
		if os.path.exists(conf_fp) :
			break
		else:
			LOG.warn("Config file '%s' not exist",conf_fp)
#
# Print info about this script
#
def printInfo():
	print "Author: Grzegorz (vara) Warywoda\nContact: war29@wp.pl\nrunapp v1.0.0\n"


def printUsage():
	printInfo()
	file = open(USAGE_FP,'r')
	content = file.read()
	file.close()
	print "%s" % content


#######################################
#                                     #
# This is Entry point for this script #
#                                     #
#######################################

def main(argv):
	START_TIME_MS = Timer.time()

	try:
		opts, args = getopt.getopt(argv, "hg:d", ["help", "grammar="])

	except getopt.GetoptError:
		printUsage
		exitScript

	JAVA_BIN = resolveJavaPath()
	if not JAVA_BIN:
		LOG.error("Java not found, set JAVA_HOME in envirioment variables")
		exitScript()

	LOG.debug("Script Home: %s ",SCRIPT_HOME)
	LOG.info("Path to java : %s", JAVA_BIN)
	LOG.info("Java-Version : %s",commands.getoutput(JAVA_BIN + " -version"))
	readConfig()

	LOG.info("Elapsed time of preparing of boot application %dms",Timer.time(START_TIME_MS))

	if not TESTING_MODE:
		LOG.info("RUN APP")

if __name__ == "__main__":
	main(sys.argv[1:])
	exitScript()
