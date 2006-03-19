#!/usr/bin/env python
# 
# peach - Build server status script
# Copyright (C) 2005 Simo Leone <simo@archlinux.org>
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
sys.path.append('/etc')
import appleConfig
from pacbuild.apple import connect, package, misc
import cgi
import re

connect(appleConfig.database)
package.packagedir = appleConfig.Packagedir

def job_list():
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
<table cellpadding='5px' cellspacing='0px'>
<tr>
	<th>Package</th><th>Arch</th><th>Status</th><th>Log</th><th>Colorized Log</th><th>Package</th>
</tr>
'''
	
	for i in package.Package.select():
		print "<tr class='%s'>" % i.status
		print "<td>%s-%s-%s</td><td>%s</td><td>%s</td>"%(i.name,i.pkgver,i.pkgrel,i.arch.name,i.status)
		print "<td><a href='?action=log&id=%s'>Log</a></td>"%(i.id)
		print "<td><a href='?action=colorlog&id=%s'>Colorized Log</a></td>"%(i.id)
		print "<td><a href='?action=pkg&id=%s'>%s-%s-%s.pkg.tar.gz</a></td>"%(i.id,i.name,i.pkgver,i.pkgrel)
		print "</tr>"
	print "</table></body></html>"

def colorize(st):
	s = st[:]
	subs = [('\[1;32m', "<font color='green'>"), ('\[1;0m', "</font>"), ('\[1;1m', "<font style='font-weight: bold;'>"), ('\[1;33m', "<font color='darkyellow'>"), ("\[1;31m", "<font color='red'>")]
	for i, j in subs:
		s = re.sub(i, j, s)
	return s

def pkg_colorlog(id=0):
	print "Content-type: text/html\n"
	print "<pre>" + colorize(package.Package.get(id).log) + "</pre>"

def pkg_log(id=0):
	print "Content-type: text/plain\n"
	print package.Package.get(id).log

def pkg_file(id=0):
	pkg = package.Package.get(id)
	print "Content-type: application/x-compressed;"
	print "Content-Disposition: attachment; filename=\""+pkg.name+"-"+pkg.pkgver+"-"+pkg.pkgrel+".pkg.tar.gz\"\n"
	sys.stdout.write(pkg.binary)

def builder_list():
	print '''Content-type: text/html

<html>
<head>
<title>Apple Status - Build Machines</title>
</head>
<body>
<table cellpadding='5px' cellspacing='0px'>
<tr>
	<th>Owner</th><th>Identifier</th>
</tr>
'''
	for i in misc.Builder.select():
		print "<tr><td>%s</td><td>%s</td></tr>"%(i.user.name, i.ident)
	print "</table></body></html>"
	
def main():
	form = cgi.FieldStorage()
	if (form.has_key("action") and form.has_key("id")):
		if (form["action"].value == "log"):
			pkg_log(form["id"].value)
		elif (form["action"].value == "colorlog"):
			pkg_colorlog(form["id"].value)
		elif (form["action"].value == "pkg"):
			pkg_file(form["id"].value)
		else:
			job_list()
	elif (form.has_key("action") and form["action"].value == "builders"):
		builder_list()
	else:
		job_list()

main()
