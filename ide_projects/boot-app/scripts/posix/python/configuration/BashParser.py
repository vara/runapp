# -*- coding: utf-8 -*-

import os
from logger import RunAppLogger
from Parser import ConfigParser

from configuration.Configuration import env,Config


LOG = RunAppLogger.getLogger("BashParser")


def getIndex(text,pattern,fromIndex=0):

	#print "i:",fromIndex, " p:'",pattern,"' t:'",text,"'"

	if pattern:

		try:
			return text.index(pattern,fromIndex)
		except ValueError:
			pass

	return -1


class Command(object):
	__commandName = None

	#__cachedIndex = None

	def __init__(self,commandName):
		self.__commandName = commandName

	def getName(self):
		return self.__commandName

	def parse(self,value):
		return value

	def check(self,value):
		index = getIndex(value,self.getName())
		if index != -1:
			#self.__cachedIndex = index
			return True

		return False


class AltCommand(Command):

	""" The format of value to parse is  ${parameter:−word}
		If parameter has not been resolved , the expansion of word is substituted. 
		Otherwise, the value of parameter is substituted.
	"""

	def __init__(self):
		Command.__init__(self,":-")

	def parse(self,value):

		values = value.split(self.getName())

		if len(values) != 2:
			#TODO: throw exception , values must contains with only two values
			LOG.error("Syntax error: parameter must have two values seperated by ':-' ")
			pass
		else:
			value = env.getVal(values[0])
			LOG.debug(" *Try reslove lvalue. %s<=>%s",values[0],value)
			if not value:
				value = values[1]
		return value


class BashParser(ConfigParser):

	__marker = "$"
	__openBrace = "{"
	__closeBrace = "}"

	__openParam = __marker + __openBrace

	__commands = ( AltCommand(), )

	def parseLine(self,line):

		LOG.debug("Bash parser try parse line: '%s'",line)

		key = None
		val = None
		try:
			index = line.index('=')

			key = line[:index]
			val = line[index+1:]

		except ValueError:
			key = "not-assigned"
			val = line

		LOG.debug(" *Set paire Key:Value to ['%s':'%s']",key,val)

		val = self.__parseValue(val)
		return [key,val]

	def __parseValue(self,value):

		indexes = self.__findParameter(value)
		if indexes:
			parameter = value[indexes[0]+2 : indexes[1]]
			LOG.debug(" *Detected parameter on %s => %s ",indexes,parameter)

			#Search for special command parameter
			for actionCommand in self.__commands:

				if actionCommand.check(parameter) == True:

					LOG.debug(" *Found command '%s' in parameter.",actionCommand.getName())

					value = actionCommand.parse(parameter)

					LOG.debug(" *Returned value: '%s'",value)

		return value

	def __findParameter(self,value,fromIndex=0):

		oIndex = getIndex(value,self.__openParam)
		if oIndex != -1:
			cIndex = getIndex(value,self.__closeBrace,oIndex+2)
			if cIndex == -1:
				#TODO:throw exception : syntax error - close brace not found
				return None
			return oIndex,cIndex
		return None



