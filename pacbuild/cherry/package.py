# 
# pacbuild.cherry.package - Package specific code
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
	name = StringCol(alternateID=True)
	repo = ForeignKey('Repo')
	packageArchs = MultipleJoin('PackageArch')

class PackageArch(SQLObject):
	applies = IntCol()
	arch = ForeignKey('Arch')
	package = ForeignKey('Package')
	packageInstances = MultipleJoin('PackageInstance')

	def getInstance(self):
		for i in self.packageInstances:
			if i.status == 'queued':
				return i

class PackageInstance(SQLObject):
	packageArch = ForeignKey('PackageArch')
	pkgver = StringCol()
	pkgrel = StringCol()
	status = EnumCol(enumValues=('new', 'queued', 'building', 'build-error', 'dep-wait', 'freshend', 'verifying', 'accepted', 'invalid'))
	timestamp = DateTimeCol()
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

	def canQueue(self):
		q = PackageInstance.select(PackageInstance.q.packageArchID==self.packageArch.id)
		if self.status == 'new':
			for i in q:
				if i.status in ('queued', 'building', 'verifying'):
					return False
			return True
		return False

	def queue(self):
		if self.canQueue():
			self.status = 'queued'
			self.timestamp = datetime.now()

	def canFreshen(self):
		q = PackageInstance.select(PackageInstance.q.packageArchID==self.packageArch.id)
		if self.status == 'new':
			for i in q:
				if i.status == 'queued':
					return i
			return False
		return False

	def freshen(self):
		oldPkg = self.canFreshen()
		if oldPkg:
			oldPkg.status = 'freshened'
			oldPkg.timestamp = datetime.now()
			self.queue()

	def canBuild(self):
		q = PackageInstance.select(PackageInstance.q.packageArchID==self.packageArch.id)
		if self.status == 'queued':
			for i in q:
				if i.status in ('building', 'verifying'):
					return False
			return True
		return False

	def build(self, user=None):
		if self.canBuild():
			self.status = 'building'
			self.timestamp = datetime.now()
			if user:
				self.user = user

def getNextBuild(arch):
	packageArchs = arch.packageArchs
	def cmpArchs(x, y):
		xInstance = x.getInstance()
		yInstance = y.getInstance()
		if xInstance == None and yInstance != None:
			return 1
		elif xInstance != None and yInstance == None:
			return -1
		elif xInstance == None and yInstance == None:
			return 0
		return x.getInstance().timestamp == y.getInstance().timestamp
	packageArchs.sort(cmp=cmpArchs)
	if len(packageArchs) >= 1:
		return packageArchs[0].getInstance()
	else:
		return None
