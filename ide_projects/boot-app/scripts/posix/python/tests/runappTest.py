# -*- coding: utf-8 -*-

import sys, os, unittest
import UtilsForTests

if __name__ == "__main__":
	sys.path.append( UtilsForTests.getAbsDirName(__file__,1))

import runapp

class RunappTest(unittest.TestCase):
	                                   # expected value, is non-null value?, expected index
	cases = {"~/dir -opts -- -appOpts" : ("-opts -- -appOpts"		,True,	0),
			 "-opts ~/dir -- -appOpts" : ("-opts -- -appOpts"		,True,	1),

			 "-opts -- ~/dir -appOpts" : ("-opts -- ~/dir -appOpts"	,False,-1),
			 "-opts -- -appOpts ~/dir" : ("-opts -- -appOpts ~/dir"	,False,-1),
			 "-opts -- -appOpts"       : ("-opts -- -appOpts"		,False,-1),

			 "-opts ~/dir"             : ("-opts"					,True,	1),
			 "-opts ~/dir -appOpts"    : ("-opts -- -appOpts"		,True,	1),
			 "~/dir"                   : ([]						,True,	0),
			 "-opts -opts ~/dir"       : ("-opts -opts"				,True,	2),
			 " "                       : (" "						,False,-1)
			}

	def setUp(self):
		pass


	def testResolveNonOptionFromListFunction(self):
		print "RunappTest test ResolveNonOptionFromListFunction"

		for case in self.cases.iteritems():

			print "----------------------------" \
				  "------------------------------------"
			print "- Test for case : ",case
			print "-\n-"

			args = case[0].split(" ")

			if hasattr(case[1][0],"split"):
				expected = case[1][0].split(" ")
			else:
				expected = case[1][0]

			isNotNone = case[1][1]
			expectedIndex = case[1][2]

			val = runapp.resolveNonOptionFromList(args)

			print "results: ",args," retVal: ",val

			if isNotNone == True:
				self.assertTrue(val != None)
			else:
				self.assertTrue(val == None)
			
			self.assertEquals(args,expected)

			if  isNotNone == True :
				self.assertTrue(len(val)==2)
				self.assertTrue(val[0] == "~/dir")
				self.assertTrue(val[1] == expectedIndex)

	def testToCMDLString(self):

		mapOfVal = [("1",None),("2",None),("3",None)]
		
		expected = "1:2:3"
		print mapOfVal
		result = runapp.toCommandLineString(mapOfVal)

		self.assertEquals(expected,result)


if __name__ == '__main__':
	unittest.main()
