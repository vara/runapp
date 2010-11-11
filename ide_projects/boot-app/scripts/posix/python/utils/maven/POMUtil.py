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


class pom:

	__env = {}

	def resolveDependency(self,pom):
		pathToPomFile = None

		pom = os.path.abspath(pom)
		if os.path.isdir(pom):
			pathToPomFile = os.path.join(pom,"pom.xml")
		else:
			pathToPomFile = pom

		print "Parse : ",pathToPomFile

		DOMTree = xml.dom.minidom.parse(pathToPomFile)

		return self.__parse( DOMTree.childNodes[0],
						os.path.dirname(pathToPomFile) )

	def __parse(self,rootElement,pomDir):
		jarPaths = []

		self.__updateProperties(rootElement)

		modules = rootElement.getElementsByTagName(Entries.MODULES)
		if modules:
			if modules[0].hasChildNodes():
				for child in modules[0].childNodes:
					if child.nodeType == xml.dom.Node.ELEMENT_NODE:
						moduleName = child.childNodes[0].nodeValue

						modulePath = os.path.join(pomDir,moduleName)
						try:

							tmpPaths = self.resolveDependency(modulePath)
							jarPaths.extend(tmpPaths)

						except Exception, e:
							print "Exception : ",e

		jarPaths.extend(self.__resolveDependency(rootElement))

		return jarPaths

	def __getModules(self,rootElement):
		listOfModules = []
		modules = rootElement.getElementsByTagName(Entries.MODULES)
		if modules:
			modules = modules[0]
			if modules.hasChildNodes():
				for child in modules.childNodes:
					if child.nodeType == xml.dom.Node.ELEMENT_NODE:
						moduleName = child.childNodes[0].nodeValue
						listOfModules.append(moduleName)

		return listOfModules

	def __updateProperties(self,rootElement):
		props = rootElement.getElementsByTagName(Entries.PROPERTIES)
		if props:
			props = props[0]
			if props.hasChildNodes():
				for child in props.childNodes:
					if child.nodeType == xml.dom.Node.ELEMENT_NODE:
						key = child.nodeName
						value = child.childNodes[0].nodeValue

						self.putEnv(key,value)

	def __resolveDependency(self,xmlElement):

		jarPaths = []
		elemDependencies = xmlElement.getElementsByTagName(Entries.DEPENDENCIES)

		if elemDependencies:
			elemDependencies=elemDependencies[0]
			tags = (Entries.GROUP_ID,Entries.ARTIFACT_ID,Entries.VERSION)

			if elemDependencies.hasChildNodes():

				for elemDependency in elemDependencies.childNodes:

					if elemDependency.nodeType == xml.dom.Node.ELEMENT_NODE \
							and elemDependency.localName == Entries.DEPENDENCY:

						jarPaths.append(self.__createPath(self.__resolveElementsOfPath(elemDependency,tags)))

		return jarPaths

	def __resolveElementsOfPath(self,node,tags):
		mvnElementsData = {}

		for tag in tags:
			element = node.getElementsByTagName(tag)
			if element:
				mvnElementsData[tag] = element[0].childNodes[0].nodeValue

		return mvnElementsData

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

