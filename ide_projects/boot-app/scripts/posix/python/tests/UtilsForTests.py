# -*- coding: utf-8 -*-

# User: Grzegorz (vara) Warywoda
# Date: 2010-11-10
# Time: 20:21:48

import os

def getAbsDirName(path,topLevels=0):
	"""
		Get absolute path to directory name for argumnet 'path'.
		Second argument determine how many top-level directories
		should be ommited.

		e.q.
		 	f = /dir3/dir2/dir1/dir0
			getAbsDirName(f)	=> /dir3/dir2/dir1/dir0
			getAbsDirName(f,2)	=> /dir3/dir2
	"""
	if os.path.islink(path):
		path = os.path.realpath(path)
	path = os.path.abspath(path)

	if os.path.isfile(path):
		path = os.path.dirname(path)

	if topLevels > 0:
		for i in range(0,topLevels):
			path = os.path.dirname(path)

	return path

os.sys.path.append( getAbsDirName(__file__,1))

import configuration.Configuration

def insertVar(key,value):
		"""
		This is a forcing for inserting variable directly
		to local environment variables container.
		Operands should be validated before calling this method.
		"""
		configuration.Configuration._Env.put([[key,value]])

if __name__ == "__main__":
	for i in range(0,3):
		print i, ":", getAbsDirName(__file__,i)
