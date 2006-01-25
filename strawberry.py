#!/usr/bin/env python
# 
# strawberry - Main client daemon
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
import xmlrpclib
import threading
import os, os.path
import re
import time
import shutil
import getopt

from sqlobject import *

defaultConfig = "/etc/strawberryConfig.py"

#import strawberryConfig
strawberryConfig = {}

class Build(SQLObject):
	cherryId = IntCol()
	sourceFilename = StringCol()
	source = StringCol()

	def _set_source(self, value):
		if value is not None:
			self._SO_set_source(value.encode('base64').replace('\n',''))
		else:
			self._SO_set_source(None)
	def _get_source(self):
		if self._SO_get_source() == None:
			return None
		else:
			return self._SO_get_source().decode('base64')

class Waka(threading.Thread):
	def __init__(self, build, buildDir, **other):
		threading.Thread.__init__(self, *other)
		self.buildDir = buildDir
		self.build = build
		self.filename = build.sourceFilename
		self.sourcePkg = os.path.join(self.buildDir, self.filename)
		self.makeWakaConf()
		self.makeSourceFile(build.source)

	def makeSourceFile(self, fileData):
		file = open(self.sourcePkg, "wb")
		file.write(fileData)
		file.close()

	def makeWakaConf(self):
		if (not os.path.isdir(self.buildDir)):
			os.makedirs(self.buildDir)
		self.mkchrootPath = os.path.join(self.buildDir,"mkchroot.conf")
		self.pacmanconfPath = os.path.join(self.buildDir,"pacman.conf")
		conf = open(self.mkchrootPath, "w")
		conf.write('WAKA_ROOT_DIR="%s"\n'%self.buildDir)
		conf.write('WAKA_CHROOT_DIR="chroot/"\n')
		conf.write('QUIKINST_LOCATION="/usr/share/waka/quickinst"\n')
		conf.write('PACKAGE_MIRROR_CURRENT="ftp://ftp.archlinux.org/current/os/${CARCH}"\n')
		conf.write('PACKAGE_MIRROR_EXTRA="ftp://ftp.archlinux.org/extra/os/${CARCH}"\n')
		conf.write('DEFAULT_PKGDEST=${WAKA_ROOT_DIR}/\n')
		conf.write('DEFAULT_KERNEL=kernel26\n')
		conf.close()
		if strawberryConfig.has_key('pacmanConf'):
			pacmanconf = open(self.pacmanconfPath, "w")
			pacmanconf.write(strawberryConfig['pacmanConf'])
			pacmanconf.close()

	def run(self):
		os.system("/usr/bin/mkchroot -p %s -o %s %s"%(self.pacmanconfPath, self.mkchrootPath, self.sourcePkg))
		# Do the post build stuff
		self.binaryPkg = re.sub('\.src\.tar\.gz$', '.pkg.tar.gz', self.sourcePkg)
		self.logFile = re.sub('\.src\.tar\.gz$', '.makepkg.log', self.sourcePkg)

		if os.path.isfile(self.binaryPkg):
			binary = open(self.binaryPkg).read()
		else:
			binary = False
		log = open(self.logFile).read()
		sendBuild(self.build, binary, log)
		shutil.rmtree(self.buildDir)

def canBuild():
	return Build.select().count() < strawberryConfig['maxBuilds']

def getNextBuild():
	server = xmlrpclib.ServerProxy(strawberryConfig['url'])
	build = server.getNextBuild(strawberryConfig['user'], strawberryConfig['password'])
	if build is not None and build is not False:
		return Build(cherryId=build[0], sourceFilename=build[1], source=build[2].decode('base64'))
	return None

def sendBuild(build, binary, log):
	server = xmlrpclib.ServerProxy(strawberryConfig['url'])
	if binary is not False:
		bin64 = binary.encode('base64')
	else:
		bin64 = False
	server.submitBuild(strawberryConfig['user'], strawberryConfig['password'], build.cherryId, bin64, log.encode('base64'))

def usage():
	print "usage: strawberry.py [-c <config>]"
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

	execfile(configPath, strawberryConfig, strawberryConfig)

	Build.setConnection(strawberryConfig['database'])
	Build.createTable(ifNotExists=True)

	threads = []

	# Start any builds that never actually finished last time
	for i in Build.select():
		if not os.path.isdir(os.path.join(strawberryConfig['buildDir'], i.sourceFilename)):
			waka = Waka(i, os.path.join(strawberryConfig['buildDir'], i.sourceFilename))
			waka.start()
			threads.append(waka)

	while True:
		if canBuild():
			build = getNextBuild()
			if build is not None and build is not False:
				print "Got a new build: %s" % build.sourceFilename
				
				# This is where you'd set up waka
				waka = Waka(build, os.path.join(strawberryConfig['buildDir'], build.sourceFilename))
				waka.start()
				threads.append(waka)
		for i, v in enumerate(threads):
			if not v.isAlive():
				print "Cleaning up from thread"
				Build.delete(waka.build.id)
				del threads[i]
		time.sleep(strawberryConfig['sleeptime'])
			

if __name__ == "__main__":
	sys.exit(_main())
