# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

import sys
import platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_about

# Some basic operating system informations
PLATFORM = sys.platform
OS_RELEASE = "unknown"
if PLATFORM == "linux2":
    if sys.version_info < (2, 6):
        OS_RELEASE = " ".join(platform.dist())
    else:
        OS_RELEASE = " ".join(platform.linux_distribution())
elif PLATFORM == "darwin":
    OS_RELEASE = platform.mac_ver()[0] + " " + platform.mac_ver()[2]
elif PLATFORM == "win32":
    OS_RELEASE = "Windows " +  " ".join(platform.win32_ver())

# Try to get version of all components
PYTHON_VERSION = platform.python_version()
PYQT_VERSION = PYQT_VERSION_STR
QT_VERSION = qVersion()


try:
    import bluetooth
    PYBLUEZ = "found"
    if PLATFORM == "win32":
        if bluetooth.have_widcomm:
            PYBLUEZ += " (widcomm)"
        else:
            PYBLUEZ += " (msbt)"
except:
    PYBLUEZ = "not found"

try:
    import PyOBEX
    PYOBEX_VERSION = PyOBEX.__version__
except:
    PYOBEX_VERSION = "not found"

try:
    import obexftp
    OBEXFTP = "found"
except:
    OBEXFTP = "not found"

try:
    import lightblue
    LIGHTBLUE = "found"
except:
    LIGHTBLUE = "not found"

try:
    import matplotlib
    MATPLOTLIB_VERSION = matplotlib.__version__
except:
    MATPLOTLIB_VERSION = "not found"

try:
    import vobject
    VOBJECT = "found"
except:
    VOBJECT = "not found"

try:
    import ldap
    LDAP_VERSION = ldap.__version__
except:
    LDAP_VERSION = "not found"

class About(QDialog,  ui.ui_about.Ui_AboutDialog):
    def __init__(self, parent, main):
        super(About,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.setupUi(self)

        self.connect(self.copyButton, SIGNAL("clicked()"),  self.copyVersion)

        self.contributors = [
                            ["Pierre-Yves Chibon",  "pingou@pingoured.fr",  "CSV, vCard and LDAP export plugin, Contact import"],  
                        ]

        self.translators = [
                            ["Lukas Hetzenecker",  "LuHe@gmx.at",  "German"],  
                            ["Chris Van Bael",  "chris.van.bael@gmail.com",  "Dutch"],  
                            ["Mari&aacute;n Kyral",  "mkyral@email.cz",  "Czech"],  
                            ["Piotr KALINA (m@urycy)",  "piotr.kalina@gmail.com",  "Polish"],  
                            ["Mirko Allegretti",  "mirko.allegretti@gmail.com",  "Italian"],
                            ["Franco Funes",  "funesfranco@gmail.com",  "Spanish"], 
                        ]
        
        credits = u"""<p><b>The KDE Artwork team</b> for the Oxygen icon set.</p>
<p><b>Phil Thompson</b> for providing PyQt4.<br />
<b>David Boddie</b> for providing PyOBEX and for helping me many times.<br />
<b>Nokia</b> for providing PyS60 and Qt.<br />
<b>The Python, pybluez and matplotlib developers</b>
</p>
"""

        credits += "<p><b><u>Contributors</u></b></p>"
        for name,  mail, contribution in self.contributors:
            credits += "<p><b>" + name + "</b>" + " &lt;" + mail + "&gt;<br />"
            credits += contribution + "</p>"

        credits += "<p><b><u>Translators</u></b></p>"
        for name,  mail, language in self.translators:
            credits += "<p><b>" + name + "</b>" + " &lt;" + mail + "&gt;<br />"
            credits += language + "&nbsp;translator</p>"
        
        credits += "<p>And all the people who reported bugs and made suggestions.</p>"
        
        self.creditBrowser.setHtml(credits)

        self.versionLabel.setText(self.main.appVersionStr)

        version = ".".join([str(i) for i in main.appVersion])
        text = "Application version: " + version + " (" + main.appVersionStr + ")" + "\n"
        text += "Settings version: " + str(main.settingsVersionStr) + "\n"
        text += "Database version: " + str(main.databaseVersionStr) + "\n\n"
        text += "Platform: " + PLATFORM + "\n"
        text += "Operating system release: " + OS_RELEASE + "\n\n"
        text += "Python: " + PYTHON_VERSION + "\n"
        text += "PyQt4: " + PYQT_VERSION + "\n"
        text += "Qt4: " + QT_VERSION + "\n"
        text += "pybluez: " + PYBLUEZ + "\n"
        text += "PyOBEX: " + PYOBEX_VERSION + "\n"
        text += "obexftp: " + OBEXFTP + "\n"
        text += "lightblue: " + LIGHTBLUE + "\n"
        text += "matplotlib: " + MATPLOTLIB_VERSION + "\n"
        text += "vobject: " + VOBJECT + "\n"
        text += "ldap: " + LDAP_VERSION + "\n"

        self.versionBrowser.setPlainText(text)

        self.show()

    def copyVersion(self):
        qApp.clipboard().setText(self.versionBrowser.toPlainText())
