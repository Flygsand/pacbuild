#!/usr/bin/env python

import unittest
import os
import warnings
import shutil

from pacbuild.apple import package, misc, connect
from sqlobject import *
from datetime import datetime
from datetime import timedelta

conn = connectionForURI("sqlite:/:memory:")
connect(conn)
class PackageTest(unittest.TestCase):
	def setUp(self):
#		warnings.filterwarnings("ignore", "tmpnam", RuntimeWarning, __name__)
#		self.tmpdir = os.tmpnam()
#		os.makedirs(self.tmpdir)
		self.trans = conn.transaction()
		connect(self.trans)
		self.arch = misc.Arch(name='i586') 
		self.user = misc.User(name='jchu', password='a', email='a', arch=self.arch, type='builder')
		self.submitter = misc.User(name='blah', password='a', email='a', arch=self.arch, type='submitter')

	def tearDown(self):
		self.trans.rollback()
		connect(conn)
#		shutil.rmtree(self.tmpdir)

	def testBuild(self):
		glibc1 = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now(), priority=1)
		glibc2 = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='3', status='building', timestamp=datetime.now(), priority=1, user=self.user)
		distcc1 = package.Package(name="distcc", arch=self.arch, pkgver='2.18.3', pkgrel='1', status='done', timestamp=datetime.now(), priority=1)
		db1 = package.Package(name='db', arch=self.arch, pkgver='4.3.28', pkgrel='1', status='cancelled', timestamp=datetime.now(), priority=1)

		glibc1.build(self.user)
		glibc2.build(self.user)
		distcc1.build(self.user)
		db1.build(self.user)

		self.failIf(glibc1.status != 'building')
		self.failIf(glibc2.status != 'building')
		self.failIf(distcc1.status != 'done')
		self.failIf(db1.status != 'cancelled')

	def testFinish(self):
		glibc1 = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now(), priority=1)
		glibc2 = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='3', status='building', timestamp=datetime.now(), priority=1, user=self.user)
		distcc1 = package.Package(name="distcc", arch=self.arch, pkgver='2.18.3', pkgrel='1', status='done', timestamp=datetime.now(), priority=1)
		db1 = package.Package(name='db', arch=self.arch, pkgver='4.3.28', pkgrel='1', status='cancelled', timestamp=datetime.now(), priority=1)

		glibc1.finish('', '')
		glibc2.finish('', '')
		distcc1.finish('', '')
		db1.finish('', '')

		self.failIf(glibc1.status != 'queued')
		self.failIf(glibc2.status != 'done')
		self.failIf(distcc1.status != 'done')
		self.failIf(db1.status != 'cancelled')

	def testCancel(self):
		glibc1 = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now(), priority=1)
		glibc2 = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='3', status='building', timestamp=datetime.now(), priority=1, user=self.user)
		distcc1 = package.Package(name="distcc", arch=self.arch, pkgver='2.18.3', pkgrel='1', status='done', timestamp=datetime.now(), priority=1)
		db1 = package.Package(name='db', arch=self.arch, pkgver='4.3.28', pkgrel='1', status='cancelled', timestamp=datetime.now(), priority=1)

		glibc1.cancel()
		glibc2.cancel()
		distcc1.cancel()
		db1.cancel()

		self.failIf(glibc1.status != 'cancelled')
		self.failIf(glibc2.status != 'cancelled')
		self.failIf(distcc1.status != 'cancelled')
		self.failIf(db1.status != 'cancelled')

	def testUnbuild(self):
		glibc1 = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now(), priority=1)
		glibc2 = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='3', status='building', timestamp=datetime.now(), priority=1, user=self.user)
		distcc1 = package.Package(name="distcc", arch=self.arch, pkgver='2.18.3', pkgrel='1', status='done', timestamp=datetime.now(), priority=1)
		db1 = package.Package(name='db', arch=self.arch, pkgver='4.3.28', pkgrel='1', status='cancelled', timestamp=datetime.now(), priority=1)

		glibc1.unbuild()
		glibc2.unbuild()
		distcc1.unbuild()
		db1.unbuild()

		self.failIf(glibc1.status != 'queued')
		self.failIf(glibc2.status != 'queued')
		self.failIf(glibc2.user != None)
		self.failIf(distcc1.status != 'done')
		self.failIf(db1.status != 'cancelled')

	def testGetNextBuild(self):
		glibc1 = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now(), priority=1)
		glibc2 = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='3', status='building', timestamp=datetime.now(), priority=1, user=self.user)
		distcc1 = package.Package(name="distcc", arch=self.arch, pkgver='2.18.3', pkgrel='1', status='done', timestamp=datetime.now(), priority=1)
		db1 = package.Package(name='db', arch=self.arch, pkgver='4.3.28', pkgrel='1', status='cancelled', timestamp=datetime.now(), priority=1)

		self.failIf(package.getNextBuild(self.arch) != glibc1)

		glibc2.unbuild()
		self.failIf(package.getNextBuild(self.arch) != glibc1)

		glibc1.priority = 2
		glibc2.priority = 2
		distcc1.status = 'queued'
		db1.status = 'queued'
		db1.priority = 2
		self.failIf(package.getNextBuild(self.arch) == distcc1)

if __name__ == "__main__":
	unittest.main()
