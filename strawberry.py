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
import xmlrpclib
import threading
import os, os.path

from sqlobject import *

import strawberryConfig

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
	def __init__(self, buildDir, **other):
		threading.Thread.__init__(self, *other)
		self.buildDir = buildDir
		makeWakaConf()

	def makeWakaConf(self):
		if (not os.path.isDir(self.buildDir)):
			os.makedirs(self.buildDir)
		

	def run(self):
		pass

def canBuild():
	return Build.select().count() < strawberryConfig.maxBuilds

def getNextBuild():
	server = xmlrpclib.ServerProxy(strawberryConfig.url)
	build = server.getNextBuild(strawberryConfig.user, strawberryConfig.password)
	if build is not None and build is not False:
		return Build(cherryId=build[0], sourceFilename=build[1], source=build[2].decode('base64'))
	return None

def _main(argv=None):
	if argv is None:
		argv = sys.argv

	Build.setConnection(strawberryConfig.database)
	Build.createTable(ifNotExists=True)

	while True:
		if canBuild():
			build = getNextBuild()
			print "Got a new build: %s" % build.sourceFilename
			# This is where you'd set up waka

if __name__ == "__main__":
	sys.exit(_main())
