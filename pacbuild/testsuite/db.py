#!/usr/bin/env python

import unittest
import os
import warnings
import shutil

from pacbuild.cherry import misc, package, repo, connect
from sqlobject import *
from datetime import datetime

class ConnectTest(unittest.TestCase):
	def setUp(self):
		warnings.filterwarnings("ignore", "tmpnam", RuntimeWarning, __name__)
		self.tmpdir = os.tmpnam()
		os.makedirs(self.tmpdir)

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def testConnect(self):
		conn = connectionForURI("sqlite://%s/test.db"%self.tmpdir)
		connect(conn)
		self.failUnless(os.path.isfile("%s/test.db"%self.tmpdir))

class DbTest(unittest.TestCase):
	def setUp(self):
		warnings.filterwarnings("ignore", "tmpnam", RuntimeWarning, __name__)
		self.tmpdir = os.tmpnam()
		os.makedirs(self.tmpdir)
		conn = connectionForURI("sqlite://%s/test.db"%self.tmpdir)
		connect(conn)

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def testArch(self):
		arch = misc.Arch(name='i586')
		self.failUnless(misc.Arch.byName('i586'))
		try:
			misc.Arch.byName('no exist')
		except main.SQLObjectNotFound:
			excepted = True
		self.failUnless(excepted)

	def testUser(self):
		arch = misc.Arch(name='i586')
		user = misc.User(name='jchu', password='a', email='jason@archlinux.org', arch=arch)
		newUser = misc.User.byName('jchu')
		self.failUnless(user==newUser)

	def testRepo(self):
		r = repo.Repo(name='current', absdir='/something', repodir='/repo', updatescript='/script')
		self.failUnless(repo.Repo.byName('current'))

	# Include package tests

if __name__ == "__main__":
	unittest.main()
