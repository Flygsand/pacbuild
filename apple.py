#!/usr/bin/env python
# 
# apple - Build distribution daemon
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
#sys.path.append('/etc')
#import appleConfig
import getopt
import os, os.path
from pacbuild.apple import connect, rpc, package

defaultConfig = "/etc/appleConfig.py"
appleConfig = {}

def usage():
	print "usage: apple.py [options]"
	print "options:"
	print "       -c <config>     : use a different config than the default (%s)" % defaultConfig
	sys.exit(2)

def _main(argv=None):
	if argv is None:
		argv = sys.argv

	try:
		optlist, args = getopt.getopt(argv[1:], "c:")
	except getopt.GetoptError:
		usage()

	configPath = defaultConfig
	for i, k in optlist:
		if i == '-c':
			if os.path.isfile(k):
				configPath = k

	execfile(configPath, appleConfig, appleConfig)

	connect(appleConfig['database'])

	rpc.init()

	try:
		while True:
			for i in package.getBuilds():
				if i.isStale(appleConfig['stalePackageTimeout']):
					i.unbuild()
			rpc.process()
	except KeyboardInterrupt:
		pass

	return 0

if __name__ == "__main__":
	sys.exit(_main())
