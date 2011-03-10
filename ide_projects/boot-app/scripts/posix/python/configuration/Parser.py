# -*- coding: utf-8 -*-

import os
import re

from configuration.Configuration import env
from utils import Utils
from logger import RALogging

LOG = RALogging.getLogger("parser-conf")

class ConfigParserInfo:

	_fileName = None
	_currentNumber = 0
	_totalLineNumbers = 0

	def __init__(self,fileName):
		self._fileName = fileName

	def getFileName(self):
		return self._fileName

	def getLineNumber(self):
		return self._currentNumber

	def getTotalLineNumbers(self):
		return self._totalLineNumbers

class ConfigParser:
	__cachedResults =None

	__autoUpdateEnvironment = True

	__allowToMultipleValues = False

	def open(self,pathToFile):

		if LOG.isDebug():
			LOG.debug("Prepare to read config file %s",pathToFile)

		if not os.path.exists(pathToFile) :
			LOG.warn("Config file '%s' not exist",pathToFile)
			return

		file = open(pathToFile,'r')
		fLines = file.readlines()
		file.close()

		if not self.__cachedResults:
			self.__cachedResults = {}
		else:
			self.__cachedResults.clear()

		info = ConfigParserInfo(pathToFile)

		commentsPattern = re.compile('#.*$')

		for textLine in fLines:

			info._currentNumber+=1

			textLine = textLine.strip()

			if not len(textLine) == 0:
				textLine = commentsPattern.sub("",textLine,0)
				if not len(textLine) == 0:
					try:
						parsedLine = self.parseLine(textLine,info)
						if parsedLine :
							parsedLine = self.postProcess(parsedLine,info)
							if parsedLine:

								if self.__cachedResults.has_key(parsedLine[0]) and self.isAllowToMultipleValues() :

									values = self.__cachedResults.get(parsedLine[0])

									if isinstance(values,basestring):
										values = [values]

									values.append(parsedLine[1])
									parsedLine[1] = values

								self.__cachedResults.update([parsedLine])

								if self.__autoUpdateEnvironment == True:
									env.putEnv(parsedLine)
							else:
								if LOG.isTrace():
									LOG.trace("[%s:%d] Parser return null value !",pathToFile,info.getLineNumber())
						else:
							LOG.warn("[%s:%d] Parser return null value !",pathToFile,info.getLineNumber())

					except Exception, e:
						LOG.warn("[%s:%d] %s",info.getFileName(),info.getLineNumber(),e)

	def parseLine(self,textLine,info):
		return textLine

	def postProcess(self,results,info):

		if LOG.isTrace():
			LOG.trace("[%s:%d] Results: %s",info.getFileName(),info.getLineNumber(),results)

		return results

	def results(self):
		retVal = None
		if self.__cachedResults:
			retVal = (self.__cachedResults.items())
			self.__cachedResults.clear()
		return retVal

	"""
	 Default value is set to True
	"""
	def setAutoUpdateEnv(self,value):

		if isinstance(value,bool):
			if self.__autoUpdateEnvironment != value:
				self.__autoUpdateEnvironment = value

	def isAutoUpdateEnv(self):
		return self.__autoUpdateEnvironment

	def setAllowToMultipleValues(self,value):

		if isinstance(value,bool):
			if self.__allowToMultipleValues != value:
				self.__allowToMultipleValues = value

	def isAllowToMultipleValues(self):
		return self.__allowToMultipleValues

	@staticmethod
	def findVariable(val,defVal=None):
		retVal = env.getEnv(val)
		if not retVal:
			retVal = defVal
		return retVal

class ParserManger:
	__parsers = dict()

	@staticmethod
	def getParserByName(name):
		parser = None
		if ParserManger.__parsers.has_key(name):
			moduleName = ParserManger.__parsers[name]

			#TODO: Maybe should cache the module object
			mod = Utils.getClass(moduleName)

			instance = mod()
			if isinstance(instance,ConfigParser):

				parser = instance
			else:
				LOG.warn("Not recognized parser class '%s'. Object must inherited from %s",moduleName,ConfigParser)

		return parser

	@staticmethod
	def registerParser(name,parserClassName):

		if not isinstance(parserClassName,basestring):
			raise TypeError("Second parameter must by a string type !")

		ParserManger.__parsers.update([[name,parserClassName]])


ParserManger.registerParser("bash-parser", "configuration.BashParser.BashParserImpl")
ParserManger.registerParser("bash-path-parser", "configuration.BashParser.FilePathResolverParser")




