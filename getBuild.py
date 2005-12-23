#!/usr/bin/env python
# 
# updatePkgbuild - Temporary script to upload PKBUILD to an apple instance
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

	if len(argv) != 5:
		print "usage: %s <server> <user> <password> <id>" % argv[0]
		return 1

	server = xmlrpclib.ServerProxy(argv[1])
	res = server.getPackage(argv[2], argv[3], int(argv[4]))
	
	if res != False:
		binary = open(res[0], "wb")
		binary.write(res[1].decode('base64'))
		log = open("%s.log" %res[0], "wb")
		log.write(res[2].decode('base64'))
	else:
		print "Auth error"

if __name__ == "__main__":
	sys.exit(_main())
