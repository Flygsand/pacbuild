#!/usr/bin/env python
# 
# strawberry - Main client daemon
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

import sys
#sys.path.append('/etc')
import xmlrpclib
import socket
import threading
import os, os.path
import re
import datetime, time
import shutil
# next two imports are for OptionParser
from copy import copy
from optparse import Option, OptionValueError, OptionParser
from syslog import *
from md5 import md5

from sqlobject import *

defaultConfig = "/etc/strawberryConfig.py"

#import strawberryConfig
strawberryConfig = {}

done = False

pacmanConfigs = []

UMASK = 0

WORKDIR = "/"

MAXFD = 1024

if (hasattr(os, "devnull")):
   REDIRECT_TO = os.devnull
else:
   REDIRECT_TO = "/dev/null"

def createDaemon():
	"""Detach a process from the controlling terminal and run it in the
	background as a daemon.
	"""

	try:
		pid = os.fork()
	except OSError, e:
		raise Exception, "%s [%d]" % (e.strerror, e.errno)

	if (pid == 0):	# The first child.
		os.setsid()

		try:
			pid = os.fork()	# Fork a second child.
		except OSError, e:
			raise Exception, "%s [%d]" % (e.strerror, e.errno)

		if (pid == 0):	# The second child.
			os.chdir(WORKDIR)
			os.umask(UMASK)
		else:
			os._exit(0)	# Exit parent (the first child) of the second child.
	else:
		os._exit(0)	# Exit parent of the first child.

	import resource		# Resource usage information.
	maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
	if (maxfd == resource.RLIM_INFINITY):
		maxfd = MAXFD
  
	# Iterate through and close all file descriptors.
	for fd in range(0, maxfd):
		try:
			os.close(fd)
		except OSError:	# ERROR, fd wasn't open to begin with (ignored)
			pass

	os.open(REDIRECT_TO, os.O_RDWR)	# standard input (0)

	os.dup2(0, 1)			# standard output (1)
	os.dup2(0, 2)			# standard error (2)

	return(0)

class PacmanConf:
	def __init__(self, name, arch, data):
		self.name = name
		self.arch = arch
		self.data = data
	def md5sum(self):
		return md5(self.data).hexdigest()

class Build(SQLObject):
	cherryId = IntCol()
	sourceFilename = StringCol()
	source = StringCol()
	pacmanConfig = StringCol()
	pacmanConfigMd5 = StringCol()

	def _set_source(self, value):
		if value is not None:
			self._SO_set_source(value.encode('base64').replace('\n',''))
		else:
			self._SO_set_source(None)
	def _get_source(self):
		if self._SO_get_source() == None:
			return None
		else:
			return self._SO_get_source().decode('base64')

class Waka(threading.Thread):
	def __init__(self, build, buildDir, currentUrl, extraUrl, chrootImage=None, **other):
		threading.Thread.__init__(self, *other)
		self.buildDir = buildDir
		self.currentUrl = currentUrl
		self.extraUrl = extraUrl
		self.build = build
		self.filename = build.sourceFilename
		self.chrootImage = chrootImage
		self.sourcePkg = os.path.join(self.buildDir, self.filename)
		self.makeWakaConf()
		self.makeSourceFile(build.source)

	def makeSourceFile(self, fileData):
		file = open(self.sourcePkg, "wb")
		file.write(fileData)
		file.close()

	def makeWakaConf(self):
		if (not os.path.isdir(self.buildDir)):
			os.makedirs(self.buildDir)
		self.mkchrootPath = os.path.join(self.buildDir,"mkchroot.conf")
		self.pacmanconfPath = os.path.join(self.buildDir,"pacman.conf")
		conf = open(self.mkchrootPath, "w")
		conf.write('WAKA_ROOT_DIR="%s"\n' % self.buildDir)
		conf.write('WAKA_CHROOT_DIR="chroot"\n')
		conf.write('QUIKINST_LOCATION="/usr/share/waka/quickinst"\n')
		conf.write('PACKAGE_MIRROR_CURRENT="%s"\n' % self.currentUrl)
		conf.write('PACKAGE_MIRROR_EXTRA="%s"\n' % self.extraUrl)
		conf.write('DEFAULT_PKGDEST=${WAKA_ROOT_DIR}/\n')
		conf.write('DEFAULT_KERNEL=kernel26\n')
		conf.close()
		thisconf = getPacmanConfig(self.build.pacmanConfig, strawberryConfig['arch'], self.build.pacmanConfigMd5)
		if not thisconf:
			syslog(LOG_ERR, "Don't have pacman.conf for %s, using mkchroot defaults"%(self.filename))
			self.pacmanconfPath = ""
		else:
			pacmanconf = open(self.pacmanconfPath, "w")
			pacmanconf.write(thisconf.data)
			pacmanconf.close()

	def run(self):
		global done
		syslog(LOG_INFO, "Beginning build of %s"%(self.build.sourceFilename))
		addargs = ""
		if self.chrootImage:
			addargs = "-i %s" % self.chrootImage
		if self.pacmanconfPath:
			addargs = addargs + " -p %s" % self.pacmanconfPath
		ret = os.system("/usr/bin/mkchroot -o %s %s %s"%(self.mkchrootPath, addargs, self.sourcePkg))
		if ret != 0:
			# There was an error building
			# Log something so the admin can figure out what's up
			# Tell apple
			syslog(LOG_ERR, "Error building %s"%(self.build.sourceFilename))
			shutil.rmtree(self.buildDir)
			done = True
		# Do the post build stuff
		self.binaryPkg = re.sub('\.src\.tar\.gz$', '.pkg.tar.gz', self.sourcePkg)
		self.logFile = re.sub('\.src\.tar\.gz$', '.makepkg.log', self.sourcePkg)

		if os.path.isfile(self.binaryPkg):
			binary = open(self.binaryPkg).read()
		else:
			binary = False
		log = open(self.logFile).read()
		if ">>>>>>>>>> Error building <<<<<<<<<<" in log:
			syslog(LOG_ERR, "Found error in log building %s"%(self.build.sourceFilename))
		sendBuild(self.build, binary, log)
		shutil.rmtree(self.buildDir)

class Heartbeat(threading.Thread):
	def __init__(self, **other):
		threading.Thread.__init__(self, *other)
		self.pulse = 3600
	def run(self):
		while True:
			try:
				server = xmlrpclib.ServerProxy(strawberryConfig['url'])
				server.beat(strawberryConfig['user'], strawberryConfig['password'], strawberryConfig['ident'], strawberryConfig['arch'])
			except (xmlrpclib.ProtocolError, xmlrpclib.Fault, socket.error):
				syslog(LOG_ERR, "Unable to send heartbeat")
				pass
			time.sleep(self.pulse)

def canBuild():
	return Build.select().count() < strawberryConfig['maxBuilds']

def getPacmanConfig(name, arch, md5):
	global pacmanConfigs
	for i in pacmanConfigs:
		if i.name == name and i.arch == arch and i.md5sum() == md5:
			return i
	server = xmlrpclib.ServerProxy(strawberryConfig['url'])
	try:
		config = server.getPacmanConfig(strawberryConfig['user'], strawberryConfig['password'], arch, name)
		if config is not None and config is not False:
			for i in pacmanConfigs:
				if i.name == name and i.arch == arch:
					pacmanConfigs.remove(i)
			config = PacmanConf(config[0], config[1], config[2])
			pacmanConfigs.append(config)
			syslog(LOG_INFO, "Got pacman config \"%s\" from %s"%(name, strawberryConfig['url']))
			return config
		return None
	except (xmlrpclib.ProtocolError, xmlrpclib.Fault, socket.error):
		syslog(LOG_ERR, "Failed to retrieve pacman config \"%s\" from %s"%(name, strawberryConfig['url']))
		return None


def getNextBuild():
	try:
		server = xmlrpclib.ServerProxy(strawberryConfig['url'])
		build = server.getNextBuild(strawberryConfig['user'], strawberryConfig['password'], strawberryConfig['ident'], strawberryConfig['arch'])
		if build is not None and build is not False:
			syslog(LOG_INFO, "Got %s from %s for next build"%(build[1], strawberryConfig['url']))
			return Build(cherryId=build[0], sourceFilename=build[1], source=build[2].decode('base64'),
						pacmanConfig=build[3], pacmanConfigMd5=build[4])
		return None
	except (xmlrpclib.ProtocolError, xmlrpclib.Fault, socket.error):
		syslog(LOG_ERR, "Couldn't fetch next build from %s"%(strawberryConfig['url']))
		return None

def sendBuild(build, binary, log):
	try:
		server = xmlrpclib.ServerProxy(strawberryConfig['url'])
		if binary is not False:
			bin64 = binary.encode('base64')
		else:
			bin64 = False
		server.submitBuild(strawberryConfig['user'], strawberryConfig['password'], build.cherryId, bin64, log.encode('base64'))
	except (xmlrpclib.ProtocolError, xmlrpclib.Fault, socket.error):
		syslog(LOG_ERR, "Couldn't upload %s to %s"%(build.sourceFilename, strawberryConfig['url']))
		return False
	
	syslog(LOG_INFO, "Uploaded %s to %s"%(build.sourceFilename, strawberryConfig['url']))

def mkchroot(confpath, imgpath):
	os.system("/usr/bin/mkchroot -o %s -c %s" % (confpath, imgpath))

def check_filename(option, opt, value):
	if os.path.isfile(value):
	    return os.path.abspath(value)
	else:
		raise OptionValueError("option %s: invalid filename" % opt)

class ExtendOption(Option):
	TYPES = Option.TYPES + ("filename",)
	TYPE_CHECKER = copy(Option.TYPE_CHECKER)
	TYPE_CHECKER["filename"] = check_filename

def createOptParser():
	usage = "usage: %prog [options]"
	description = "<fill in description here>"
	parser = OptionParser(usage = usage, description = description,
	                      option_class = ExtendOption)

	parser.add_option("-c", "--config", action = "store", type = "filename",
	                  dest = "config", default = defaultConfig,
	                  help = "use a different config than default (%s)" % defaultConfig)
	parser.add_option("-d", "--daemon", action = "store_true",
	                  dest = "daemon", default = False,
	                  help = "run as a daemon")
	return parser


def _main(argv=None):
	if argv is None:
		argv = sys.argv

	# instantiate parser object and set it loose
	parser = createOptParser()
	(opts, args) = parser.parse_args()

	# use results of parse_args to set things up
	configPath = opts.config
	if opts.daemon:
		createDaemon()
		pid = open('/var/run/strawberry.pid', 'w')
		pid.write('%s\n' % os.getpid())
		pid.close()

	openlog("strawberry", LOG_PID, LOG_USER)
	syslog(LOG_INFO, "Started strawberry")

	execfile(configPath, strawberryConfig, strawberryConfig)

	Build.setConnection(strawberryConfig['database'])
	Build.createTable(ifNotExists=True)

	# Kick off our heartbeat thread
	heartbeat = Heartbeat()
	heartbeat.start()

	threads = []

	# Start any builds that never actually finished last time
	for i in Build.select():
		# Clean up any half-built versions
		# We're starting fresh, after all
		if os.path.isdir(os.path.join(strawberryConfig['buildDir'], i.sourceFilename)):
			shutil.rmtree(os.path.join(strawberryConfig['buildDir'], i.sourceFilename))

		otherargs = {}
		if strawberryConfig.has_key('chrootImage'):
			otherargs['chrootImage'] = strawberryConfig['chrootImage']
		syslog(LOG_INFO, "Resuming unfinished build - %s"%(i.sourceFilename))
		waka = Waka(i, os.path.join(strawberryConfig['buildDir'], i.sourceFilename), strawberryConfig['currentUrl'], strawberryConfig['extraUrl'], **otherargs)
		waka.start()
		threads.append(waka)

	while not done:
		for i, v in enumerate(threads):
			if not v.isAlive():
				print "Cleaning up from thread"
				Build.delete(v.build.id)
				del threads[i]
		if canBuild():
			if strawberryConfig.has_key('chrootImage'):
				# this is basically verbatim from above, but we need more
				# abstraction before it can be rewritten as non-duplicate code
				confpath = "/tmp/mkchroot_xxx.conf"
				conf = open(confpath, "w")
				conf.write('WAKA_ROOT_DIR="%s"\n' % strawberryConfig['buildDir'])
				conf.write('WAKA_CHROOT_DIR="chroot"\n')
				conf.write('QUIKINST_LOCATION="/usr/share/waka/quickinst"\n')
				conf.write('PACKAGE_MIRROR_CURRENT="%s"\n' % strawberryConfig['currentUrl'])
				conf.write('PACKAGE_MIRROR_EXTRA="%s"\n' % strawberryConfig['extraUrl'])
				conf.write('DEFAULT_PKGDEST=${WAKA_ROOT_DIR}/\n')
				conf.write('DEFAULT_KERNEL=kernel26\n')
				conf.close()

				if os.path.isfile(strawberryConfig['chrootImage']):
					stat = os.stat(strawberryConfig['chrootImage'])
					today = datetime.datetime.now()
					mtime = datetime.datetime(*time.localtime(stat.st_mtime)[:7])
					staleDiff = datetime.timedelta(days=14)
					if today - mtime >= staleDiff:
						mkchroot(confpath, strawberryConfig['chrootImage'])
				else:
					mkchroot(confpath, strawberryConfig['chrootImage'])
			build = getNextBuild()
			if build is not None and build is not False:
				print "Got a new build: %s" % build.sourceFilename
				
				# This is where you'd set up waka
				otherargs = {}
				if strawberryConfig.has_key('chrootImage'):
					otherargs['chrootImage'] = strawberryConfig['chrootImage']
				waka = Waka(build, os.path.join(strawberryConfig['buildDir'], build.sourceFilename), strawberryConfig['currentUrl'], strawberryConfig['extraUrl'], **otherargs)
				waka.start()
				threads.append(waka)
		time.sleep(strawberryConfig['sleeptime'])
			

if __name__ == "__main__":
	sys.exit(_main())
