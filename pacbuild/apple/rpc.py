# 
# pacbuild.apple.rpc - XMLRPC server code
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
# 

import SimpleXMLRPCServer
import SocketServer
import package
from misc import Builder, PacmanConf, Arch
from pacbuild.apple import authUser
import select
from sqlobject import *
from datetime import datetime

server = None

class RPCDaemon:
	def __init__(self):
		self.sessions = []
		
	def getNextBuild(self, user, password, ident, arch):
		user = authUser(user, password)
		arch = Arch.byName(arch)
		builder = Builder.getBuilder(user, ident, arch)
		if not user:
			return False
		nextBuild = package.getNextBuild(builder.arch)
		if nextBuild == None:
			return False
		nextBuild.build(user)
		return (nextBuild.id, '%s-%s-%s.src.tar.gz'%(nextBuild.name, nextBuild.pkgver, nextBuild.pkgrel), nextBuild.source.encode('base64'), nextBuild.pacmanconf.name, nextBuild.pacmanconf.md5sum())

	def submitBuild(self, user, password, buildId, data, log):
		user = authUser(user, password)
		if not user:
			return False
		try:
			build = package.Package.get(buildId)
		except main.SQLObjectNotFound:
			return False
		if build.user != user:
			return False
		if build.status != 'building':
			return False
		if data is not None and data != False:
			data = data.decode('base64')
		elif data == False:
			data = None
		log = log.decode('base64')

		build.finish(data, log)
		return True

	def submitPKGBUILD(self, user, password, arch, name, pkgver, pkgrel, priority, pacmanconfig, source):
		user = authUser(user, password)
		if not user or user.type != 'submitter':
			return 'User is not authorized'
		arch = Arch.byName(arch)
		try:
			pconf = PacmanConf.getConf(pacmanconfig, arch)
		except:
			return "Invalid or unknown build config, '%s'" % pacmanconfig
		build = package.Package(name=name, pkgver=pkgver, pkgrel=pkgrel, status='queued', timestamp=datetime.now(), arch=arch, priority=priority, pacmanconf=pconf)
		build.source = source.decode('base64')
		return 'Build queued with id=%s' % build.id

	def getPackage(self, user, password, id):
		user = authUser(user, password)
		if not user or user.type != 'submitter':
			return False
		build = package.Package.get(id)
		if build.binary != None:
			binary = build.binary.encode('base64')
		else:
			binary = ''
		if build.log != None:
			log = build.log.encode('base64')
		else:
			log = ''
		return ("%s-%s-%s.pkg.tar.gz" % (build.name, build.pkgver, build.pkgrel), binary, log)
	
	def beat(self, user, password, ident, arch):
		user = authUser(user, password)
		if not user:
			return False
		arch = Arch.byName(arch)
		j = Builder.getBuilder(user, ident, arch)
		j.lastBeat = datetime.now()
		return True

	def getPacmanConfig(self, user, password, arch, name):
		user = authUser(user, password)
		if not user:
			return False
		arch = Arch.byName(arch)
		try:
			conf = PacmanConf.getConf(name, arch)
			return (conf.name, conf.arch.name, conf.data)
		except:
			return False


class ThreadedXMLRPC(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer):
	pass

def init():
	global server
	server = SimpleXMLRPCServer.SimpleXMLRPCServer(("", 8888), logRequests=False)
	server.register_instance(RPCDaemon())

def process():
	if len(select.select([server.fileno()],[],[],1)) > 0:
		server.handle_request()

def close():
	global server
	server.server_close()
	server = None
