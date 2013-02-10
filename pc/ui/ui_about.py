# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/about.ui'
#
# Created: Wed Nov 17 12:05:52 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(625, 485)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/phone"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AboutDialog.setWindowIcon(icon)
        self.verticalLayout_3 = QtGui.QVBoxLayout(AboutDialog)
        self.verticalLayout_3.setSpacing(20)
        self.verticalLayout_3.setMargin(15)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtGui.QLabel(AboutDialog)
        self.label.setPixmap(QtGui.QPixmap(":/phone"))
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtGui.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(50)
        font.setBold(False)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtGui.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.versionLabel = QtGui.QLabel(AboutDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.versionLabel.setFont(font)
        self.versionLabel.setText("x.y.z")
        self.versionLabel.setObjectName("versionLabel")
        self.horizontalLayout.addWidget(self.versionLabel)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.tabWidget = QtGui.QTabWidget(AboutDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.aboutTab = QtGui.QWidget()
        self.aboutTab.setObjectName("aboutTab")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.aboutTab)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setMargin(15)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_5 = QtGui.QLabel(self.aboutTab)
        self.label_5.setWordWrap(True)
        self.label_5.setOpenExternalLinks(True)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_2.addWidget(self.label_5)
        spacerItem1 = QtGui.QSpacerItem(20, 23, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.tabWidget.addTab(self.aboutTab, "")
        self.creditsTab = QtGui.QWidget()
        self.creditsTab.setObjectName("creditsTab")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.creditsTab)
        self.verticalLayout_4.setSpacing(5)
        self.verticalLayout_4.setContentsMargins(10, 5, 10, 5)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.creditBrowser = QtGui.QTextBrowser(self.creditsTab)
        self.creditBrowser.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>")
        self.creditBrowser.setObjectName("creditBrowser")
        self.verticalLayout_4.addWidget(self.creditBrowser)
        self.tabWidget.addTab(self.creditsTab, "")
        self.versionInformationTab = QtGui.QWidget()
        self.versionInformationTab.setObjectName("versionInformationTab")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.versionInformationTab)
        self.verticalLayout_5.setSpacing(5)
        self.verticalLayout_5.setContentsMargins(10, 5, 10, 5)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.versionBrowser = QtGui.QTextBrowser(self.versionInformationTab)
        self.versionBrowser.setObjectName("versionBrowser")
        self.verticalLayout_5.addWidget(self.versionBrowser)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.copyButton = QtGui.QPushButton(self.versionInformationTab)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/edit-copy"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.copyButton.setIcon(icon1)
        self.copyButton.setObjectName("copyButton")
        self.horizontalLayout_3.addWidget(self.copyButton)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.tabWidget.addTab(self.versionInformationTab, "")
        self.verticalLayout_3.addWidget(self.tabWidget)
        self.buttonBox = QtGui.QDialogButtonBox(AboutDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(AboutDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), AboutDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), AboutDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QtGui.QApplication.translate("AboutDialog", "About Series60-Remote", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("AboutDialog", "Series60-Remote", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("AboutDialog", "Version", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("AboutDialog", "<p><b>Series60-Remote</b> is written and maintained by Lukas Hetzenecker.</p>\n"
"\n"
"<p>Visit <a href=\"http://series60-remote.sf.net\">http://series60-remote.sf.net</a> for more information on this project.</p>\n"
"\n"
"<h3>Bugs and wishes</h3>\n"
"<p>Software can always be improved, and i am ready to do so. However, you - the user - must tell me when something does not work as expected or could be done better.</p>\n"
"\n"
"<p>Series60-Remote has a bug tracking system. Visit <a href=\"http://series60-remote.sf.net\">http://series60-remote.sf.net</a> to report bugs.\n"
"\n"
"<h3>License</h3>\n"
"<p><a href=\"http://www.gnu.org/licenses/gpl-2.0.txt\">GNU General Public License Version 2</a></p>", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.aboutTab), QtGui.QApplication.translate("AboutDialog", "&About", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.creditsTab), QtGui.QApplication.translate("AboutDialog", "&Credits", None, QtGui.QApplication.UnicodeUTF8))
        self.copyButton.setText(QtGui.QApplication.translate("AboutDialog", "Copy", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.versionInformationTab), QtGui.QApplication.translate("AboutDialog", "Version information", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc
