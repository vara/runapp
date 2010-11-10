# -*- coding: utf-8 -*-

import os
import sys
import logging
import logging.config

TRACE = 5
DEBUG5 = 6
DEBUG4 = 7
DEBUG3 = 8
DEBUG2 = 9
DEBUG = logging.DEBUG

def getLogger(name=None):
	return logging.getLogger(name)

def initialize():

	import configuration.Configuration
	from configuration.Configuration import Keys,Config

	for i in range(1,5) :
		logging.addLevelName(logging.DEBUG-i,"DEBUG"+str(i))

	logging.addLevelName(TRACE,"TRACE")
	logging.getLogger().setLevel(logging.INFO)
	logging.setLoggerClass(RALogger)
	absPath = os.path.join(Config.getScriptRootPath(),Keys.LOG_CONF_FP.fromEnv())

	if os.path.exists(absPath):
		logging.config.fileConfig(absPath)
	else:
		logging.basicConfig(level=logging.INFO)
		getLogger().warn("Path \n\t => '%s'\n not found !"
					"... Logger has been configured basing on defult implementation.",absPath)

	#User can quickly override level from console
	debugLev = os.getenv("DEBUG")
	if debugLev:
		getLogger().setLevel(int(debugLev))

class RALogger(logging.Logger):

	def __init__(self,name):
		logging.Logger.__init__(self,name,0)

	def setDebugLevel(self,intVal):
		try:
			initVal = min((9,intVal)) + logging.DEBUG
			self.setLevel(intVal)
		except:
			logging.warn("You try set wrong level ! [%s]",intVal)

	def debug(self,msg, *args, **kwargs):
		#print "  !!! :",args
		logging.Logger.debug(self,msg, *args,**kwargs)

	def ndebug(self,level,msg, *args, **kwargs):

		level = RALogger.__fixLevel(logging.DEBUG,level)
		if self.isEnabledFor(level):
			self._log(level, msg, args, **kwargs)

	def trace(self,msg, *args, **kwargs):

		if self.isEnabledFor(TRACE):
			self._log(TRACE, msg, args, **kwargs)

	def isDebug(self,val=0):
		level = RALogger.__fixLevel(logging.DEBUG,val)
		return self.isEnabledFor(level)

	def isWarn(self):
		if self.disabled >=  logging.WARN:
			return 0
		return logging.WARN >= self.getEffectiveLevel()

	def isTrace(self):
		if self.disabled >= TRACE:
			return 0
		return TRACE >= self.getEffectiveLevel()

	@staticmethod
	def setRootLogLevel(level=logging.INFO):
		try :
			level = int(level)
			if level < 0 :
				level = 0
			logging.getLogger().setLevel(level)
			logging.getLogger().info("Set level to %d on ROOT logger.",level)
		except ValueError, e:
			logging.getLogger().warn("Wrong value for logger level !\n => %s ",e)

	@staticmethod
	def __fixLevel(origLevel,diff=0):
		level = origLevel
		if origLevel == logging.DEBUG:
			level = logging.DEBUG - min((4,diff))
		return level

if __name__ == "__main__":

	RALogger.initialize()
	log = getLogger("logger")

	print "Level is ", log.level
	if log.isEnabledFor(logging.DEBUG):
		log.debug("Debug message")
