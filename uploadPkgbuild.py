#!/usr/bin/env python
# 
# updatePkgbuild - Temporary script to upload PKGBUILD to an apple instance
# Copyright (C) 2005 Jason Chu <jason@archlinux.org>
# 
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# 

import sys
import xmlrpclib
import threading
import os, os.path
import re
import time

from sqlobject import *

def _main(argv=None):
	if argv is None:
		argv = sys.argv

	if len(argv) != 10:
		print "usage: %s <server> <user> <password> <priority> <pacman config> <name> <pkgver> <pkgrel> <source>" % argv[0]
		return 1

	binary = open(argv[9], "rb")
	bin = binary.read().encode('base64')

	server = xmlrpclib.ServerProxy(argv[1])
	print server.submitPKGBUILD(argv[2], argv[3], argv[6], argv[7], argv[8], int(argv[4]), argv[5], bin)

if __name__ == "__main__":
	sys.exit(_main())
