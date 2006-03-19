# 
# pacbuild - cherry module
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

__all__ = ['misc','package','rpc']

import misc, package
from sqlobject import *

def connect(conn):
	misc.Arch.setConnection(conn)
	misc.Arch.createTable(ifNotExists=True)
	misc.User.setConnection(conn)
	misc.User.createTable(ifNotExists=True)
	misc.Builder.setConnection(conn)
	misc.Builder.createTable(ifNotExists=True)

	package.Package.setConnection(conn)
	package.Package.createTable(ifNotExists=True)

def authUser(name, password):
	try:
		user = misc.User.byName(name)
		if user.password == password:
			return user
		else:
			return False
	except main.SQLObjectNotFound:
		return False
