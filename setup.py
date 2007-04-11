#!/usr/bin/env python
from distutils.core import setup

DATAFILES = [('/usr/share/waka', ['waka/build', 'waka/quickinst']),
             ('/etc/pacbuild', ['waka/mkchroot.conf', 'strawberry.conf', 'apple.conf']),
             ('/usr/share/pacbuild', ['peach.py'])]

setup(name="pacbuild",
      version="0.4",
      description="Automated package builder",
      author="Jason Chu",
      author_email="jason@archlinux.org",
      packages=["pacbuild", "pacbuild/apple"],
      scripts=["apple", "strawberry", "waka/mkchroot", "getBuild.py", "mkpkgsrc", "queuepkg"],
      data_files=DATAFILES)
