# 
# strawberryConfig - Config file for strawberry daemon
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

from sqlobject import *
from socket import gethostname
import os, os.path

import platform

arch = platform.machine()

user = ''
password = ''

import md5
md5obj = md5.new()
md5obj.update(password)
password = md5obj.hexdigest()

url = 'http://localhost:8888'
# Each of your build machines should have a unique ident
# Defaults to hostname
ident = gethostname()

buildDir = '/mnt/temp/wakachroot'

maxBuilds = 1

DBdir = '/var/lib/pacbuild'

if not os.path.isdir(DBdir):
	os.makedirs(DBdir)
database = connectionForURI("sqlite://%s/strawberry.db"%DBdir)

# Comment out if you want the chroot built every time
chrootImage = '%s/strawberry.img' % DBdir

sleeptime = 600

currentUrl = "ftp://ftp.archlinux.org/current/os/${CARCH}"
extraUrl = "ftp://ftp.archlinux.org/extra/os/${CARCH}"
