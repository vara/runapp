# -*- coding: utf-8 -*-

import os
from logger import RALogging
from Parser import ConfigParser

from configuration.Configuration import env,Config

LOG = RALogging.getLogger("BashParser")

def getIndex(text,pattern,fromIndex=0):

	#print "i:",fromIndex, " p:'",pattern,"' t:'",text,"'"

	if pattern:
		try:
			return text.index(pattern,fromIndex)
		except ValueError:
			pass

	return -1

def isString(text):

	if text:
		if text[0] == '"' and text[len(text)-1] == '"':
			return True

	return False

def normalize(text):

	if isString(text) == True:
		length = len(text)
		text = text[1:length-1]

	return text

def replace(text,pattern,new):
	newText = text.replace(pattern,new,1)

	LOG.debug(" ***Replace '%s' => '%s' : '%s'",pattern,new,newText)

	return newText


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

class ExportCommnad(Command):
	def __init__(self):
		Command.__init__(self,"export")

	def parse(self,value):
		value = replace(value,self.getName(),"")
		value=value.strip()
		env.export(value)
		LOG.debug("Exported vlaue '%s'",value)
		return value


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
			LOG.debug(" ***Resloved lvalue. '%s'<=>'%s'",values[0],value)
			if not value:
				value = normalize(values[1])
		return value


class BashParserImpl(ConfigParser):

	__marker = '$'
	__openBrace = '{'
	__closeBrace = '}'

	__openParam = __marker + __openBrace

	__rCommands = ( AltCommand(),)
	__lCommands = ( ExportCommnad(),)

	def parseLine(self,line):

		LOG.debug("Bash parser try parse line: '%s'",line)

		key = None
		val = None
		try:
			index = line.index('=')

			key = line[:index]
			val = line[index+1:]

		except ValueError:
			key = line
			val = None

		val = normalize(val)

		if val:
			val = self.__parseRValue(val)

		if key:
			key = self.__parseLValue(key)

		LOG.debug(" *Set paire Key:Value to ['%s':'%s']",key,val)
		
		return [key,val]

	def __parseLValue(self,lValue):
		#tmpValue = None

		lValue = self.__parseRValue(lValue)

		for actionCommand in self.__lCommands:
			if actionCommand.check(lValue) == True:
				LOG.debug(" **Found command for '%s'.",actionCommand.getName())
				lValue = actionCommand.parse(lValue)
		return  lValue

	def __parseRValue(self,value):

		textLength = len(value)
		index = getIndex(value,self.__marker,0)

		clonedValue = value

		while index != -1 and index+1 < textLength :

			# For ${....}
			if value[index+1] == self.__openBrace :
				closeIndex = getIndex(value,self.__closeBrace,index+2)
				if closeIndex == -1:
					#TODO:throw exception : syntax error - close brace not found
					LOG.warn("Close brace not found !!!")
					return value
				else:
					parameter = value[index+2 : closeIndex]

					LOG.debug(" **Detected parameter on %s => %s ",(index,closeIndex),parameter)
					tmpValue = None
					wasDone = False
					#Search for special command parameter
					for actionCommand in self.__rCommands:

						if actionCommand.check(parameter) == True:
							wasDone = True
							LOG.debug(" **Found command '%s' in parameter.",actionCommand.getName())
							tmpValue = actionCommand.parse(parameter)
							break
					
					if wasDone == False:
						tmpValue = env.getVal(parameter,"")

					if not tmpValue:	tmpValue = ''
					LOG.debug(" **Resolved value : '%s'",tmpValue)
					clonedValue = replace(clonedValue,value[index : closeIndex+1],tmpValue)
					index = closeIndex # !!!

			# For $VARIABLE
			else:
				index+=1

				closeIndex = getIndex(value,' ',index)
				if closeIndex != -1:
					allegedVarLength = closeIndex - index
				else:
					allegedVarLength = textLength-index
					closeIndex = index+allegedVarLength

				variable = value[index:closeIndex]

				LOG.debug(" **i:%d ci:%d len:%d value:'%s'",index,closeIndex,allegedVarLength,variable)

				tmpValue = env.getVal(variable,"")

				LOG.debug(" **Resolved value : '%s'",tmpValue)

				clonedValue = replace(clonedValue,value[index-1 : closeIndex],tmpValue)

			index = getIndex(value,self.__marker,index)

		return clonedValue



	def __findParameter(self,value,fromIndex=0):

		oIndex = getIndex(value,self.__openParam,fromIndex)
		if oIndex != -1:
			cIndex = getIndex(value,self.__closeBrace,oIndex+2)
			if cIndex == -1:
				#TODO:throw exception : syntax error - close brace not found
				return None
			return oIndex,cIndex
		return None




