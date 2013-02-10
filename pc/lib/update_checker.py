# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

import sys
import distutils.version
from PyQt4.QtCore import *
from PyQt4.QtNetwork import *

class UpdateChecker(QObject):
    def __init__(self, parent, main):
        super(UpdateChecker,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.settings = main.settings
        self.log = main.log

        self.manager = QNetworkAccessManager(parent)
        self.connect(self.manager,  SIGNAL("finished(QNetworkReply *)"),  self.updateReply)

    def updateCheck(self):
        url = self.settings.setting("updateCheck/url")

        version = ".".join([str(i) for i in self.main.appVersion])
        url.addQueryItem("version", version)
        url.addQueryItem("platform", sys.platform)

        request = QNetworkRequest(url)
        request.setRawHeader("User-Agent",  "Series60-Remote Update-Checker (%s; %s)" % (sys.platform,  version))

        self.log.info(QString("Checking for updates using url %1").arg(url.toString()))

        self.manager.get(QNetworkRequest(url))

    def updateReply(self,  reply):
        if reply.error() != QNetworkReply.NoError:
            self.log.error(QString("Update check failed: %1").arg(reply.errorString()))
            self.emit(SIGNAL("updateCheckFailed"),  reply.errorString())
            return

        currentVersion = ".".join([str(i) for i in self.main.appVersion])
        showUnstable = self.settings.setting("updateCheck/showUnstable")

        currentVersion = distutils.version.LooseVersion(currentVersion)

        version = currentVersion
        message = ""
        validKeyFound = False
        data = unicode(reply.readAll())
        for line in data.split('\n'):
            if line.count(" ") < 1:
                continue
            key,  value = line.split(' ',  1)
            if key == "STABLE_VERSION":
                validKeyFound = True
                sv = distutils.version.LooseVersion(value)
                version = max(version,  sv)
            elif key == "UNSTABLE_VERSION":
                validKeyFound = True
                if showUnstable:
                    uv = distutils.version.LooseVersion(value)
                    version = max(version,  uv)
            elif key == "UPDATE_MESSAGE":
                validKeyFound = True
                message = value
            elif key == "URL_MOVED":
                validKeyFound = True
                self.settings.setSetting("updateCheck/url",  QUrl(value))
            elif key == "WEBSITE_CHANGED":
                validKeyFound = True
                self.settings.setSetting("updateCheck/website",  QUrl(value))
            elif key == "DISABLE_CHECK":
                validKeyFound = True
                self.settings.setSetting("updateCheck/enabled",  False)
            else:
                self.log.info(QString("Unknown key in update check response: %1").arg(key))

        if not validKeyFound:
            error = "No valid version string found!"
            self.log.error(QString("Update check failed: %1").arg(error))
            self.emit(SIGNAL("updateCheckFailed"),  error)

        if version > currentVersion:
            version = str(version)
            self.settings.setSetting("updateCheck/lastVersion",  version)
            self.settings.setSetting("updateCheck/lastMessage",  message)
            self.log.info(QString("Detected new version: %1").arg(version))
            self.emit(SIGNAL("updateCheckNewVersion"),  version,  message)
        else:
            self.log.info(QString("Update check finished, no new version"))

        self.settings.setSetting("updateCheck/lastCheck",  QDate.currentDate())



