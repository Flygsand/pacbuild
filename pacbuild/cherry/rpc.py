# 
# pacbuild.cherry.rpc - XMLRPC server code
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
from pacbuild.cherry import authUser
import select

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
			return None
		nextBuild.build(user)
		return (nextBuild.id, '%s-%s-%s.src.tar.gz'%(nextBuild.packageArch.package.name, nextBuild.pkgver, nextBuild.pkgrel), nextBuild.source.encode('base64'))
		

class ThreadedXMLRPC(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer):
	pass

def init():
	global server
	server = ThreadedXMLRPC(("", 8888))

def process():
	if len(select.select([server.fileno()],[],[],1)) > 0:
		server.handle_request()

def close():
	global server
	server.server_close()
	server = None
