#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
import shutil
from setuptools import setup
from distutils.dir_util import copy_tree
from py2app.build_app import py2app as _py2app

NAME = 'Series60-Remote'
VERSION = '0.4.80'
URL = 'http://series60-remote.sourceforge.net'

PKGMGR = '/Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker'
DYNLIB = '/opt/local/lib/'

QT_INCLUDES = ['QtCore', 'QtGui', 'QtSql', 'PyQt4.QtXml']
QT_EXCLUDES = ['QtDesigner', 'QtNetwork', 'QtOpenGL', 'QtScript', 'QtTest', 'QtWebKit', 'phonon']

APP_PATH = os.sep.join(os.path.realpath(os.curdir).split(os.sep)[:-3]) # e.g. /Users/lukas/series60-remote/trunk/pc/ 

class py2app(_py2app):
    """py2app extensions to delete Qt debug libs."""
    # Add no-plugins option
    _py2app.user_options.append(
        ('no-plugins', None,
         'Do not include Qt plugins in application bundle'),
    )
    # Add mpkg option
    _py2app.user_options.append(
        ('no-mpkg', None,
         'Do not build a mpkg from the bundle'),
    )
    # Add dmg option
    _py2app.user_options.append(
        ('no-dmg', None,
         'Do not build a dmg image from the bundle'),
    )
    _py2app.boolean_options.append('no-plugins')
    _py2app.boolean_options.append('no-mpkg')
    _py2app.boolean_options.append('no-dmg')
    def initialize_options(self):
        _py2app.initialize_options(self)
        self.no_plugins = False
        self.no_mpkg = False
        self.no_dmg = False
    def run(self):
        """Runs original py2app and deletes all files containing
        'debug' in their name.
        """
        # First normal py2app run
        _py2app.run(self)
        # Then remove debuging files
        print '*** removing Qt debug and unneeded  libs ***'
        for root, dirs, files in os.walk(self.dist_dir):
            for file in files:
                if 'debug' in file :
                    print 'removing', file
                    os.remove(os.path.join(root,file))

        if self.no_plugins is False:
           print "Copy plugins..."
           os.system("sh copy-plugins.sh")

           print "Generate qt.conf file..."
           ofi = open("dist/" + NAME + ".app/Contents/Resources/qt.conf", "w")
           print >> ofi, "[Paths]"
           print >> ofi, "Plugins = plugins"
           print >> ofi
           ofi.close()

        if self.no_mpkg is False:
           print "Generate mpkg..."
           pkgmgr_cmd = PKGMGR + " --doc series60-remote.pmdoc -o ./" + NAME + ".mpkg -v"
           os.system(pkgmgr_cmd)

           if self.no_dmg is False:
              print "Generate dmg"
              DIR = "build-dmg-%i" % random.Random().randint(1, 10000)
              copy_tree(NAME + ".mpkg", DIR + os.sep + NAME + ".mpkg", preserve_symlinks=1)
              os.system("perl pkg-dmg.pl --source %s --target %s --volname '%s' --icon phone.icns" % (DIR, NAME + "_" + VERSION + ".dmg", NAME + " " + VERSION))

setup(
    app = [APP_PATH + '/pc/series60_remote.py'],
    name = NAME,
    version = VERSION,
    setup_requires = ['py2app'],
    author='Lukas Hetzenecker',
    author_email='LuHe@gmx.at',
    url='http://series60-remote.sourceforge.net',
    download_url='http://sourceforge.net/projects/series60-remote/files',
    license='GPL',
    options = {
        'py2app': {
            'includes' : ['sip', 'PyQt4._qt', 'PyQt4.QtCore', 'PyQt4.QtGui', 
                          'PyQt4.QtSql', 'PyQt4.QtXml'],
            'excludes' : ['PyQt4.' + i for i in QT_EXCLUDES],
            'frameworks' : ['LightAquaBlue.framework', DYNLIB + 'libtiff.dylib', DYNLIB + 'libpng12.dylib', DYNLIB + 'libmng.dylib', DYNLIB + 'libjpeg.dylib'],
            'iconfile' : 'phone.icns',
            'argv_emulation': True,
        }
    },
    data_files = [
        ( 'doc', [APP_PATH + '/Changelog', APP_PATH + '/HACKING', APP_PATH + '/INSTALL', APP_PATH + '/LICENSE',
                  APP_PATH + '/LICENSE.icons-oxygen', APP_PATH + '/README.icons-oxygen', APP_PATH + '/TODO'] ),
        ( 'mobile', [APP_PATH + '/mobile/series60-remote-py14.sis', APP_PATH + '/mobile/series60-remote-py20.sis', 
                     APP_PATH + '/mobile/PythonForS60_1_4_5_3rdEd.sis', APP_PATH + '/mobile/Python_2.0.0.sis'] ),
        ( 'data/export-templates/default', [APP_PATH + '/pc/data/export-templates/default/contacts.html',
                                            APP_PATH + '/pc/data/export-templates/default/messages.html',
                                            APP_PATH + '/pc/data/export-templates/default/index.html',
                                            APP_PATH + '/pc/data/export-templates/default/style.css'] ),
    ],
    cmdclass = {
        'py2app': py2app
    }
)

