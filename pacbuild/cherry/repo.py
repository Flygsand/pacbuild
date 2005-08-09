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
from datetime import datetime
import pacman
import tarfile

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
			yield (path, pkgbuild)
	instances = property(getInstances)

	def getPackages(self):
		pass

	def addFile(self):
		pass

def getInstances(repo, arch):
	for path, i in repo.instances:
		try:
			pkg = package.Package.byName(i.name)
		except main.SQLObjectNotFound:
			pkg = package.Package(name=i.name, repo=repo)

		pkgArch = None
		for j in pkg.packageArchs:
			if j.arch == arch:
				pkgArch = j
				break
		if not pkgArch:
			pkgArch = package.PackageArch(applies=True, arch=arch, package=pkg)

		pkgInstance = None
		for j in pkgArch.packageInstances:
			if j.pkgver == i.version and j.pkgrel == i.release:
				pkgInstance = j
				break
		if not pkgInstance:
			# Time to build source package
			srcpkg = os.tmpfile()
			srcpkgtar = tarfile.open(name="", fileobj=srcpkg, mode='w:gz')
			path = os.path.dirname(path)
			for j in os.listdir(path):
				srcpkgtar.add(os.path.join(path, j), arcname=j)
			srcpkgtar.close()
			srcpkg.seek(0)
			pkgInstance = package.PackageInstance(pkgver=i.version,
			                                      pkgrel=i.release,
			                                      status='new',
			                                      timestamp=datetime.now(),
			                                      packageArch=pkgArch,
			                                      source=srcpkg.read())
		yield pkgInstance
