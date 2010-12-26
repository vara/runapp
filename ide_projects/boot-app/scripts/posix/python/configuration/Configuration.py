# -*- coding: utf-8 -*-

import os
import sys
import logging
from types import *
import RootDir

LOG = logging.getLogger("configuration")

PROVIDERS = ("java","maven")

class KeyEntry(object):
	__key = None
	__defaultVal = None

	def __init__(self,key,defaultValue=None):

		KeyEntry.isValid(key)

		self.__key = intern(key)
		self.__defaultVal = defaultValue
		#print self

	def getKey(self):
		return self.__key

	def getDefaultValue(self):
		return self.__defaultVal

	def reg(self):
		"""
			Register itself to Keys container
		"""
		Keys.registerKey(self)

	def fromEnv(self):
		""" Retrieve value from local environment variables.
			If declaration of this object has not been found then
			returned value will be the equivalent with self.getDefaultValue
		"""
		return env.getEnv(self)

	@staticmethod
	def _isValid(key_name):

		length = len(key_name)
		if length > 70 or length == 0 :
			raise Exception("Name '%s' is too long must be less than 70 characters." % key_name)

		for char in key_name:
			if not KeyEntry.isValid(char):
				raise Exception("Name '%s' contains illegal character '%s' " % (key_name,char))

	@staticmethod
	def isValid(char) :
	    return KeyEntry.isAlpha(char) or KeyEntry.isDigit(char) or char == '_' or char == '-'

	@staticmethod
	def isAlpha(char):
	    return (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z')

	@staticmethod
	def isDigit(char) :
	    return char >= '0' and char <= '9'

	def __str__(self):
		return self.__class__.__name__+"[ "+str(self.__key)+" , "+str(self.__defaultVal)+" ]"

KeyEntryType = KeyEntry

class _Env (object):

	""" Encapsulate data ..."""

	_dict = {}
	_exported = []

	@staticmethod
	def put(newValue):

		# Maybe add inspection whether element will be overwritten etc.
		_Env._dict.update( newValue )

		if LOG.isEnabledFor(logging.DEBUG-2):
			LOG.debug("Inserted '%s' to environment variables",newValue)

	@staticmethod
	def getVal(key,defaultValue=None):
		# search in local map
		retValue = _Env._dict.get(key)

		if not retValue:
			#search in global map
			retValue = os.getenv(key)

		if not retValue:
			retValue = defaultValue

		return retValue

	@staticmethod
	def getLocalKeys():
		return _Env._dict.keys()

	@staticmethod
	def prints():
		print _Env._exported
		print _Env._dict
		print os.environ

	@staticmethod
	def export(key,value=None):
		if key:
			if not key in _Env._exported:
				_Env._exported.append(key)
			if not key in _Env._dict:
				_Env.put( [[key,value]] )

	@staticmethod
	def unset(key):
		if key:
			if key in _Env._exported:
				_Env._exported.remove(key)
			if _Env._dict.has_key(key):
				_Env._dict.pop(key)
			if os.environ.has_key(key):
				os.environ.pop(key)

	@staticmethod
	def getExportedVar():
		mapOfExportedVars = dict(os.environ)
		for key in _Env._exported:
			val = _Env.getVal(key)
			mapOfExportedVars.update([[key,val]])

		return mapOfExportedVars

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

class Keys(object):

	CONFIG_FName 	= KeyEntry("CONFIG_FP","runapp.conf")
	DEPENDENCY_FName= KeyEntry("DEPENDENCY_FP","runapp.dep")
	JVM_ARGS_FName 	= KeyEntry("JVM_ARGS_FP","runapp.jvmargs")
	EXEC_TOOL 		= KeyEntry("EXEC_TOOL","")
	M2_REPOSITORY 	= KeyEntry("M2_REPOSITORY",
							 os.path.expanduser('~')+os.sep+".m2"+os.sep+"repository")
	MAIN_CLASS 		= KeyEntry("MAINCLASS")
	TESTING_MODE	= KeyEntry("TESTING_MODE")
	WAIT_ON_EXIT 	= KeyEntry("WAIT_ON_EXIT","1")
	PRJ_DIR 		= KeyEntry("PROJECT_DIR" , os.getcwd() )
	USER_ARGS_TO_APP= KeyEntry("USER_ARGS_TO_APP",'')
	LOG_CONF_FP 	= KeyEntry("LOG_CONF_FP","resources/configuration/logger/logging.conf")
	PROVIDER 		= KeyEntry("PROVIDER","java")

	"""test"""
	_HOME = KeyEntry("HOME")
	_M2 = KeyEntry("M2")

	__list = [ CONFIG_FName,
			  DEPENDENCY_FName,
			  JVM_ARGS_FName,
			  EXEC_TOOL,
			  M2_REPOSITORY,
			  MAIN_CLASS,
			  TESTING_MODE,
			  WAIT_ON_EXIT,
			  _HOME,
			  _M2,
			  PRJ_DIR,
			  USER_ARGS_TO_APP,
			  LOG_CONF_FP,
			  PROVIDER ]

	@staticmethod
	def getKeyFromString(sKey):
		for key in Keys.__list:
			if key.getKey() == sKey:
				return key
		return None

	@staticmethod
	def registerKey(key_entry):
		if issubclass(type(key_entry),KeyEntryType):
			Keys.__list.append(key_entry)
		else:
			LOG.warn("You trying to added wrong type of object."
				"Object: '%s' is not subclass of '$s'",type(key_entry),KeyEntryType)

	@staticmethod
	def printAllKeys():
		for key in Keys.__list:
			print key

class Config(object):

	__isJar = False

	# Immutable values

	__scriptLocation = None

	__scriptRootPath = None

	__javaBinPath = None

	__userDir = os.path.expanduser('~')

	@staticmethod
	def update():

		if LOG.isEnabledFor(logging.DEBUG):
			LOG.debug("Update environment variables !")

		tmpPrjDir = Config.getProjectDir()
		if tmpPrjDir != os.getcwd():
			tmpPrjDir = os.path.abspath(tmpPrjDir)
			os.chdir(tmpPrjDir)
			if LOG.isEnabledFor(logging.DEBUG-2):
				LOG.debug("Directory changed to %s" % tmpPrjDir)


	@staticmethod
	def getScriptLocation():

		""" Return the path to directory where boot script is placed.
		"""
		if not Config.__scriptLocation:
			Config.__scriptLocation = os.path.dirname(os.path.abspath(sys.argv[0]))

		return Config.__scriptLocation

	@staticmethod
	def getScriptRootPath():

		""" Return the path to root directory of this script.
			This path can be used as relative base point to the external resources.

				ScriptRootDir/		<= base point
					├── resources/
					└── subDir1/

			In practice this path is equivalent with Config.getScriptLocation()
		"""
		if not Config.__scriptRootPath:
			Config.__scriptRootPath = RootDir.determinePath()

		return Config.__scriptRootPath

	@staticmethod
	def getProjectDir():
		return Keys.PRJ_DIR.fromEnv()

	@staticmethod
	def setProjectDir(path):
		
		Config.__setValue(Keys.PRJ_DIR,path)
		# TODO: What does if path not exists?
		# Where should be protection ? before calling?
		os.chdir(path)
		if LOG.isEnabledFor(logging.DEBUG-2):
			LOG.debug("Directory changed to %s" % path)

	@staticmethod
	def setConfigFName(path):
		Config.__setValue(Keys.CONFIG_FName,path)

	@staticmethod
	def setDependencyFName(path):
		Config.__setValue(Keys.DEPENDENCY_FName,path)

	@staticmethod
	def setProvider(provider):
		Config.__setValue(Keys.PROVIDER,provider)

	@staticmethod
	def setJVMArgsFName(path):
		Config.__setValue(Keys.JVM_ARGS_FName,path)

	@staticmethod
	def setExecTool(tool):
		Config.__setValue(Keys.EXEC_TOOL,tool)

	@staticmethod
	def setMainClass(mainClass):
		Config.__setValue(Keys.MAIN_CLASS,mainClass)

	@staticmethod
	def setTestingMode(testingMode):
		Config.__setValue(Keys.TESTING_MODE,testingMode)

	@staticmethod
	def __setValue(Key,value):
		oldVal = Key.fromEnv()
		if oldVal != value:
			env.putEnv(Key,value)

			if oldVal and LOG.isEnabledFor(logging.DEBUG):
				LOG.debug("Override '%s' value '%s' => '%s'.",Key.getKey(),oldVal,value)

	@staticmethod
	def getConfigFName():
		return Keys.CONFIG_FName.fromEnv()

	@staticmethod
	def getDependencyFName():
		return Keys.DEPENDENCY_FName.fromEnv()

	@staticmethod
	def getJVMArgsFP():
		return Keys.JVM_ARGS_FName.fromEnv()

	@staticmethod
	def getUserDir():
		return str(Config.__userDir)

	@staticmethod
	def getM2Repository():
		return Keys.M2_REPOSITORY.fromEnv()

	@staticmethod
	def getJavaBinPath():
		if not Config.__javaBinPath:
			#!!! Invoked only once, uses for avoiding cyclic dependency with RALogging module.
			#In function RALogging.initialize() is used Keys class

			try:
				from utils import Utils
				Config.__javaBinPath = Utils.resolveJavaPath()
			except ImportError, e:
				LOG.warn("Unable to load Utils module: %s",e)

		return Config.__javaBinPath

	@staticmethod
	def getProvider():
		return Keys.PROVIDER.fromEnv()

	@staticmethod
	def getExecTool():
		return Keys.EXEC_TOOL.fromEnv()

	@staticmethod
	def getMainClass():
		return Keys.MAIN_CLASS.fromEnv()

	@staticmethod
	def isTestingMode():
		return Keys.TESTING_MODE.fromEnv()

	@staticmethod
	def isJar():
		return bool(Config.__isJar)

	@staticmethod
	def setJar(boolean):
		Config.__isJar = bool(boolean)

class env:
	""" Access to the Local environment variables via this object.
	"""
	@staticmethod
	def putEnv(key,value=None):

		if key:

			entryType = type(key)

			if LOG.isEnabledFor(5):#trace
				LOG.log(5,"Insert to Environment typeOf : '%s'", entryType)

			if entryType is StringType:
				newValue = [[key , value]]

			elif issubclass(entryType ,KeyEntryType):

				if not value:
					value = key.getDefaultValue()

				newValue = [[key.getKey(), value]]

			elif entryType is DictType :
				newValue = key

			elif (entryType is ListType) or \
				 			(entryType is TupleType):
				newValue = [ key ]

		_Env.put(newValue)

	@staticmethod
	def getEnv(key,defaultVal=None):

		""" Retrieve value assigned to the 'key'.

			If default value is not defined then try to resolve it.
		"""
		retVal = defaultVal
		if key:

			entryType = type(key)

			#For KeyEntry object
			if issubclass(entryType,KeyEntryType):
				# If defaultValue has not been set explicitly
				# then use value from KeyEntry object
				if not defaultVal:
					defaultVal = key.getDefaultValue()
				key = key.getKey()

			#For string object
			elif entryType == StringType:
				if not defaultVal:
					kEntry = Keys.getKeyFromString(key)
					if kEntry:
						defaultVal = kEntry.getDefaultValue()

			retVal = _Env.getVal(key,defaultVal)

		if LOG.isEnabledFor(logging.DEBUG):
			LOG.debug("GetValue Key: '%s' return: '%s'",(key,defaultVal),retVal)

		return retVal

	@staticmethod
	def export(key,val=None):
		_Env.export(key,val)

	@staticmethod
	def getEnvInt(entry,defaultIntValue=-1):
		val = env.getEnv(entry)

		try:
			val = int(val)
		except :
			val = defaultIntValue

		return val

	@staticmethod
	def getExportedVars():

		return _Env.getExportedVar()

	""" test """

if __name__ == "__main__":
	key = Keys.getKeyFromString("HOME")
	print key

	print "Retrieve user home fromString:",Keys.retrieveValue("HOME"), ";FromObject:",Keys.retrieveValue(key)

	print env.getVal(Keys.M2_REPOSITORY)

	env.prints()
