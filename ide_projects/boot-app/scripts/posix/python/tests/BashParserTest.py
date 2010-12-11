# -*- coding: utf-8 -*-

# User: Grzegorz (vara) Warywoda
# Date: 2010-11-13
# Time: 20:37:51
import sys, os, unittest
import UtilsForTests

from configuration.BashParser import BashParserImpl
import configuration.Configuration
from configuration.Configuration import KeyEntry

class BashParserTest(unittest.TestCase):

	def testSeparatorChars(self):
		print "Test separator chars"
		KEY = KeyEntry("VALUE","ELO")
		configuration.Configuration.env.putEnv(KEY,KEY.getDefaultValue())

		lines = { "prefix $VALUE postfix"	: "prefix "+KEY.getDefaultValue()+" postfix",
				  "prefix$VALUEpostfix"		: "prefix",
				  "prefix$VALUE.postfix"	: "prefix"+KEY.getDefaultValue()+".postfix",
				  "prefix.$VALUE.postfix"	: "prefix."+KEY.getDefaultValue()+".postfix",
				  "prefix.$VALUE$postfix"	: "prefix."+KEY.getDefaultValue()
				}

		parse = getattr(BashParserImpl(),"_BashParserImpl__parseRValue");

		for k,v in lines.iteritems():
			result = parse(k)

			print "*** Key:'%s' \tgot: '%s'" %(k,result)

			self.assertEquals(v,result)

if __name__ == '__main__':

	unittest.main()
