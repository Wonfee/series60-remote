#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

import os
import sys
from distutils.core import setup

VERSION = '0.4.80'

applicationSis_Py14 = "series60-remote-py14.sis"
pythonSis_Py14 = "PythonForS60_1_4_5_3rdEd.sis"
applicationSis_Py20 = "series60-remote-py20.sis"
pythonSis_Py20 = "Python_2.0.0.sis"


textfiles = ['Changelog', 'HACKING', 'INSTALL', 'LICENSE', 'LICENSE.icons-oxygen',
         'README.icons-oxygen', 'TODO']
pys60 = 'PythonForS60_1_4_5_3rdEd.sis'
sisfiles = ['mobile/' + applicationSis_Py14, 'mobile/' + applicationSis_Py20, 'mobile/' + pythonSis_Py14, 'mobile/' + pythonSis_Py20]
desktopfile = 'pc/series60-remote.desktop'

extra = {}

src_dir = 'pc'
app_dir = 'series60_remote'

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Before distributing source call sibling setup to generate files.
if "sdist" in sys.argv[1:] and os.name == 'posix':
   if os.path.exists('mobile/create_package'):
      os.system("cd mobile && ./create_package && cd ..")
   #if os.path.exists('pc/generate-pro.sh') and os.path.exists('pc/mkpyqt.py'):
   #   os.system("cd pc && ./generate-pro.sh && ./mkpyqt.py && cd ..")
   if os.path.exists('pc/mkpyqt.py'):
      os.system("cd pc && ./mkpyqt.py && cd ..")

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk(src_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        s = fullsplit(dirpath)
        if s[0] == src_dir:
           s[0] = app_dir
        packages.append('.'.join(s))

dist = setup(name='series60-remote',
             version=VERSION,
             author='Lukas Hetzenecker',
             author_email='LuHe@gmx.at',
             url='http://series60-remote.sf.net',
             description='Series60-Remote is an application to manage your S60 mobile phone.',
             long_description="""Series60-Remote is an application for Linux and XP that manages Nokia mobile phones with the S60 operating system. The application provides the following features:
 - Message management
 - Contact management
 - File management
""",
             license='GPL2',
             packages=packages,
             package_dir={app_dir: src_dir},
             scripts=['series60-remote']
             )

# HACK! Copy extra files
if dist.have_run.get('install'):
   install = dist.get_command_obj('install')

   # Copy textfiles in site-package directory
   for file in textfiles:
      install.copy_file(file, os.path.join(install.install_lib, app_dir))

   # Copy .sis files on Unix-like systems to /usr/share/series60-remote, on Windows systems 
   # to PREFIX/site-packages/series60_remote/mobile
   if os.name == 'posix':
      dest = os.path.join(install.install_data, 'share', install.config_vars['dist_name'])
   else:
      dest = os.path.join(install.install_lib, app_dir)

   install.mkpath(dest + os.sep + 'mobile')
   for file in sisfiles:
      install.copy_file(file, dest + os.sep + 'mobile')

   # Copy export templates too
   install.mkpath(dest + os.sep + 'data')
   for root, dirs, files in os.walk('pc' + os.sep +'data'):
      # Ignore hidden dirs
      for dir in dirs:
         if dir.startswith("."):
            dirs.remove(dir)

      datadest = dest + os.sep + os.sep.join(root.split(os.sep)[1:]) # remove pc/ from directory
      install.mkpath(datadest) # create target directory
      for file in files:
         install.copy_file(root + os.sep + file, datadest)

   # Install desktop file on Linux
   if os.name == 'posix':
      dest = os.path.join(install.install_data, 'share', 'applications')
      install.mkpath(dest)
      install.copy_file(desktopfile, dest)

