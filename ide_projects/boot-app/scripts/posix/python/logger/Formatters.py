# -*- coding: utf-8 -*-

import logging, os

class ColorFormatter(logging.Formatter):
	FORMAT = ("[%(levelname)-7s] " \
				"%(message)s " \
				"($BOLD%(filename)s$RESET:%(lineno)d)")

	BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

	RESET_SEQ = "\033[0m"
	COLOR_SEQ = "\033[1;%dm"
	BOLD_SEQ = "\033[1m"

	COLORS = {
		'WARNING': YELLOW,
		'INFO': WHITE,
		'DEBUG': GREEN,
		'CRITICAL': YELLOW,
		'ERROR': RED,
		'TRACE': BLUE,
		'DEBUG1': GREEN,
		'DEBUG2': GREEN,
		'DEBUG3': GREEN,
		'DEBUG4': GREEN
	}

	def formatMsg(self, msg, use_color = True):

		if use_color:
			msg = msg.replace("$RESET", self.RESET_SEQ).replace("$BOLD", self.BOLD_SEQ)
		else:
			msg = msg.replace("$RESET", "").replace("$BOLD", "")
		return msg

	def __init__(self, fmt=None, datefmt=None, use_color=True):

		if not fmt:
			fmt = ColorFormatter.FORMAT
		msg = self.formatMsg(fmt, use_color)

		logging.Formatter.__init__(self, msg,datefmt)

		self.use_color = use_color

	def format(self, record):
		levelname = record.levelname
		if self.use_color and levelname in self.COLORS:
			fore_color = 30 + self.COLORS[levelname]
			levelname_color = self.COLOR_SEQ % fore_color + levelname + self.RESET_SEQ
			record.levelname = levelname_color

		ss = logging.Formatter.format(self, record)
		return ss.replace(os.linesep,'')
