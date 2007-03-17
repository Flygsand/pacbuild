# appleConfig - Config file for apple daemon
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
import os, os.path
import datetime

DBdir = '/var/lib/pacbuild'
Packagedir = '/var/lib/pacbuild/apple'
if not os.path.isdir(DBdir):
	os.makedirs(DBdir)
if not os.path.isdir(Packagedir):
	os.makedirs(Packagedir)
database = connectionForURI("sqlite://%s/apple.db"%DBdir)

stalePackageTimeout = datetime.timedelta(days=2)
