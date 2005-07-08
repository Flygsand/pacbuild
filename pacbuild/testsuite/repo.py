#!/usr/bin/env python

import unittest
import os
import warnings
import shutil

from pacbuild.cherry import repo, connect
from sqlobject import *
from datetime import datetime

class RepoTest(unittest.TestCase):
	def setUp(self):
		warnings.filterwarnings("ignore", "tmpnam", RuntimeWarning, __name__)
		self.tmpdir = os.tmpnam()
		os.makedirs(self.tmpdir)
		conn = connectionForURI("sqlite://%s/test.db"%self.tmpdir)
		connect(conn)
		shutil.copytree('pacbuild/testsuite/testAbs', '%s/abs'%self.tmpdir)

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def testGetInstances(self):
		pass

	def testCategories(self):
		r = repo.Repo(name='current', absdir='%s/abs'%self.tmpdir, repodir='na', updatescript='na')
		repoCats = set(r.categories)
		testCats = set(('base', 'devel'))
		self.failUnless(repoCats - testCats == set([]))

	def testPkgbuilds(self):
		r = repo.Repo(name='current', absdir='%s/abs'%self.tmpdir, repodir='na', updatescript='na')
		repoPkgbuilds = set(r.pkgbuilds)
		testPkgbuilds = set(('db', 'dcron', 'devfsd', 'dhcpcd', 'diffutils', 'file', 'filesystem', 'findutils', 'flex', 'gcc', 'gdbm', 'gettext', 'glibc', 'grep', 'groff', 'grub', 'gzip', 'hotplug', 'initscripts', 'iputils', 'kbd', 'openssl', 'tar', 'tcp_wrappers', 'vim', 'zlib', 'arch', 'distcc', 'gc', 'gdb', 'mod_python', 'ruby', 'strace', 'unixodbc'))
		self.failUnless(repoPkgbuilds - testPkgbuilds == set([]))

	def testInstances(self):
		r = repo.Repo(name='current', absdir='%s/abs'%self.tmpdir, repodir='na', updatescript='na')
		instances = r.instances
		

if __name__ == "__main__":
	unittest.main()
