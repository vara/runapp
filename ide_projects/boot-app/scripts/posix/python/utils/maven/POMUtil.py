# -*- coding: utf-8 -*-

# User: Grzegorz (vara) Warywoda
# Date: 2010-11-11
# Time: 00:34:14

"""
	Maven pom utilities
"""

import os, string, xml
import POMUtil

def findIndex(text,pattern,fromIndex=0):
	#print "i:",fromIndex, " p:'",pattern,"' t:'",text,"'"
	try:
		return text.index(pattern,fromIndex)

	except ValueError:
		pass
	return -1


class Entries:

	ARTIFACT_ID = "artifactId"
	VERSION = "version"
	GROUP_ID = "groupId"
	DEPENDENCIES = "dependencies"
	DEPENDENCY = "dependency"
	PARENT = "parent"
	RELATIVE_PATH = "relativePath"
	MODULES = "modules"
	MODULE = "module"

	PROPERTIES = "properties"
	SCOPE = "scope"

def resolveFilePath(path):
	if path:
		path = os.path.expanduser(path)
		
		path = os.path.abspath(path)
	return path

class Pom:

	__env = {}
	repositoryPath = ""

	__searchInParent = False

	def setSearchInParent(self,value):
		self.__searchInParent = bool(value)

	def isSearchInParent(self):
		return self.__searchInParent

	def __init__(self,repositoryPath=None):
		if repositoryPath:
			self.repositoryPath = repositoryPath

	def resolveDependency(self,pathToPom):

		pathToPom = resolveFilePath(pathToPom)

		if os.path.isdir(pathToPom):
			pathToPom = os.path.join(pathToPom,"pom.xml")

		print "Parse : ",pathToPom

		DOMTree = xml.dom.minidom.parse(pathToPom)

		for node in DOMTree.childNodes:

			if node.nodeType == xml.dom.Node.ELEMENT_NODE :
				results = self.__parse( node ,
									    os.path.dirname(pathToPom) )
				return results

		print "Elemnt node not found in '%s'" % pathPom

	def __parse(self,rootElement,pomDir):
		jarPaths = []

		self.__updateProperties(rootElement)

#		if self.isSearchInParent() == True:
#			Pom = self.__getParentPom(rootElement)

		modules = self.__getModules(rootElement)

		if len(modules) >0:
			for moduleName in modules:
				modulePath = os.path.join(pomDir,moduleName)
				try:

					tmpPaths = self.resolveDependency(modulePath)

					jarPaths.extend(tmpPaths)

				except Exception as inst:
					print "Exception : %s in %s" % (inst,pomDir)

		dependencies =self.__resolveDependency(rootElement)
		print "In ",pomDir," resolved ",len(dependencies)," dependencies"

		jarPaths.extend(dependencies)

		return jarPaths

	def __getParentPom(self,rootElement):
		props = rootElement.getElementsByTagName(Entries.PARENT)
		if props:
			values = self.__getNodeAsList(props[0])
			#for value in values:	self.putEnv(value[0],value[1])
			print values

	def __getModules(self,rootElement):
		listOfModules = []
		props = rootElement.getElementsByTagName(Entries.MODULES)
		if props:
			for node in self.__getNodeAsList(props[0]):
				listOfModules.append(node[1])
		return listOfModules

	def __updateProperties(self,rootElement):

		props = rootElement.getElementsByTagName(Entries.PROPERTIES)
		if props:
			values = self.__getNodeAsList(props[0])
			for value in values:	self.putEnv(value[0],value[1])
			#print values

	def __resolveDependency(self,rootElement):

		jarPaths = []
		elemDependencies = rootElement.getElementsByTagName(Entries.DEPENDENCIES)

		if elemDependencies:
			elemDependencies=elemDependencies[0]

			if elemDependencies.hasChildNodes():
				dependenciesMap = {}

				for elemDependency in elemDependencies.childNodes:

					if elemDependency.nodeType == xml.dom.Node.ELEMENT_NODE:

						nodeList = self.__getNodeAsList(elemDependency)
						
						for pair in nodeList:
							dependenciesMap.update([pair])

						jarPaths.append(self.__createPath(dependenciesMap,self.repositoryPath))
						dependenciesMap.clear()

		return jarPaths

	def __getNodeAsList(self,element):

		retValues = []

		#print element.toxml()

		if element.hasChildNodes():
			for child in element.childNodes:
				if child.nodeType == xml.dom.Node.ELEMENT_NODE:
					key = child.nodeName
					value = child.childNodes[0].nodeValue

					retValues.append( (key,value) )

		return retValues

	def __createPath(self,dependencyMap,prefixPath=""):

		groupId    = dependencyMap[Entries.GROUP_ID]
		artifactId = dependencyMap[Entries.ARTIFACT_ID]
		version    = dependencyMap[Entries.VERSION]

		groupId = string.replace(groupId, ".", os.sep)

		basePath = os.path.join(prefixPath,groupId,artifactId,version,
								   ''.join([artifactId , '-' , version]))

		basePath =  self.__fixPath( basePath )

		return ( basePath+".jar" , basePath+"-sources.jar" )


	def __fixPath(self,path):
		index = POMUtil.findIndex(path,"${")

		if index != -1:
			cIndex = POMUtil.findIndex(path,"}",index+2)

			if cIndex != -1:
				envKey = path[index+2:cIndex]
				envValue = self.findVariable(envKey)

				if envValue:
					path = string.replace(path,path[index : cIndex+1],envValue)
				else:
					print "Value has not been found in local env !!! : ",envKey

		return path

	def putEnv(self,key,value,canOverride=True):
		hasKey = self.__env.has_key(key)

		if hasKey:
			if canOverride:
				if self.__env.get(key) != value:
					self.__putEnv__(key,value)
		else:
			self.__putEnv__(key,value)


	def __putEnv__(self,key,value):
		#print "putEnv: ",key," : ",value
		self.__env.update([[key,value]])

	def findVariable(self,val,defVal=None):
		retVal = self.__env.get(val)
		if not retVal:
			retVal = defVal
		return retVal

