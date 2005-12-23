#!/usr/bin/env python

import unittest
import os
import warnings
import shutil

from pacbuild.apple import package, misc, connect, rpc
from sqlobject import *
from datetime import datetime

class RpcServerTest(unittest.TestCase):
	def setUp(self):
		warnings.filterwarnings("ignore", "tmpnam", RuntimeWarning, __name__)
		self.tmpdir = os.tmpnam()
		os.makedirs(self.tmpdir)
		conn = connectionForURI("sqlite://%s/test.db"%self.tmpdir)
		connect(conn)
		self.arch = misc.Arch(name='i586') 
		self.user = misc.User(name='jchu', password='a', email='jchu@xentac.net', arch=self.arch, type='builder')
		self.submitter = misc.User(name='jchu2', password='a', email='jchu@xentac.net', arch=self.arch, type='submitter')
		shutil.copytree('pacbuild/testsuite/testAbs', '%s/abs'%self.tmpdir)

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def testGetNextBuild(self):
		glibc = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now(), source='', priority=1)
		distcc = package.Package(name="distcc", arch=self.arch, pkgver='2.18.3', pkgrel='1', status='building', timestamp=datetime.now(), source='', priority=1)
		db1 = package.Package(name='db', arch=self.arch, pkgver='4.3.28', pkgrel='1', status='cancelled', timestamp=datetime.now(), source='', priority=1)
		db2 = package.Package(name='db', arch=self.arch, pkgver='4.3.27', pkgrel='1', status='queued', timestamp=datetime.now(), source='', priority=1)

		daemon = rpc.RPCDaemon()
		nextBuild = daemon.getNextBuild('jchu', 'a')
		self.failUnless(nextBuild[0] == glibc.id)
		self.failUnless(glibc.status == 'building')

		nextBuild = daemon.getNextBuild('jchu', 'a')
		self.failUnless(nextBuild[0] == db2.id)
		self.failUnless(db2.status == 'building')

		nextBuild = daemon.getNextBuild('jchu', 'a')
		self.failUnless(nextBuild == None)

	def testSubmitBuild(self):
		glibc = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now(), source='', priority=1)
		distcc = package.Package(name="distcc", arch=self.arch, pkgver='2.18.3', pkgrel='1', status='building', timestamp=datetime.now(), source='', priority=1)
		db1 = package.Package(name='db', arch=self.arch, pkgver='4.3.28', pkgrel='1', status='cancelled', timestamp=datetime.now(), source='', priority=1)
		db2 = package.Package(name='db', arch=self.arch, pkgver='4.3.27', pkgrel='1', status='queued', timestamp=datetime.now(), source='', priority=1)

		daemon = rpc.RPCDaemon()
		nextBuild = daemon.getNextBuild('jchu', 'a')
		res = daemon.submitBuild('jchu', 'b', nextBuild[0], 'built'.encode('base64'), 'this is a log'.encode('base64'))
		self.failUnless(res == False)

		res = daemon.submitBuild('jchu', 'a', nextBuild[0], 'built'.encode('base64'), 'this is a log'.encode('base64'))
		self.failUnless(res == True)
		self.failUnless(glibc.binary == 'built')
		self.failUnless(glibc.log == 'this is a log')

		res = daemon.submitBuild('jchu', 'a', distcc.id, 'built'.encode('base64'), 'this is a log')
		self.failUnless(res == False)

	def testSubmitPKGBUILD(self):
		glibc = package.Package(name="glibc", arch=self.arch, pkgver='2.3.4', pkgrel='2', status='queued', timestamp=datetime.now(), source='', priority=1)
		daemon = rpc.RPCDaemon()
		res = daemon.submitPKGBUILD('jchu2', 'b', 'glibc', '2.3.4', '2', 1, 'some source'.encode('base64'))
		self.failUnless(res == False)

		daemon = rpc.RPCDaemon()
		res = daemon.submitPKGBUILD('jchu', 'a', 'glibc', '2.3.4', '2', 1, 'some source'.encode('base64'))
		self.failUnless(res == False)

		daemon = rpc.RPCDaemon()
		res = daemon.submitPKGBUILD('jchu2', 'a', 'glibc', '2.3.4', '2', 1, 'some source'.encode('base64'))
		self.failIf(res == False)
		glibc = package.Package.get(res)
		self.failUnless(glibc.name == 'glibc')
		self.failUnless(glibc.arch == self.arch)
		self.failUnless(glibc.pkgver == '2.3.4')
		self.failUnless(glibc.pkgrel == '2')
		self.failUnless(glibc.status == 'queued')
		self.failUnless(glibc.source == 'some source')
		self.failUnless(glibc.priority == 1)

if __name__ == "__main__":
	unittest.main()
