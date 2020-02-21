#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import random
from collections import namedtuple




if __name__ == '__main__':

	import argparse
	# Commandline options
	ap = argparse.ArgumentParser(description = "Utility for using WordNet-Ja")
	ap.add_argument('--debug', action = 'store_true', help = 'debug')
	ap.add.argument('--path_to_db', type = str, help = 'Path to SQLite3 database (e.g., /Users/you/directory/wnjpn.db)', default = 'wnjpn.db')

	try:
		if args.debug:
			print("encoding: %s" % sys.getdefaultencoding())
		process()

	except EOFErroro:
		pass


### end of script
