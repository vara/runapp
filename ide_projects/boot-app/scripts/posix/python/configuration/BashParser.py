# -*- coding: utf-8 -*-

import os,string
from logger import RALogging
from Parser import ConfigParser
from configuration.Configuration import Config,env

LOG = RALogging.getLogger("parser-bash")


def _strip_spaces(alist):
	return map(lambda x: string.strip(x), alist)

def _get_index(text,pattern,fromIndex=0):
	#print "i:",fromIndex, " p:'",pattern,"' t:'",text,"'"
	try:
		return text.index(pattern,fromIndex)

	except ValueError:
		pass
	return -1

def _get_index_for_first(text,patterns,fromIndex=0,defaultVal=-1):
	#print "i:",fromIndex, " p:'",pattern,"' t:'",text,"'"
	index = fromIndex
	for char in text[fromIndex:]:
		for pattern in patterns:
			if pattern == char:
				return index
		index+=1
	return defaultVal

def _is_string(text):

	if text:
		if text[0] == '"' :
			if text[len(text)-1] != '"':
				raise Exception("End quot mark not found")
			return True
		else:
			if text[len(text)-1] == '"':
				raise Exception("Start quot mark not found")
	return False

def _normalize(text):

	if text:
		text = text.strip()

	if _is_string(text) == True:
		length = len(text)
		text = text[1:length-1]

	return text

def _replace(text,pattern,new):
	newText = text.replace(pattern,new,1)

	if LOG.isDebug(3):
		LOG.ndebug(3," ***Replace '%s' => '%s' , result: '%s'",pattern,new,newText)

	return newText


class Command(object):
	__commandValue = None

	#__cachedIndex = None

	def __init__(self,commandValue):
		self.__commandValue = commandValue

	def getCommandValue(self):
		return self.__commandValue

	def parse(self,value):
		return value

	def check(self,value):
		index = _get_index(value,self.__commandValue)
		if index != -1:
			#self.__cachedIndex = index
			return True

		return False

	def __str__(self):
		return str(self.__class__.__name__)

class ExportCommnad(Command):
	def __init__(self):
		Command.__init__(self,"export")

	def parse(self,value):
		value = _replace(value,self.getCommandValue(),"")
		value=value.strip()
		env.export(value)

		if LOG.isDebug(2):
			LOG.ndebug(2," ***Exported vlaue '%s'",value)

		return value


class AltCommand(Command):

	""" The format of value to parse is  ${parameter:−word}
		If parameter has not been resolved , the expansion of word is substituted.
		Otherwise, the value of parameter is substituted.
	"""

	def __init__(self):
		Command.__init__(self,":-")

	def parse(self,value):

		values = value.split(self.getCommandValue())

		if len(values) != 2:
			#TODO: throw exception , values must contains with only two values
			LOG.error("Syntax error: parameter must have two values seperated by ':-' ")
			pass
		else:
			value = ConfigParser.findVariable(values[0])

			if LOG.isDebug(2):
				LOG.ndebug(2," ***Resloved value. '%s'<=>'%s'",values[0],value)

			if not value:
				value = _normalize(values[1])
		return value


class BashParserImpl(ConfigParser):

	__marker = '$'
	__openBrace = '{'
	__closeBrace = '}'

	__openParam = __marker + __openBrace

	__Commands = ( AltCommand(),ExportCommnad())

	def parseLine(self,textLine,info):

		if LOG.isDebug(1):
			LOG.ndebug(1,"Bash parser try parse line: '%s'",textLine)

		key = None
		val = None
		try:
			index = textLine.index('=')

			key = textLine[:index]
			val = textLine[index+1:]

		except ValueError:
			key = textLine
			val = None

		val = _normalize(val)

		if val:
			val = self.__parseRValue(val)

		if key:
			key = self.__parseLValue(key)

		if LOG.isDebug(1):
			LOG.ndebug(1," Result ['%s':'%s']",key,val)
		
		return [key,val]

	def __parseLValue(self,lValue):

		lValue = self.__parseRValue(lValue)

		actionCommand = self.getCommandForParameter(lValue)
		if actionCommand:
			if LOG.isDebug(2):
				LOG.ndebug(2," **Detected '%s' command",actionCommand)

			lValue = actionCommand.parse(lValue)

		return  lValue

	def __parseRValue(self, value):

		textLength = len(value)
		index = _get_index(value,self.__marker,0)

		while index != -1 and index+1 < textLength :

			if LOG.isDebug(4):
				LOG.ndebug(4," **index:%d length:%d value:'%s'",index,textLength,value)

			# For ${....}
			if value[index+1] == self.__openBrace :

				closeIndex = _get_index(value,self.__closeBrace,index+2)
				if closeIndex == -1:
					raise Exception("Broken line. Close brace not found => '{0}'".format(value[index:]) )
				else:
					parameter = value[index+2 : closeIndex]

					if LOG.isDebug(2):
						LOG.ndebug(2," **Detected parameter on %s => '%s' ",(index,closeIndex),parameter)

					tmpValue = None
					#Search for special command parameter
					actionCommand = self.getCommandForParameter(parameter)
					if actionCommand:
						if LOG.isDebug(2):
							LOG.ndebug(2," **Detected '%s' command",actionCommand)
						tmpValue = actionCommand.parse(parameter)
					else:
						tmpValue = self.findVariable(parameter,"")

					if LOG.isDebug(2):
						LOG.ndebug(2," **Resolved value : '%s'",tmpValue)

					value = _replace(value,value[index : closeIndex+1],tmpValue)
					index += len(tmpValue)

			# For $VARIABLE
			else:

				closeIndex = _get_index_for_first(value,(self.__marker,' '),index+1, textLength)

				parameter = value[index+1:closeIndex]

				if LOG.isDebug(2):
						LOG.ndebug(2," **Detected parameter on %s => '%s' ",(index,closeIndex),parameter)

				tmpValue = self.findVariable(parameter,"")

				if LOG.isDebug(2):
					LOG.ndebug(2," **Resolved value : '%s'",tmpValue)

				value = _replace(value,value[index : closeIndex],tmpValue)
				index += len(tmpValue)

			index = _get_index(value,self.__marker,index)
			textLength = len(value)

		return value

	def getCommandForParameter(self,parameter):
		if parameter:
			for actionCommand in self.__Commands:
				if actionCommand.check(parameter) == True:
					return actionCommand
		return None

class FilePathResolverParser(BashParserImpl):

	def postProcess(self,results,info):

		if LOG.isTrace():
			LOG.trace("[%s:%d] %s",info.getFileName(),info.getLineNumber(),results)

		if self.checkPath(results[0]) == False:
			if LOG.isWarn():
				LOG.warn("!!! NOT EXISTS [%s:%d] '%s'",info.getFileName(),info.getLineNumber(),results[0])
			results =  None

		return results

	def checkPath(self,path):
		if not os.path.exists(path):
			return False
		return True





