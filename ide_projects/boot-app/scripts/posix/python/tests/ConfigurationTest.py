# -*- coding: utf-8 -*-

# User: Grzegorz (vara) Warywoda
# Date: 2010-11-11
# Time: 19:40:57

import sys, os

import UtilsForTests

import unittest
import logger.RALogging

from configuration.Configuration import env ,_Env,Keys,KeyEntry

class EmptyValueKeyEntry (KeyEntry):
	def __init__(self):
		KeyEntry.__init__(self,"EmptyKeyEntry")

class TestValueKeyEntry (KeyEntry):
	def __init__(self):
		KeyEntry.__init__(self,"TestKeyEntry","Value-ForTestKeyEntry")

class UnknownObject(object):
	pass

class EnvironmentTest(unittest.TestCase):

	def setUp(self):
		_Env._dict.clear()

	def testGetEnvMethod(self):
		expected = "test"

		#Only for test
		UtilsForTests.insertVar(Keys.MAIN_CLASS.getKey(),expected)

		#Get val from KeyEntry object
		val = env.getEnv(Keys.MAIN_CLASS)
		self.assertEquals(val,expected)

		#Get val from String object
		val = env.getEnv(Keys.MAIN_CLASS.getKey())
		self.assertEquals(val,expected)

		#Get val via KeyEntry object
		val = Keys.MAIN_CLASS.fromEnv()
		self.assertEquals(val,expected)

		#### test default parameter ####

		#For just return default value, when key is null
		expected = "test"
		val = env.getEnv(None,expected)
		self.assertEquals(val,expected)

		expected = None
		val = env.getEnv(None,expected)
		self.assertEquals(val,expected)

		#If key has not been found in local map,  return the default value where is passed as parameter
		expected = "test"
		val = env.getEnv(TestValueKeyEntry(),expected)
		self.assertEquals(val,expected)

		#If key has not been found in local map,  return the default value from TestValueKeyEntry
		expected = TestValueKeyEntry().getDefaultValue()
		val = env.getEnv( TestValueKeyEntry() )
		self.assertEquals(val,expected)

		expected = None
		val = env.getEnv(TestValueKeyEntry().getKey())
		self.assertEquals(val,expected)

		expected = None
		val = env.getEnv(UnknownObject())
		self.assertEquals(val,expected)

		expected = "test"
		val = env.getEnv(UnknownObject(),expected)
		self.assertEquals(val,expected)

	def testPutEnvMethod(self):
		pass


if __name__ == '__main__':
	logger.RALogging.initialize()
	unittest.main()



