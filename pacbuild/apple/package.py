# 
# pacbuild.apple.package - Package specific code
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

class Package(SQLObject):
	name = StringCol()
	pkgver = StringCol()
	pkgrel = StringCol()
	status = EnumCol(enumValues=('queued', 'building', 'done', 'cancelled'))
	timestamp = DateTimeCol()
	arch = ForeignKey('Arch')
	# 1 is the lowest priority -- I can see always wanting to bump things up, but less wanting to always have things behind other things
	priority = IntCol()

	log = StringCol(default=None)
	binary = StringCol(default=None)
	source = StringCol(default=None)
	user = ForeignKey('User', default=None)

	def _set_binary(self, value):
		if value is not None:
			self._SO_set_binary(value.encode('base64').replace('\n',''))
		else:
			self._SO_set_binary(None)
	def _get_binary(self):
		if self._SO_get_binary() == None:
			return None
		else:
			return self._SO_get_binary().decode('base64')

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

	def build(self, user):
		if self.status == 'queued' and user.type == 'builder':
			self.status = 'building'
			self.user = user
			self.timestamp = datetime.now()

	def finish(self, binary, log):
		if self.status == 'building':
			self.status = 'done'
			self.binary = binary
			self.log = log
			self.timestamp = datetime.now()

	def cancel(self):
		self.status = 'cancelled'
		self.timestamp = datetime.now()

	def unbuild(self):
		if self.status == 'building':
			self.status = 'queued'
			self.user = None
			self.timestamp = datetime.now()

def getNextBuild(arch):
	results = Package.select(AND(Package.q.archID==arch.id, Package.q.status=='queued'), orderBy='priority', reversed=True)
	if results.count() > 0:
		return results[0]
