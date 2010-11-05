# -*- coding: utf-8 -*-

#
## Author: Grzegorz (vara) Warywoda 
## Since: 2010-11-03 14:20:47 CET
#

import os
import sys
import commands
import time
import logging

from utils.Utils import OSUtil, FSUtil, Timer
from logger.RunAppLogger import RALogger

RALogger.initialize()

LOG = logging.getLogger("runapp")

# Definition of global variables
#
# SCRIPT_HOME   -- Path to directory where is this script placed
# JAVA_BIN      -- path to java executable file
# WAIT_ON_EXIT  -- wait, before exit script
# TESTING_MODE  -- dont call main program
# PROVIDER      -- java|maven (Default:java)
# DEBUG         -- number of debug level (default:None)
# EXEC_TOOL     -- Tool for execution JVM

# CONFIG_FP     -- Path to configuration file
# DEPENDENCY_FP -- Path to dependency file path
# JVM_ARGS_FP   -- Path to file with jvm argumnets

# MAINCLASS     -- Boot class
# PROJECT_DIR   -- Path to root directory calling project
# M2_REPOSITORY -- Path to maven repository
# USER_ARGS_TO_APP --All arguments passed by user
#
# COMMENTCHAR   -- Used in configuration files

COMMENTCHAR   = '#'
USER_DIR      = os.path.expanduser('~')
CWD           = os.getcwd()
WAIT_ON_EXIT  = 1
PROVIDER      = "java" #HARD CODE FIXME: after implement maven boot util
SCRIPT_HOME   = os.path.dirname(FSUtil.resolveSymlink(sys.argv[0]))

CONFIG_FP     = os.getenv("CONFIG_FP","runapp.conf")
DEPENDENCY_FP = os.getenv("DEPENDENCY_FP","runapp.dep")
JVM_ARGS_FP   = os.getenv("JVM_ARGS_FP","runapp.jvmargs")

def exitScript():
    
    LOG.debug("Wait on exit %d" , WAIT_ON_EXIT)
    time.sleep(WAIT_ON_EXIT)    
    exit()

def resolveJavaPath() :
    _javaBin = os.getenv("JAVA_HOME")
    if _javaBin ==  None: 
        _javaBin = os.getenv("JRE_HOME")
        if _javaBin ==  None: 
            _javaBin = os.getenv("JDK_HOME")
            if _javaBin ==  None: 
                
                if OSUtil.isLinux() or OSUtil.isMac():
                    _javaBin = commands.getoutput('which java')
                    
                elif OSUtil.isWin():
                    try:
                        from _winreg import ConnectRegistry,OpenKey,QueryValueEx,CloseKey
                        
                        aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
                        aKey1 = OpenKey(aReg, r"SOFTWARE\JavaSoft\Java Runtime Environment")
                        JRTVersion = QueryValueEx(aKey,"CurrentVersion")                    
                        aKey2 = OpenKey(aKey1, JRTVersion)
                        _javaBin = QueryValueEx(aKey,"JavaHome") 
                    
                        CloseKey(aKey1) 
                        CloseKey(aKey2) 
                        CloseKey(aReg)                        
                        
                    except ImportError:
                        print "Module _winreg not found" 
    
    if _javaBin !=  None: 
        if not _javaBin.endswith("/bin/java"):
            _javaBin=_javaBin+"/bin/java"            
        _javaBin = FSUtil.resolveSymlink(_javaBin)
        
    return _javaBin

def readConfig():
    for prefix in ("",CWD+"/",USER_DIR+"/"):	
	
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
    file = open(SCRIPT_HOME+"/../usage.txt",'r')
    content = file.read()
    file.close()
    print "%s" % content


#######################################
#                                     #
# This is Entry point for this script #
#                                     #
#######################################
START_TIME_MS = Timer.time()

JAVA_BIN = resolveJavaPath()
if not JAVA_BIN:
    LOG.error("Java not found, set JAVA_HOME in envirioment variables")
    exitScript()   
    
LOG.info("Script Home: %s ",SCRIPT_HOME)
LOG.info( "Path to java : %s", JAVA_BIN)

readConfig()

LOG.info("Elapsed time of boot application %dms",Timer.time(START_TIME_MS))

exitScript()


