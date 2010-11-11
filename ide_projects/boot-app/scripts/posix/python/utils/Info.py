# -*- coding: utf-8 -*-

# User: Grzegorz (vara) Warywoda
# Date: 2010-11-10
# Time: 22:56:44

# From http://en.wikipedia.org/wiki/%3Azanurkuj_w_pythonie

def info(object, spacing=10, collapse=1): #(1) (2) (3)
	u"""Wypisuje metody i ich notki dokumentacyjne.
	Argumentem może być moduł, klasa, lista, słownik, czy też łańcuch znaków."""
	methodList = [method for method in dir(object) if callable(getattr(object, method))]
	processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
	print "\n".join(["%s %s" %
				  (method.ljust(spacing),
				   processFunc(unicode(getattr(object, method).__doc__)))
				 for method in methodList])
