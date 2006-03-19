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
from misc import Builder
from pacbuild.apple import authUser
import select
from sqlobject import *
from datetime import datetime

server = None

class RPCDaemon:
	def __init__(self):
		self.sessions = []
		
	def getNextBuild(self, user, password):
		user = authUser(user, password)
		if not user:
			return False
		nextBuild = package.getNextBuild(user.arch)
		if nextBuild == None:
			return False
		nextBuild.build(user)
		return (nextBuild.id, '%s-%s-%s.src.tar.gz'%(nextBuild.name, nextBuild.pkgver, nextBuild.pkgrel), nextBuild.source.encode('base64'))

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

	def submitPKGBUILD(self, user, password, name, pkgver, pkgrel, priority, source):
		user = authUser(user, password)
		if not user or user.type != 'submitter':
			return False
		build = package.Package(name=name, pkgver=pkgver, pkgrel=pkgrel, status='queued', timestamp=datetime.now(), arch=user.arch, priority=priority)
		build.source = source.decode('base64')
		return build.id

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
	
	def beat(self, user, password, ident):
		user = authUser(user, password)
		if not user:
			return False
		j = list(Builder.select(AND(Builder.q.userID == user.id, Builder.q.ident == ident)))
		if not j:
			j = Builder(user=user, ident=ident)
			return True
		j[0].lastBeat = datetime.now()
		return True

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
