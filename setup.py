#!/usr/bin/env python
from distutils.core import setup

DATAFILES = [('/usr/share/waka', ['waka/functions', 'waka/build', 'waka/quickinst']), ('/etc', ['waka/mkchroot.conf'])]

setup(name="pacbuild",
      version="0.1",
      description="Automated package builder",
      author="Jason Chu",
      author_email="jason@archlinux.org",
      packages=["pacbuild"],
      scripts=["cherry.py", "strawberry.py", "waka/mkchroot"],
      data_files=DATAFILES)
