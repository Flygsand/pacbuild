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

UMASK = 0

WORKDIR = "/"

MAXFD = 1024

if (hasattr(os, "devnull")):
   REDIRECT_TO = os.devnull
else:
   REDIRECT_TO = "/dev/null"

def createDaemon():
	"""Detach a process from the controlling terminal and run it in the
	background as a daemon.
	"""

	try:
		pid = os.fork()
	except OSError, e:
		raise Exception, "%s [%d]" % (e.strerror, e.errno)

	if (pid == 0):	# The first child.
		os.setsid()

		try:
			pid = os.fork()	# Fork a second child.
		except OSError, e:
			raise Exception, "%s [%d]" % (e.strerror, e.errno)

		if (pid == 0):	# The second child.
			os.chdir(WORKDIR)
			os.umask(UMASK)
		else:
			os._exit(0)	# Exit parent (the first child) of the second child.
	else:
		os._exit(0)	# Exit parent of the first child.

	import resource		# Resource usage information.
	maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
	if (maxfd == resource.RLIM_INFINITY):
		maxfd = MAXFD
  
	# Iterate through and close all file descriptors.
	for fd in range(0, maxfd):
		try:
			os.close(fd)
		except OSError:	# ERROR, fd wasn't open to begin with (ignored)
			pass

	os.open(REDIRECT_TO, os.O_RDWR)	# standard input (0)

	os.dup2(0, 1)			# standard output (1)
	os.dup2(0, 2)			# standard error (2)

	return(0)

def usage():
	print "usage: apple.py [options]"
	print "options:"
	print "       -c <config>     : use a different config than the default (%s)" % defaultConfig
	print "       -d              : run as a daemon"
	sys.exit(2)

def _main(argv=None):
	if argv is None:
		argv = sys.argv

	try:
		optlist, args = getopt.getopt(argv[1:], "c:d")
	except getopt.GetoptError:
		usage()

	configPath = defaultConfig
	for i, k in optlist:
		if i == '-c':
			if os.path.isfile(k):
				configPath = k
		if i == '-d':
			createDaemon()
			pid = open('/var/run/apple.pid', 'w')
			pid.write('%s\n' % os.getpid())
			pid.close()

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
