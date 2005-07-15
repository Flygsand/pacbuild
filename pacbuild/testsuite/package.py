#!/usr/bin/env python

import unittest
import os
import warnings
import shutil

from pacbuild.cherry import repo, package, misc, connect
from sqlobject import *
from datetime import datetime

class PackageTest(unittest.TestCase):
	def setUp(self):
		warnings.filterwarnings("ignore", "tmpnam", RuntimeWarning, __name__)
		self.tmpdir = os.tmpnam()
		os.makedirs(self.tmpdir)
		conn = connectionForURI("sqlite://%s/test.db"%self.tmpdir)
		connect(conn)
		self.repo = repo.Repo(name='current', absdir='%s/abs'%self.tmpdir, repodir='na', updatescript='na')
		self.arch = misc.Arch(name='i586') 
		shutil.copytree('pacbuild/testsuite/testAbs', '%s/abs'%self.tmpdir)

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def testCanQueue(self):
		glibc = package.Package(name="glibc", repo=self.repo)
		distcc = package.Package(name="distcc", repo=self.repo)
		db = package.Package(name='db', repo=self.repo)

		glibcArch = package.PackageArch(applies=1, arch=self.arch, package=glibc)
		distccArch = package.PackageArch(applies=1, arch=self.arch, package=distcc)
		dbArch = package.PackageArch(applies=1, arch=self.arch, package=db)

		glibcInstance1 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now())
		glibcInstance2 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='3', status='new', timestamp=datetime.now())

		distccInstance = package.PackageInstance(packageArch=distccArch, pkgver='2.18.3', pkgrel='1', status='new', timestamp=datetime.now())

		dbInstance1 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.28', pkgrel='1', status='build-error', timestamp=datetime.now())
		dbInstance2 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.27', pkgrel='1', status='new', timestamp=datetime.now())


		self.failIf(glibcInstance1.canQueue())
		self.failIf(glibcInstance2.canQueue())
		self.failUnless(distccInstance.canQueue())
		self.failIf(dbInstance1.canQueue())
		self.failUnless(dbInstance2.canQueue())

	def testQueue(self):
		glibc = package.Package(name="glibc", repo=self.repo)
		distcc = package.Package(name="distcc", repo=self.repo)
		db = package.Package(name='db', repo=self.repo)

		glibcArch = package.PackageArch(applies=1, arch=self.arch, package=glibc)
		distccArch = package.PackageArch(applies=1, arch=self.arch, package=distcc)
		dbArch = package.PackageArch(applies=1, arch=self.arch, package=db)

		glibcInstance1 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now())
		glibcInstance2 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='3', status='new', timestamp=datetime.now())

		distccInstance = package.PackageInstance(packageArch=distccArch, pkgver='2.18.3', pkgrel='1', status='new', timestamp=datetime.now())

		dbInstance1 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.28', pkgrel='1', status='build-error', timestamp=datetime.now())
		dbInstance2 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.27', pkgrel='1', status='new', timestamp=datetime.now())


		glibcInstance2.queue()
		self.failIf(glibcInstance2.status == 'queued')
		distccInstance.queue()
		self.failUnless(distccInstance.status == 'queued')
		dbInstance1.queue()
		self.failIf(dbInstance1.status == 'queued')
		dbInstance2.queue()
		self.failUnless(dbInstance2.status == 'queued')

	def testCanFreshen(self):
		glibc = package.Package(name="glibc", repo=self.repo)
		distcc = package.Package(name="distcc", repo=self.repo)
		db = package.Package(name='db', repo=self.repo)

		glibcArch = package.PackageArch(applies=1, arch=self.arch, package=glibc)
		distccArch = package.PackageArch(applies=1, arch=self.arch, package=distcc)
		dbArch = package.PackageArch(applies=1, arch=self.arch, package=db)

		glibcInstance1 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now())
		glibcInstance2 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='3', status='new', timestamp=datetime.now())

		distccInstance = package.PackageInstance(packageArch=distccArch, pkgver='2.18.3', pkgrel='1', status='new', timestamp=datetime.now())

		dbInstance1 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.28', pkgrel='1', status='build-error', timestamp=datetime.now())
		dbInstance2 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.27', pkgrel='1', status='new', timestamp=datetime.now())


		self.failIf(glibcInstance1.canFreshen())
		oldPkg = glibcInstance2.canFreshen()
		self.failUnless(oldPkg == glibcInstance1)
		self.failIf(distccInstance.canFreshen())
		self.failIf(dbInstance1.canFreshen())
		self.failIf(dbInstance2.canFreshen())

	def testFreshen(self):
		glibc = package.Package(name="glibc", repo=self.repo)
		distcc = package.Package(name="distcc", repo=self.repo)
		db = package.Package(name='db', repo=self.repo)

		glibcArch = package.PackageArch(applies=1, arch=self.arch, package=glibc)
		distccArch = package.PackageArch(applies=1, arch=self.arch, package=distcc)
		dbArch = package.PackageArch(applies=1, arch=self.arch, package=db)

		glibcInstance1 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now())
		glibcInstance2 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='3', status='new', timestamp=datetime.now())

		distccInstance = package.PackageInstance(packageArch=distccArch, pkgver='2.18.3', pkgrel='1', status='new', timestamp=datetime.now())

		dbInstance1 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.28', pkgrel='1', status='build-error', timestamp=datetime.now())
		dbInstance2 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.27', pkgrel='1', status='new', timestamp=datetime.now())


		glibcInstance2.freshen()
		self.failUnless(glibcInstance2.status == 'queued')
		self.failUnless(glibcInstance1.status == 'freshened')
		distccInstance.freshen()
		self.failUnless(distccInstance.status == 'new')
		dbInstance1.freshen()
		self.failIf(dbInstance1.status == 'queued')
		dbInstance2.freshen()
		self.failIf(dbInstance2.status == 'queued')
		self.failUnless(dbInstance1.status == 'build-error')

	def testCanBuild(self):
		glibc = package.Package(name="glibc", repo=self.repo)
		distcc = package.Package(name="distcc", repo=self.repo)
		db = package.Package(name='db', repo=self.repo)

		glibcArch = package.PackageArch(applies=1, arch=self.arch, package=glibc)
		distccArch = package.PackageArch(applies=1, arch=self.arch, package=distcc)
		dbArch = package.PackageArch(applies=1, arch=self.arch, package=db)

		glibcInstance1 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now())
		glibcInstance2 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='3', status='new', timestamp=datetime.now())

		distccInstance = package.PackageInstance(packageArch=distccArch, pkgver='2.18.3', pkgrel='1', status='new', timestamp=datetime.now())

		dbInstance1 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.28', pkgrel='1', status='build-error', timestamp=datetime.now())
		dbInstance2 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.27', pkgrel='1', status='new', timestamp=datetime.now())


		self.failUnless(glibcInstance1.canBuild())
		self.failIf(glibcInstance2.canBuild())
		self.failIf(distccInstance.canBuild())
		self.failIf(dbInstance1.canBuild())
		self.failIf(dbInstance2.canBuild())

	def testBuild(self):
		glibc = package.Package(name="glibc", repo=self.repo)
		distcc = package.Package(name="distcc", repo=self.repo)
		db = package.Package(name='db', repo=self.repo)

		glibcArch = package.PackageArch(applies=1, arch=self.arch, package=glibc)
		distccArch = package.PackageArch(applies=1, arch=self.arch, package=distcc)
		dbArch = package.PackageArch(applies=1, arch=self.arch, package=db)

		glibcInstance1 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now())
		glibcInstance2 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='3', status='new', timestamp=datetime.now())

		distccInstance = package.PackageInstance(packageArch=distccArch, pkgver='2.18.3', pkgrel='1', status='new', timestamp=datetime.now())

		dbInstance1 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.28', pkgrel='1', status='build-error', timestamp=datetime.now())
		dbInstance2 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.27', pkgrel='1', status='new', timestamp=datetime.now())


		glibcInstance1.build()
		self.failUnless(glibcInstance1.status == 'building')
		distccInstance.build()
		self.failUnless(distccInstance.status == 'new')
		dbInstance1.build()
		self.failUnless(dbInstance1.status == 'build-error')
		dbInstance2.build()
		self.failUnless(dbInstance2.status == 'new')

if __name__ == "__main__":
	unittest.main()
