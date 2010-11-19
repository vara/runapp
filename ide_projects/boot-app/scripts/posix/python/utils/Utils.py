# -*- coding: utf-8 -*-

#
# Author: Grzegorz (vara) Warywoda
# Since: 2010-11-03 14:25:36 CET
#

import os, sys, datetime, commands, traceback, string

def getAbsDirName(path,topLevels=0):

	"""
		Get absolute path to directory for argumnet 'path'.
		Second argument determine how many top-level directories should be ommited.
		
		e.q.
		 	f = /dir3/dir2/dir1/dir0
			getAbsDirName(f)	=> /dir3/dir2/dir1/dir0
			getAbsDirName(f,2)	=> /dir3/dir2
	"""

	if os.path.islink(path):
		path = os.path.realpath(path)
	path = os.path.abspath(path)

	if os.path.isfile(path):
		path = os.path.dirname(path)

	if topLevels > 0:
		for i in range(0,topLevels):
			path = os.path.dirname(path)
	return path

def printStackTrace():
	traceback.print_stack()

def getClass( clazz ):
	""" Load/retrieve class dynamically """

	parts = clazz.split('.')
	module = ".".join(parts[:-1])
	m = __import__( module )
	for comp in parts[1:]:
		m = getattr(m, comp)
	return m

"""Workaround for resolving modules properly"""
if __name__ == "__main__":
	sys.path.append( getAbsDirName(__file__,1))

from logger import RALogging
LOG = RALogging.getLogger("utils")


def resolveJavaPath() :

	#@Author Grzegorz (vara) Warywoda 2010-11-13 08:16:01 CET
	# Fix: local variable '_javaBin' referenced before assignment when env wll not be set
	_javaBin = None

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

				if LOG.isDebug():
					LOG.debug("Try to resolve java path from windows registry")

				aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
				aKey1 = OpenKey(aReg, r"SOFTWARE\JavaSoft\Java Runtime Environment")
				JRTVersion = QueryValueEx(aKey1,"CurrentVersion")
				if JRTVersion:

					if LOG.isDebug(1):
						LOG.ndebug(1,"JRE ver. %s",JRTVersion[0])

					aKey2 = OpenKey(aKey1, JRTVersion[0])
					regVal = QueryValueEx(aKey2,"JavaHome")
					CloseKey(aKey2)
					if regVal :
						_javaBin = regVal[0]

				if LOG.isDebug():
					LOG.debug("Resolved java path is %s",_javaBin)

				CloseKey(aKey1)
				CloseKey(aReg)

			except ImportError:
				LOG.warn("Module _winreg not found, module needed for resolving Java installation path!")

	if _javaBin:
		suffix = os.sep+"bin"+os.sep+"java"
		if not _javaBin.endswith(suffix):
			_javaBin += suffix
		_javaBin = FSUtil.resolveSymlink(_javaBin)

	return _javaBin

def resolveMavenPath():
	_mvn = MvnUtil.findPath()
	return _mvn


def toString(data,separator=' '):
	retVal=""
	for s in data:
		retVal+=s
		retVal+=separator
	return retVal

class FSUtil(object):
	"""Utilitie class used to operations on file sytem"""

	@staticmethod
	def resolveSymlink(path):
		if os.path.islink (path):
			path = os.path.realpath(path)
		return os.path.abspath(path)

	@staticmethod
	def check_path(path):
		path = os.path.expanduser(path)
		return FSUtil.resolveSymlink(path)

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

		if LOG.isTrace():
			LOG.trace("Current time : %s Stop time: %s" ,currentTimeMS,stopTimeMilli)

		if stopTimeMilli:
			currentTimeMS = currentTimeMS - stopTimeMilli
		return currentTimeMS

	@staticmethod
	def stamp(milli,msg=""):
		print Timer.toString(milli,msg)

	@staticmethod
	def toString(milli,msg=""):
		elapsed = Timer.time(milli)
		sTime = Timer.__format(elapsed)
		return msg + " et: " + sTime

	@staticmethod
	def __format(milliseconds):
		sb = ''
		if milliseconds > 1000:

			sec = int(milliseconds/1000)
			milliseconds = milliseconds % 1000

			if sec > 60:
				min = int(sec /60)
				sec%=60
				if min > 60:
					hour = int(min /60)
					min%=60
					sb+= str(hour) + "h "

				sb+=str(min) + "m "
			sb+= str(sec) + "s "

		sb += str(milliseconds) +"ms"
		return sb

from xml.dom import minidom

class MvnUtil:
	POM_NS = "{http://maven.apache.org/POM/4.0.0}"

	@staticmethod
	def findPath():
		_mvn = os.getenv("M2_HOME")
		if _mvn != None:
			suffix = os.sep+"bin"+os.sep+"mvn"
			_mvn += suffix
		return _mvn

	@staticmethod
	def parse(pathToPom,searchInParent=False):
		"""
		Parses the POM to get a list of file path pairs returned by buildPath()
		"""
		from maven import POMUtil

		pom = POMUtil.Pom(os.path.expanduser("~/.m2/repository"))

		pom.setSearchInParent(searchInParent)

		list = pom.resolveDependency(os.path.expanduser(pathToPom))
		if list:
			list =MvnUtil.__removeDuplicatedPaths(list)
		else: list = []

		return list

	@staticmethod
	def __removeDuplicatedPaths(arrayList):
		return dict.fromkeys(arrayList).keys()
		#return list(set(arrayList))

""" test """

if __name__ == "__main__":
	start = Timer.time()

	RALogging.initialize()

	print "Linux :", bool(OSUtil.isLinux()),\
		"\nWindows :", bool(OSUtil.isWin()) ,\
		"\nMacOS :", bool(OSUtil.isMac())

	print "Resolve sym link method ", FSUtil.resolveSymlink(".")
	print "JavaPath : %s" % resolveJavaPath()
	
	dependencyList = MvnUtil.parse("~/varaprj/jklipper/ide_projects/jklipper.utils")
	print "Number of found dependecies ",len(dependencyList)
	for p in dependencyList:
		print p[0]

	Timer.stamp(start,"Time of working application")


