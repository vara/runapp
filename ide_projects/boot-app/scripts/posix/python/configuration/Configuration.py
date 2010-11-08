# -*- coding: utf-8 -*-

import os
import sys
import logging
import UserDict
from utils import Utils

LOG = logging.getLogger("configuration")

PROVIDERS = ("java","maven")

class KeyEntry(object):
	__key = None
	__defaultVal = None

	def __init__(self,key,defaultValue=None):
		self.__key = key
		self.__defaultVal = defaultValue

	def getKey(self):
		return self.__key

	def getDefaultValue(self):
		return self.__defaultVal

	def __str__(self):
		return "KeyEntry["+str(self.__key)+","+str(self.__defaultVal)+"] on "+hex(id(self))


class _Env (object):
	_dict = None

	def __init__(self):
		if not _Env._dict:
			_Env._dict = dict()

	@staticmethod
	def put(kEntry,value):
		LOG.debug("Insert to map %s:%s",kEntry,value)

		_Env._dict.update( [[kEntry , value]] )

	@staticmethod
	def put(dic):
		LOG.debug("Insert to map %s",dict)
		_Env._dict.update( dic )

	@staticmethod
	def getVal(kEntry,defaultVal=None):

		retValue = None
		if kEntry:
			if isinstance(kEntry,KeyEntry):
				if not defaultVal:
					defaultVal = kEntry.getDefaultValue()
				kEntry = kEntry.getKey()

			retValue = _Env._dict.get(kEntry)
			if not retValue:
				retValue = os.getenv(kEntry)

		if not retValue: retValue = defaultVal

		#LOG.debug("GetValue for Key: '%s', default: '%s' return: %s",kEntry,defaultVal,retValue)
		return retValue

	@staticmethod
	def getKeys():
		return _Env._dict.keys()

	@staticmethod
	def prints():
		print _Env._dict

	@staticmethod
	def getDic():
		return _Env._dict

env = _Env()

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
# PROJECT_DIR   -- Path to root directory where $CONFIG_FP is placed
# M2_REPOSITORY -- Path to maven repository
# USER_ARGS_TO_APP --All arguments passed by user
#
# COMMENTCHAR   -- Used in configuration files
# USAGE_FP      -- Path to file with text for usage information

class Keys(object):

	CONFIG_FP = KeyEntry("CONFIG_FP","runapp.conf")
	DEPENDENCY_FP = KeyEntry("DEPENDENCY_FP","runapp.dep")
	JVM_ARGS_FP = KeyEntry("JVM_ARGS_FP","runapp.jvmargs")
	EXEC_TOOL = KeyEntry("EXEC_TOOL")
	M2_REPOSITORY = KeyEntry("M2_REPOSITORY")
	MAIN_CLASS =  KeyEntry("MAINCLASS")
	TESTING_MODE = KeyEntry("TESTING_MODE")
	WAIT_ON_EXIT = KeyEntry("WAIT_ON_EXIT","1")

	"""test"""
	_HOME = KeyEntry("HOME")
	_M2 = KeyEntry("M2")

	_list = ( CONFIG_FP,
			  DEPENDENCY_FP, \
			  JVM_ARGS_FP, \
			  EXEC_TOOL, \
			  M2_REPOSITORY, \
			  MAIN_CLASS, \
			  TESTING_MODE, \
			  WAIT_ON_EXIT,
			  _HOME,_M2)

	@staticmethod
	def retrieveValue(entry):
		retValue = None
		if isinstance(entry,str):
			entry = Keys.getKeyFromString(entry)
		if entry:
			retValue = env.getVal(entry)

		return retValue
		
	@staticmethod
	def iValue(entry):
		val = Keys.retrieveValue(entry)
		if val:
			val = int(val)
		return val

	@staticmethod
	def getKeyFromString(sKey):
		for key in Keys._list:
			if key.getKey() == sKey:
				return key

		return None

class Config(object):

	_commentChar = '#'
	_userDir = os.path.expanduser('~')

	_configFP = Keys.retrieveValue(Keys.CONFIG_FP)
	_dependencyFP = Keys.retrieveValue(Keys.DEPENDENCY_FP)
	_jvmArgumentsFP = Keys.retrieveValue(Keys.JVM_ARGS_FP)

	_M2RepositoryFP = Keys.retrieveValue(Keys.M2_REPOSITORY)

	_provider = PROVIDERS[0]

	_execTool = Keys.retrieveValue(Keys.EXEC_TOOL)
	_mainClass = Keys.retrieveValue(Keys.MAIN_CLASS)
	_testingMode  = Keys.retrieveValue(Keys.TESTING_MODE)

	_javaBinPath = None

	@staticmethod
	def getConfigFP():
		return Config._configFP

	@staticmethod
	def getDependencyFP():
		return Config._dependencyFP

	@staticmethod
	def getJVMArgsFP():
		return Config._jvmArgumentsFP

	@staticmethod
	def setConfigFP(path):
		Config._configFP = path
		
		if LOG.isEnabledFor(logging.DEBUG):
			LOG.debug("Override configuration file name to '%s'.",path)

	@staticmethod
	def setDependencyFP(path):
		Config._dependencyFP = path

		if LOG.isEnabledFor(logging.DEBUG):
			LOG.debug("Override dependency file name to '%s'.",path)

	@staticmethod
	def setProvider(provider):
		Config._provider = provider

		if LOG.isEnabledFor(logging.DEBUG):
			LOG.info("Provider has been set to %s",provider)

	@staticmethod
	def setJVMArgsFP(path):
		Config._jvmArgumentsFP = path

		if LOG.isEnabledFor(logging.DEBUG):
			LOG.debug("Override jvm_args file name to '%s'.",path)

	@staticmethod
	def setExecTool(tool):
		Config._execTool = tool

		if LOG.isEnabledFor(logging.DEBUG):
			LOG.debug("Set exec tool '%s'.",tool)

	@staticmethod
	def setMainClass(mainClass):
		Config._mainClass = mainClass

		if LOG.isEnabledFor(logging.DEBUG):
			LOG.debug("Set main class to '%s'.",mainClass)
	@staticmethod
	def setTestingMode(testingMode):
		Config._testingMode = testingMode

		if LOG.isEnabledFor(logging.DEBUG):
			LOG.debug("Set testing mode to '%s'.",testingMode)

	@staticmethod
	def getUserDir():
		return Config._userDir

	@staticmethod
	def getM2Repository():
		if not Config._M2RepositoryFP:
			Config._M2RepositoryFP = Config._userDir+os.sep+".m2"+os.sep+"repository"
		return Config._M2RepositoryFP

	@staticmethod
	def getJavaBinPath():
		if not Config._javaBinPath:
			Config._javaBinPath = Utils.resolveJavaPath()
		return Config._javaBinPath

	@staticmethod
	def getProvider():
		return Config._provider

	@staticmethod
	def getExecTool():
		return Config._execTool

	@staticmethod
	def getMainClass():
		return Config._mainClass

	@staticmethod
	def isTestingMode():
		if Config._testingMode:
			return True
		return False

	@staticmethod
	def getCommentChar():
		return Config._commentChar


	""" test """

if __name__ == "__main__":
	key = Keys.getKeyFromString("HOME")
	print key

	print "Retrieve user home fromString:",Keys.retrieveValue("HOME"), ";FromObject:",Keys.retrieveValue(key)

	print env.getVal(Keys.M2_REPOSITORY)

	env.prints()
