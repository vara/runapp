# -*- coding: utf-8 -*-

#
## Author: Grzegorz (vara) Warywoda 
## Since: 2010-11-03 14:25:36 CET
#

import os
import sys
import datetime

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
    
    def __getattr__(self, attr):	
	return getattr(self.__instance, attr)	
    
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
    
""" test """    
    
if __name__ == "__main__":
    start = Timer.time()
    
    print "Linux :", bool(OSUtil.isLinux()),\
          "\nWindows :", bool(OSUtil.isWin()) ,\
          "\nMacOS :", bool(OSUtil.isMac())
    
    print "Resolve sym link method ", FSUtil.resolveSymlink(".")

    Timer.stamp(start,"Elapsed time of boot application")
    
    

	