#!/usr/bin/env python
# 
#   peach - Build server status script
#   Copyright (C) 2005-2007 Simo Leone <simo@archlinux.org>
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
import os, os.path
import cgi
import re
from ConfigParser import SafeConfigParser
from pacbuild.apple import connect, package, misc
from sqlobject import *

# default config file
# TODO peach currently only works with the default config file
defaultConfig = "/etc/pacbuild/apple.conf"
configpath = defaultConfig

# parse the config file
cfgparser = SafeConfigParser()
cfgparser.read(configpath)

# store values from config file
packagedir = cfgparser.get("options","packagedir")
dbdir = cfgparser.get("options","dbdir")

# check the config file paths
if not os.path.isdir(packagedir):
	raise StandardError("%s: invalid package directory %s" % (configpath, packagedir))
if not os.path.isdir(dbdir):
	raise StandardError("%s: invalid database directory %s" % (configpath, dbdir))

# establish and connect to the database
database = connectionForURI("sqlite://%s/apple.db" % dbdir)
connect(database)

# set the package directory
package.packagedir = packagedir

def job_list(all=False, archid=None):
	print '''Content-type: text/html

<html>
<head>
<title>Apple Status - Job Queue</title>
<style type="text/css">
<!--

.error {
	background-color: red;
}
.done {
	background-color: #5FFB17;
}
.building {
	background-color: #9AFEFF;
}


-->
</style>
</head>
<body>
<a href='?action=arches'>Architectures</a> <a href='?action=builders'>Build Machines</a> <a href='?action=conflist'>Pacman Configurations</a><br>
'''
	if all:
		print '<a href="?">Most recent 20 builds</a>'
	else:
		print '<a href="?action=all">All builds</a>'

	print '''<hr />
<table cellpadding='5px' cellspacing='0px'>
<tr>
	<th>ID</th><th>Package</th><th>Arch</th><th>Status</th><th>Log</th><th>Colorized Log</th><th>Package</th>
</tr>
'''
	
	where = None
	if archid != None:
		where = package.Package.q.archID == int(archid)
	if all:
		packages = package.Package.select(where, orderBy="-timestamp")
	else:
		packages = package.Package.select(where, orderBy="-timestamp")[:20]

	for i in packages:
		print "<tr class='%s'>" % i.status
		print "<td>%s</td>"%(i.id)
		print "<td>%s-%s-%s</td><td>%s</td><td>%s</td>"%(i.name,i.pkgver,i.pkgrel,i.arch.name,i.status)
		print "<td><a href='?action=log&id=%s'>Log</a></td>"%(i.id)
		print "<td><a href='?action=colorlog&id=%s'>Colorized Log</a></td>"%(i.id)
		# if build is not 'done', don't print a link
		if i.status == 'done':
			print "<td><a href='?action=pkg&id=%s'>%s-%s-%s-%s.pkg.tar.gz</a></td>"%(i.id,i.name,i.pkgver,i.pkgrel,i.arch.name)
		else:
			print "<td>%s-%s-%s-%s.pkg.tar.gz</td>"%(i.name,i.pkgver,i.pkgrel,i.arch.name)
		print "</tr>"
	print "</table></body></html>"

def colorize(st):
	s = st[:]
	subs = [('\[1;32m', "<font color='green'>"), ('\[1;0m', "</font>"), ('\[1;1m', "<font style='font-weight: bold;'>"), ('\[1;33m', "<font color='darkyellow'>"), ("\[1;31m", "<font color='red'>")]
	for i, j in subs:
		s = re.sub(i, j, s)
	return s

def strip_colors(st):
	s = st[:]
	subs = [('\[1;32m', ""), ('\[1;0m', ""), ('\[1;1m', ""), ('\[1;33m', ""), ("\[1;31m", "")]
	for i, j in subs:
		s = re.sub(i, j, s)
	return s

def pkg_colorlog(id=0):
	print "Content-type: text/html\n"
	print "<pre>" + colorize(package.Package.get(id).log) + "</pre>"

def pkg_log(id=0):
	print "Content-type: text/plain\n"
	print strip_colors(package.Package.get(id).log)

def pkg_file(id=0):
	pkg = package.Package.get(id)
	print "Content-type: application/x-compressed;"
	print "Content-Disposition: attachment; filename=\""+pkg.name+"-"+pkg.pkgver+"-"+pkg.pkgrel+"-"+pkg.arch.name+".pkg.tar.gz\"\n"
	sys.stdout.write(pkg.binary)

def arch_list():
	print '''Content-type: text/html

<html>
<head>
<title>Apple Status - Architectures</title>
</head>
<body>
<table cellpadding='5px' cellspacing='0px'>
<tr>
	<th>Architecture</th>
</tr>
'''
	for i in misc.Arch.select():
		print "<tr><td><a href='?action=list&arch=%s'>%s</a></td></tr>"%(i.id, i.name)
	print "</table></body></html>"
	
def builder_list():
	print '''Content-type: text/html

<html>
<head>
<title>Apple Status - Build Machines</title>
</head>
<body>
<table cellpadding='5px' cellspacing='0px'>
<tr>
	<th>Owner</th><th>Identifier</th><th>Architecture</th>
</tr>
'''
	for i in misc.Builder.select():
		print "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%(i.user.name, i.ident, i.arch.name)
	print "</table></body></html>"
	
def pacConf_list():
	print '''Content-type: text/html

<html>
<head>
<title>Apple Status - Available Pacman Configurations</title>
</head>
<body>
'''
	for i in misc.PacmanConf.select():
		print "<a href='?action=pacmanconfig&id=%s'>%s</a> (%s)<br />"%(i.id, i.name, i.arch.name)
	print "</body></html>"

def pacman_config(id=0):
	print "Content-type: text/plain\n"
	print misc.PacmanConf.get(id).data

def main():
	form = cgi.FieldStorage()
	if form.has_key("action") and form.has_key("id"):
		if form["action"].value == "log":
			pkg_log(form["id"].value)
		elif form["action"].value == "colorlog":
			pkg_colorlog(form["id"].value)
		elif form["action"].value == "pkg":
			pkg_file(form["id"].value)
		elif form["action"].value == "pacmanconfig":
			pacman_config(form["id"].value)
		else:
			job_list()
	elif form.has_key("action") and form["action"].value == "arches":
		arch_list()
	elif form.has_key("action") and form["action"].value == "builders":
		builder_list()
	elif form.has_key("action") and form["action"].value == "conflist":
		pacConf_list()
	elif form.has_key("action") and form["action"].value == "all":
		job_list(all=True)
	elif form.has_key("action") and form["action"].value == "list" and form.has_key("arch"):
		job_list(all=True, archid=form['arch'].value)
	else:
		job_list()

main()
