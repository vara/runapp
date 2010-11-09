# -*- coding: utf-8 -*-

import os,sys

""" This module is used to only determine root directory of project.
	In other words this works as marker of root node of the project.
	An idea borrowed from http://wiki.python.org/moin/Distutils/Tutorial
"""

__CACHED_PATH = None

def determinePath():

	"""Get path to root dirertory of project """

	global __CACHED_PATH
	
	if not __CACHED_PATH:
		try:
			root = __file__
			if os.path.islink (root):
				root = os.path.realpath (root)

			root = os.path.dirname (os.path.abspath (root))

		except:
			root = os.path.dirname(os.path.abspath(sys.argv[0]))

		__CACHED_PATH = root

	return __CACHED_PATH
