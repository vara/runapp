# -*- coding: utf-8 -*-

# User: Grzegorz (vara) Warywoda
# Date: 2010-11-14
# Time: 01:34:34

import unittest,sys

import UtilsForTests

import ConfigurationTest
import runappTest
import BashParserTest

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(ConfigurationTest.EnvironmentTest))
	suite.addTest(unittest.makeSuite(runappTest.RunappTest))
	suite.addTest(unittest.makeSuite(BashParserTest.BashParserTest))
	return suite

if __name__ == '__main__':
	unittest.TextTestRunner().run(suite())
