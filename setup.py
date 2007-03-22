#!/usr/bin/env python
from distutils.core import setup

DATAFILES = [('/usr/share/waka', ['waka/functions', 'waka/build', 'waka/quickinst']), ('/etc', ['waka/mkchroot.conf', 'strawberryConfig.py', 'appleConfig.py']), ('/usr/share/pacbuild', ['peach.py'])]

setup(name="pacbuild",
      version="0.4",
      description="Automated package builder",
      author="Jason Chu",
      author_email="jason@archlinux.org",
      packages=["pacbuild", "pacbuild/apple"],
      scripts=["apple.py", "strawberry.py", "waka/mkchroot", "getBuild.py", "queuepackage.sh", "uploadPkgbuild.py", "mkpkgsrc", "queuepkg"],
      data_files=DATAFILES)
