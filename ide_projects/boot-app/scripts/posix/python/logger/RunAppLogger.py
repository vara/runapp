# -*- coding: utf-8 -*-

import logging,formatter
import os
from Handlers import ConsoleHandler
from Formatters import ColorFormatter

TRACE = 5
DEBUG5 = 6
DEBUG4 = 7
DEBUG3 = 8
DEBUG2 = 9

class RALogger(logging.Logger):
        
    def __init__(self,name):
        logging.Logger.__init__(self,name,0)
        
    @staticmethod
    def initialize():
        
        hdlr = ConsoleHandler()
        fmt = ColorFormatter()        
        hdlr.setFormatter(fmt)
        logging.getLogger().addHandler(hdlr)
                
        for i in range(1,4):
            logging.addLevelName(logging.DEBUG-i,"DEBUG"+str(i+1))
            
        logging.addLevelName(TRACE,"TRACE")        
        logging.getLogger().setLevel(logging.INFO)
        
        debugLev = os.getenv("DEBUG")

        if debugLev:
            logging.getLogger().setLevel(int(debugLev))         

    def setDebugLevel(self,intVal):
        try:
            initVal = min((9,intVal)) + logging.DEBUG	    
            self.setLevel(intVal)
        except:
            logging.warn("You try set wrong level ! [%s]",intVal)

    def isDebugEnable(self):
        return self.isEnabledFor(logging.DEBUG)

    def isDebugEnable(self,intVal):
        try:
            intVal=int(intVal)+logging.DEBUG
        except:
            intVal = logging.DEBUG

        return self.isEnabledFor(intVal)

    def isWarn(self):
        if self.disabled >=  logging.WARN:
            return 0
        return logging.WARN >= self.getEffectiveLevel()

    def isTrace(self):
        if self.disabled >= TRACE:
            return 0
        return TRACE >= self.getEffectiveLevel()
        
    @staticmethod
    def isTraceEnable():
        return logging.getLogger().isEnabledFor(logging.WARN)
    
    @staticmethod
    def isWarnEnable():
        return logging.getLogger().isEnabledFor(logging.WARN)

if __name__ == "__main__":

    RALogger.initialize()
    log = logging.getLogger("logger")
    
    print "Level is ", log.level
    if log.isEnabledFor(logging.DEBUG):
        log.debug("Debug message")