# -*- coding: utf-8 -*-

#
# Author: Grzegorz (vara) Warywoda
# Since: 2010-11-03 14:25:36 CET
#

import os
import sys
import datetime
import logging
import commands

LOG = logging.getLogger("utils.logger")

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

def resolveMavenPath():
	_mvn = os.getenv("M2_HOME")
	if _mvn != None:
		suffix = os.sep+"bin"+os.sep+"mvn"
		_mvn += suffix
	return _mvn


class FSUtil(object):
	"""Utilitie class used to operations on file sytem"""

	@staticmethod
	def resolveSymlink(path):
		return os.path.realpath(path)

class OSUtil(object):

	__instance = None

	class __impl:
		"""A OSUtil class implementation """
		_isLinux = False
		_isWin = False
		_isMac = False

		def __init__(self):
			#print "Created instance of OSUtils.__impl : ",id(self)
			if sys.platform.startswith("win"):
				self._isWin = True

			if sys.platform.startswith("darwin"):
				self._isMac = True

			if sys.platform.startswith("linux"):
				self._isLinux= True

		def isLinuxOS(self):
			return self._isLinux

		def isMacOS(self):
			return self._isMac

		def isWinOS(self):
			return self._isWin

	def __init__(self):
		if OSUtil.__instance is None:
			OSUtil.__instance = OSUtil.__impl()

		self.__dict__['_OSUtil__instance'] = OSUtil.__instance

	def __getattr__(self, attribute):
		return getattr(self.__instance, attribute)

	@staticmethod
	def isLinux():
		return OSUtil().isLinuxOS()

	@staticmethod
	def isMac():
		return OSUtil().isMacOS()

	@staticmethod
	def isWin():
		return OSUtil().isWinOS()


class Timer(object):
	@staticmethod
	def time(stopTimeMilli=None):

		dTime = datetime.datetime.now()
		currentTimeMS = long(dTime.microsecond/1000 + (dTime.second + ( (dTime.minute + (dTime.hour*60))*60)) *1000 )

	#	print "Current time : " ,currentTime , "Stop time: ",stopTimeMilli

		if stopTimeMilli:
			currentTimeMS = currentTimeMS - stopTimeMilli
		return currentTimeMS

	@staticmethod
	def stamp(milli,msg=None):
		elapsed = Timer.time(milli)
		if msg:
			print msg
		print "et:%d" % elapsed


class BashUtil(object):

	_varPrefixChar = "$"

	@staticmethod
	def findVariables(path):
		pass


""" test """

if __name__ == "__main__":
	start = Timer.time()

	print "Linux :", bool(OSUtil.isLinux()),\
		"\nWindows :", bool(OSUtil.isWin()) ,\
		"\nMacOS :", bool(OSUtil.isMac())

	print "Resolve sym link method ", FSUtil.resolveSymlink(".")

	print "JavaPath : %s",resolveJavaPath()

	Timer.stamp(start,"Elapsed time of boot application")



