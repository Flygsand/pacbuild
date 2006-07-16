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
import os, os.path

packagedir = None

class Package(SQLObject):
	name = StringCol()
	pkgver = StringCol()
	pkgrel = StringCol()
	status = EnumCol(enumValues=('queued', 'building', 'done', 'error', 'cancelled'))
	timestamp = DateTimeCol()
	arch = ForeignKey('Arch')
	# 1 is the lowest priority -- I can see always wanting to bump things up, but less wanting to always have things behind other things
	priority = IntCol()

	log = StringCol(default=None)
	user = ForeignKey('User', default=None)
	pacmanconf = ForeignKey('PacmanConf')

	def _set_binary(self, value):
		filename = '%s-%s_%s-%s-%s.pkg.tar.gz' % (self.id, self.arch.name, self.name, self.pkgver, self.pkgrel)
		fullpath = os.path.join(packagedir, filename)
		if value is not None and value != False:
			f = open(fullpath, "wb")
			f.write(value)
			f.close()
		else:
			if os.path.isfile(fullpath):
				os.unlink(fullpath)
	def _get_binary(self):
		filename = '%s-%s_%s-%s-%s.pkg.tar.gz' % (self.id, self.arch.name, self.name, self.pkgver, self.pkgrel)
		fullpath = os.path.join(packagedir, filename)
		if not os.path.isfile(fullpath):
			return None
		else:
			f = open(fullpath, "rb")
			return (f.read(), f.close())[0]

	def _set_source(self, value):
		filename = '%s-%s_%s-%s-%s.src.tar.gz' % (self.id, self.arch.name, self.name, self.pkgver, self.pkgrel)
		fullpath = os.path.join(packagedir, filename)
		if value is not None:
			f = open(fullpath, "wb")
			f.write(value)
			f.close()
		else:
			if os.path.isfile(fullpath):
				os.unlink(fullpath)
	def _get_source(self):
		filename = '%s-%s_%s-%s-%s.src.tar.gz' % (self.id, self.arch.name, self.name, self.pkgver, self.pkgrel)
		fullpath = os.path.join(packagedir, filename)
		if not os.path.isfile(fullpath):
			return None
		else:
			f = open(fullpath, "rb")
			return (f.read(), f.close())[0]

	def build(self, user):
		if self.status == 'queued':
			self.status = 'building'
			self.user = user
			self.timestamp = datetime.now()

	def finish(self, binary, log):
		if self.status == 'building':
			self.binary = binary
			self.log = log
			self.timestamp = datetime.now()
			if self.hasLogError():
				self.status = 'error'
			else:
				self.status = 'done'

	def cancel(self):
		self.status = 'cancelled'
		self.timestamp = datetime.now()

	def unbuild(self):
		if self.status == 'building':
			self.status = 'queued'
			self.user = None
			self.timestamp = datetime.now()

	def isStale(self, delta):
		if self.status == 'building' and datetime.now()-self.timestamp >= delta:
			return True
		return False

	def hasLogError(self, log=None):
		if log is None:
			log = self.log
		if log is not None:
			logstring = ''.join(self.log)
			if ">>>>>>>>>> Error building <<<<<<<<<<" in logstring:
				return True
		return False

def getNextBuild(arch):
	results = Package.select(AND(Package.q.archID==arch.id, Package.q.status=='queued'), orderBy='priority', reversed=True)
	if results.count() > 0:
		return results[0]

def getBuilds():
	return Package.select(Package.q.status=='building')
