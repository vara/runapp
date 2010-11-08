# -*- coding: utf-8 -*-

import os
import re
import logging

from  configuration.Configuration import env,Config

LOG = logging.getLogger("config-parser")

class ConfigParser:
	__cachedResults =None

	__autoUpdateEnvironment = True

	def open(self,pathToFile):
		file = open(pathToFile,'r')
		fLines = file.readlines()
		file.close()

		self.__cachedResults = {}

		cch = Config.getCommentChar()
		commentsPattern = re.compile(cch+'.*$')

		for line in fLines:
			line = line.strip()
			if not len(line) == 0:
				line = commentsPattern.sub("",line,0)
				if not len(line) == 0:

					parsedLine = self.parseLine(line)

					if parsedLine :
						if self.__cachedResults.has_key(parsedLine[0]):

							values = self.__cachedResults.get(parsedLine[0])

							if isinstance(values,basestring):
								values = [values]

							values.append(parsedLine[1])
							parsedLine[1] = values

						self.__cachedResults.update([parsedLine])
						
						if self.__autoUpdateEnvironment == True:
							env.getDic().update([parsedLine])

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


class ParserManger:
	__parsers = dict()

	@staticmethod
	def getParserByName(name):
		if ParserManger.__parsers.has_key(name):
			return ParserManger.__parsers[name]
		return None

	@staticmethod
	def registerParser(name,parser):

		if not isinstance(parser,ConfigParser):
			#TODO: Throw exception
			pass
		else:
			ParserManger.__parsers.update([[name,parser]])






