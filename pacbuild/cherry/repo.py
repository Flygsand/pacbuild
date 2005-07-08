# 
# pacbuild.cherry.repo - Repo code
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

from sqlobject import *
import os
import os.path
import package

class Repo(SQLObject):
	name = StringCol(alternateID=True)
	absdir = StringCol()
	repodir = StringCol()
	updatescript = StringCol()
	packages = MultipleJoin('Package')

	def getCategories(self, withDir=False):
		for category in os.listdir(self.absdir):
			catdir = os.path.join(self.absdir, category)
			if os.path.isdir(catdir):
				if withDir:
					yield catdir
				else:
					yield category
	categories = property(getCategories)

	def getPkgbuilds(self, withDir=False):
		for catdir in self.getCategories(True):
			for packageDir in os.listdir(catdir):
				pkgbuild = os.path.join(catdir, packageDir, 'PKGBUILD')
				if os.path.isfile(pkgbuild):
					if withDir:
						yield pkgbuild
					else:
						yield packageDir
	pkgbuilds = property(getPkgbuilds)

	def getInstances(self):
		for path in self.getPkgbuilds(True):
			pkgbuild = pacman.load(path)
			try:
				pkg = package.Package.byName(pkgbuild.name)
			except main.SQLObjectNotFound:
				pkg = package.Package(name=pkgbuild.name)
			yield pkg
	instances = property(getInstances)
