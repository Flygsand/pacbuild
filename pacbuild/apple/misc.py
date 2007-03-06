# 
# pacbuild.apple.misc - Simple single class data types
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

from sqlobject import *
from datetime import datetime
from md5 import md5

class Arch(SQLObject):
	name = StringCol(alternateID=True)
	packageArchs = MultipleJoin('Package')
	builders = MultipleJoin('Builder')

class User(SQLObject):
	name = StringCol(alternateID=True)
	password = StringCol()
	email = StringCol()
	packages = MultipleJoin('Package')
	type = EnumCol(enumValues=('builder', 'submitter'))

class Builder(SQLObject):
	user = ForeignKey('User')
	ident = StringCol()
	arch = ForeignKey('Arch')
	lastBeat = DateTimeCol(default=datetime.now)

	@classmethod
	def getBuilder(cls, user, ident, arch):
		builders = cls.select(AND(Builder.q.userID == user.id, Builder.q.ident == ident, Builder.q.archID == arch.id))
		builders = builders[:1]
		builder = None
		for b in builders:
			builder = b
		if builder == None:
			builder = cls(user=user, ident=ident, arch=arch, lastBeat=datetime.now())
		return builder

class PacmanConf(SQLObject):
	name = StringCol(alternateID=True)
	data = StringCol()

	def md5sum(self):
		return md5(self.data).hexdigest()
