#!/usr/bin/env python

import unittest
import os
import warnings
import shutil

from pacbuild.cherry import repo, package, misc, connect, rpc
from sqlobject import *
from datetime import datetime

class RpcServerTest(unittest.TestCase):
	def setUp(self):
		warnings.filterwarnings("ignore", "tmpnam", RuntimeWarning, __name__)
		self.tmpdir = os.tmpnam()
		os.makedirs(self.tmpdir)
		conn = connectionForURI("sqlite://%s/test.db"%self.tmpdir)
		connect(conn)
		self.repo = repo.Repo(name='current', absdir='%s/abs'%self.tmpdir, repodir='na', updatescript='na')
		self.arch = misc.Arch(name='i586') 
		self.user = misc.User(name='jchu', password='a', email='jchu@xentac.net', arch=self.arch)
		shutil.copytree('pacbuild/testsuite/testAbs', '%s/abs'%self.tmpdir)

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def testGetNextBuild(self):
		glibc = package.Package(name="glibc", repo=self.repo)
		distcc = package.Package(name="distcc", repo=self.repo)
		db = package.Package(name='db', repo=self.repo)

		glibcArch = package.PackageArch(applies=1, arch=self.arch, package=glibc)
		distccArch = package.PackageArch(applies=1, arch=self.arch, package=distcc)
		dbArch = package.PackageArch(applies=1, arch=self.arch, package=db)

		glibcInstance1 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now(), source='')

		distccInstance = package.PackageInstance(packageArch=distccArch, pkgver='2.18.3', pkgrel='1', status='new', timestamp=datetime.now(), source='')

		dbInstance1 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.28', pkgrel='1', status='build-error', timestamp=datetime.now(), source='')
		dbInstance2 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.27', pkgrel='1', status='queued', timestamp=datetime.now(), source='')

		daemon = rpc.RPCDaemon()
		nextBuild = daemon.getNextBuild('jchu', 'a')
		self.failUnless(nextBuild[0] == glibcInstance1.id)
		self.failUnless(glibcInstance1.status == 'building')

		nextBuild = daemon.getNextBuild('jchu', 'a')
		self.failUnless(nextBuild[0] == dbInstance2.id)
		self.failUnless(dbInstance2.status == 'building')

		nextBuild = daemon.getNextBuild('jchu', 'a')
		self.failUnless(nextBuild == None)

	def testSubmitBuild(self):
		glibc = package.Package(name="glibc", repo=self.repo)
		distcc = package.Package(name="distcc", repo=self.repo)
		db = package.Package(name='db', repo=self.repo)

		glibcArch = package.PackageArch(applies=1, arch=self.arch, package=glibc)
		distccArch = package.PackageArch(applies=1, arch=self.arch, package=distcc)
		dbArch = package.PackageArch(applies=1, arch=self.arch, package=db)

		glibcInstance1 = package.PackageInstance(packageArch=glibcArch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now(), source='')

		distccInstance = package.PackageInstance(packageArch=distccArch, pkgver='2.18.3', pkgrel='1', status='new', timestamp=datetime.now(), source='')

		dbInstance1 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.28', pkgrel='1', status='build-error', timestamp=datetime.now(), source='')
		dbInstance2 = package.PackageInstance(packageArch=dbArch, pkgver='4.3.27', pkgrel='1', status='queued', timestamp=datetime.now(), source='')

		daemon = rpc.RPCDaemon()
		nextBuild = daemon.getNextBuild('jchu', 'a')
		res = daemon.submitBuild('jchu', 'b', nextBuild[0], 'built'.encode('base64'), 'this is a log')
		self.failUnless(res == False)

		res = daemon.submitBuild('jchu', 'a', nextBuild[0], 'built'.encode('base64'), 'this is a log')
		self.failUnless(res == True)
		self.failUnless(glibcInstance1.binary == 'built')
		self.failUnless(glibcInstance1.log == 'this is a log')

		res = daemon.submitBuild('jchu', 'a', distccInstance.id, 'built'.encode('base64'), 'this is a log')
		self.failUnless(res == False)

if __name__ == "__main__":
	unittest.main()
