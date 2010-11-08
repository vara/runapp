# -*- coding: utf-8 -*-

import os
import re
import logging

from configuration.Configuration import env,Config
from utils import Utils 

LOG = logging.getLogger("config-parser")

class ConfigParser:
	__cachedResults =None

	__autoUpdateEnvironment = True

	__allowToMultipleValues = False

	def open(self,pathToFile):

		LOG.debug("Prepare to read comfig file %s",pathToFile)

		file = open(pathToFile,'r')
		fLines = file.readlines()
		file.close()

		if not self.__cachedResults:
			self.__cachedResults = {}
		else:
			self.__cachedResults.clear()

		cch = Config.getCommentChar()
		commentsPattern = re.compile(cch+'.*$')

		for line in fLines:
			line = line.strip()
			if not len(line) == 0:
				line = commentsPattern.sub("",line,0)
				if not len(line) == 0:

					parsedLine = self.parseLine(line)

					if parsedLine :
						if self.__cachedResults.has_key(parsedLine[0]) and self.isAllowToMultipleValues() :

							values = self.__cachedResults.get(parsedLine[0])

							if isinstance(values,basestring):
								values = [values]

							values.append(parsedLine[1])
							parsedLine[1] = values

						self.__cachedResults.update([parsedLine])
						
						if self.__autoUpdateEnvironment == True:
							env.put(parsedLine)

	def parseLine(self,line):
		return line

	def results(self):
		retVal = (self.__cachedResults.items())
		self.__cachedResults.clear()
		return retVal

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

class ParserManger:
	__parsers = dict()

	@staticmethod
	def getParserByName(name):
		parser = None
		if ParserManger.__parsers.has_key(name):
			moduleName = ParserManger.__parsers[name]

			mod = Utils.getClass(moduleName)()

			if isinstance(mod,ConfigParser):
				parser = mod
			else:
				LOG.debug("Not recognized parser class '%s'. Object must inherited from %s",moduleName,ConfigParser)

		return parser

	@staticmethod
	def registerParser(name,parserClassName):

		if not isinstance(parserClassName,basestring):
			raise TypeError("Second parameter must by a string type !")

		ParserManger.__parsers.update([[name,parserClassName]])


ParserManger.registerParser("bash-parser", "configuration.BashParser.BashParserImpl")




