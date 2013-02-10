# -*- mode: python -*-

# File for pyinstaller

APP_PATH = os.sep.join(os.path.realpath(os.curdir).split(os.sep)[:-3]) # e. g. c:\\Dokumente und Einstellungen\\lukas\\Eigene Dateien\\series60-remote\\series60-remote-svn\\trunk
INST_PATH = os.path.dirname( os.path.realpath( __file__ ) ) # e. g. c:\\Dokumente und Einstellungen\\lukas\\Eigene Dateien\\pyinstaller

print "Application path is", APP_PATH
print "PyInstaller path is", INST_PATH

# Get list of data files
datafiles = []
for root, dirs, files in os.walk(APP_PATH + "\\pc\\data\\"):
   # Ignore hidden directories (e.g. .svn)
   for dir in dirs:
      if dir.startswith("."):
         dirs.remove(dir)
   dest = root.replace(APP_PATH + "\\pc\\", "")
   dest = dest.replace("\\", "/")
   for file in files:
      datafiles.append( (dest + "/" + file, root + "\\" + file, 'DATA') )

a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), APP_PATH + '\\pc\\series60_remote.py'],
             pathex=[INST_PATH])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts + [('O','','OPTION')],
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\series60-remote', 'series60-remote.exe'),
          icon=APP_PATH + "\\pc\\pics\\phone.ico",
          debug=False,
          strip=True,
          upx=False,
          console=False )

coll = COLLECT(exe,
               a.binaries,
               [("Changelog.txt", APP_PATH + "\\Changelog", 'DATA')],
               [("HACKING.txt", APP_PATH + "\\HACKING", 'DATA')],
               [("INSTALL.txt", APP_PATH + "\\INSTALL", 'DATA')],
               [("LICENSE.txt", APP_PATH + "\\LICENSE", 'DATA')],
               [("LICENSE.icons-oxygen.txt", APP_PATH + "\\LICENSE.icons-oxygen", 'DATA')],
               [("README.icons-oxygen.txt", APP_PATH + "\\README.icons-oxygen", 'DATA')],
               [("TODO.txt", APP_PATH + "\\TODO", 'DATA')],
               [("mobile/series60-remote-py14.sis", APP_PATH + "\\mobile\\series60-remote-py14.sis", 'DATA')],
               [("mobile/series60-remote-py20.sis", APP_PATH + "\\mobile\\series60-remote-py20.sis", 'DATA')],
               [("mobile/PythonForS60_1_4_5_3rdEd.sis", APP_PATH + "\\mobile\\PythonForS60_1_4_5_3rdEd.sis", 'DATA')],
               [("mobile/Python_2.0.0.sis", APP_PATH + "\\mobile\\Python_2.0.0.sis", 'DATA')],
               datafiles,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name=os.path.join('dist', 'series60-remote'))
