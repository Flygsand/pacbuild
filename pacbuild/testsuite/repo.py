#!/usr/bin/env python

import unittest
import os
import warnings
import shutil

from pacbuild.cherry import repo, misc, connect
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

	def testRepoInstances(self):
		r = repo.Repo(name='current', absdir='%s/abs'%self.tmpdir, repodir='na', updatescript='na')
		instances = r.instances
		found = False
		for path, i in instances:
			if i.name == 'glibc':
				found = True
				self.failUnless(i.version=='2.3.4' and i.release=='2')
		self.failIf(not found)

	def testGetInstances(self):
		r = repo.Repo(name='current', absdir='%s/abs'%self.tmpdir, repodir='na', updatescript='na')
		arch = misc.Arch(name='i586')
		instances = repo.getInstances(r, arch)
		found = 0
		for i in instances:
			if i.packageArch.package.name == 'glibc':
				found += 1
				self.failUnless(i.pkgver=='2.3.4' and i.pkgrel=='2' and i.status == 'new' and i.packageArch.arch.name == 'i586')
			if i.packageArch.package.name == 'ruby':
				found += 1
				self.failUnless(i.pkgver=='1.8.2' and i.pkgrel=='4' and i.status == 'new' and i.packageArch.arch.name == 'i586')
		self.failUnless(found == 2)

if __name__ == "__main__":
	unittest.main()
