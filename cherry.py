#!/usr/bin/env python
# 
# cherry - Main organizational daemon
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
from pacbuild.cherry import repo, misc, connect, package
from sqlobject import *

import cherryConfig

def handleArch(archList):
	ret = []
	for i in archList:
		try:
			arch = misc.Arch.byName(i)
		except main.SQLObjectNotFound:
			arch = misc.Arch(name=i)
		ret.append(arch)

def handleRepo(repoList):
	ret = []
	for i in repoList:
		try:
			r = repo.Repo.byName(i['name'])
			r.absdir = i['absdir']
			r.repodir = i['repodir']
			r.updatescript = i['updatescript']
		except main.SQLObjectNotFound:
			r = repo.Repo(name=i['name'], absdir=i['absdir'], repodir=i['repodir'], updatescript=i['updatescript'])
		ret.append(r)

def _main(argv=None):
	if argv is None:
		argv = sys.argv

	connect(cherryConfig.database)

	arches = handleArch(cherryConfig.arches)
	repos = handleRepo(cherryConfig.repos)

	for i in arches:
		for j in repos:
			instances = getInstances(j, i)
			if instances.canQueue():
				instances.queue()

	return 0

if __name__ == "__main__":
	sys.exit(_main())

