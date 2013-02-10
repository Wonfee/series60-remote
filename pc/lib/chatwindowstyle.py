# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ChatWindowStyle(QObject):
    def __init__(self,  styleName,  stylePath=""):
        super(ChatWindowStyle,  self).__init__()

        # HACK: We need Main()
        main = qApp.property("main").toPyObject()

        self.main = main
        self.helper = main.helper

        if not stylePath:
            stylePath = self.helper.chatThemeFolder(styleName)

        if not stylePath:
            self.stylePath =  None
            return None

        self.stylePath = stylePath + os.sep + "Contents" + os.sep + "Resources" + os.sep

        self.__headerHtml = ""
        self.__footerHtml = ""
        self.__incomingHtml = ""
        self.__nextIncomingHtml = ""
        self.__outgoingHtml = ""
        self.__nextOutgoingHtml = ""
        self.__statusHtml = ""

        self.__compactVariants = list()
        self.__variantsList = list()

        self.readStyleFiles()

    def __nonzero__(self):
        return bool(self.stylePath and self.incomingHtml()) and bool(self.outgoingHtml())

    def variants(self):
        if not self.__variantsList:
            self.listVariants()

        return self.__variantsList

    def hasCompact(self,  styleVariant):
        return styleVariant in self.__compactVariants

    def compact(self,  styleVariant):
        if not styleVariant:
            return "_compact_"
        else:
            return "_compact_" + styleVariant

    def listVariants(self):
        self.__compactVariants = list()
        self.__variantsList = list()

        variantDirPath = self.stylePath + "Variants/"
        variantDir = QDir(variantDirPath)

        variantList = variantDir.entryList(QStringList("*.css"))
        compactVersionPrefix = "_compact_"
        for variantName in variantList:
            variantName = variantName.left(variantName.lastIndexOf("."))

            if variantName.startsWith(compactVersionPrefix):
                if variantName == compactVersionPrefix:
                    self.__compactVariants.append("")
                continue

            compactVersionPath = variantDirPath + os.sep + "_compact_" + variantName + ".css"
            if QFile.exists(compactVersionPath):
                self.__compactVariants.append(variantName)

            self.__variantsList.append(variantName)

    def headerHtml(self): return unicode(self.__headerHtml)
    def footerHtml(self): return unicode(self.__footerHtml)
    def incomingHtml(self): return unicode(self.__incomingHtml)
    def nextIncomingHtml(self): return unicode(self.__nextIncomingHtml)
    def outgoingHtml(self): return unicode(self.__outgoingHtml)
    def nextOutgoingHtml(self): return unicode(self.__nextOutgoingHtml)
    def statusHtml(self): return unicode(self.__statusHtml)

    def readStyleFiles(self):
        self.headerFile = self.stylePath + "Header.html"
        self.footerFile = self.stylePath + "Footer.html"
        self.incomingFile = self.stylePath + "Incoming/Content.html"
        self.nextIncomingFile = self.stylePath + "Incoming/NextContent.html"
        self.outgoingFile = self.stylePath + "Outgoing/Content.html"
        self.nextOutgoingFile = self.stylePath + "Outgoing/NextContent.html"
        self.statusFile = self.stylePath + "Status.html"
        self.outgoingStateUnknownFile = self.stylePath + "Outgoing/StateUnknown.html"
        self.outgoingStateSendingFile = self.stylePath + "Outgoing/StateSending.html"
        self.outgoingStateSentFile = self.stylePath + "Outgoing/StateSent.html"
        self.outgoingStateErrorFile = self.stylePath + "Outgoing/StateError.html"
        # Ignored: Incoming/FileTransferRequest.html, Incoming/voiceClipRequest.html, Incoming/Action.html, Outgoing/Action.html

        fileAccess = QFile()

        # First load header file
        if QFile.exists(self.headerFile):
            fileAccess.setFileName(self.headerFile)
            fileAccess.open(QIODevice.ReadOnly)
            stream = QTextStream(fileAccess)
            stream.setCodec(QTextCodec.codecForName("UTF-8"))
            self.__headerHtml = stream.readAll()
            fileAccess.close()

        # Load Footer file
        if QFile.exists(self.footerFile):
            fileAccess.setFileName(self.footerFile)
            fileAccess.open(QIODevice.ReadOnly)
            stream = QTextStream(fileAccess)
            stream.setCodec(QTextCodec.codecForName("UTF-8"))
            self.__footerHtml = stream.readAll()
            fileAccess.close()

        # Load incoming file
        if QFile.exists(self.incomingFile):
            fileAccess.setFileName(self.incomingFile)
            fileAccess.open(QIODevice.ReadOnly)
            stream = QTextStream(fileAccess)
            stream.setCodec(QTextCodec.codecForName("UTF-8"))
            self.__incomingHtml = stream.readAll()
            fileAccess.close()

        # Load next Incoming file
        if QFile.exists(self.nextIncomingFile):
            fileAccess.setFileName(self.nextIncomingFile)
            fileAccess.open(QIODevice.ReadOnly)
            stream = QTextStream(fileAccess)
            stream.setCodec(QTextCodec.codecForName("UTF-8"))
            self.__nextIncomingHtml = stream.readAll()
            fileAccess.close()

        # Load outgoing file
        if QFile.exists(self.outgoingFile):
            fileAccess.setFileName(self.outgoingFile)
            fileAccess.open(QIODevice.ReadOnly)
            stream = QTextStream(fileAccess)
            stream.setCodec(QTextCodec.codecForName("UTF-8"))
            self.__outgoingHtml = stream.readAll()
            fileAccess.close()

        # Load next outgoing file
        if QFile.exists(self.nextOutgoingFile):
            fileAccess.setFileName(self.nextOutgoingFile)
            fileAccess.open(QIODevice.ReadOnly)
            stream = QTextStream(fileAccess)
            stream.setCodec(QTextCodec.codecForName("UTF-8"))
            self.__nextOutgoingHtml = stream.readAll()
            fileAccess.close()

        # Load outgoing files
        if QFile.exists(self.outgoingStateUnknownFile):
            fileAccess.setFileName(self.outgoingStateUnknownFile)
            fileAccess.open(QIODevice.ReadOnly)
            stream = QTextStream(fileAccess)
            stream.setCodec(QTextCodec.codecForName("UTF-8"))
            self.__outgoingStateUnknownHtml = stream.readAll()
            fileAccess.close()

        if QFile.exists(self.outgoingStateSendingFile):
            fileAccess.setFileName(self.outgoingStateSendingFile)
            fileAccess.open(QIODevice.ReadOnly)
            stream = QTextStream(fileAccess)
            stream.setCodec(QTextCodec.codecForName("UTF-8"))
            self.__outgoingStateSendingHtml = stream.readAll()
            fileAccess.close()

        if QFile.exists(self.outgoingStateSentFile):
            fileAccess.setFileName(self.outgoingStateSentFile)
            fileAccess.open(QIODevice.ReadOnly)
            stream = QTextStream(fileAccess)
            stream.setCodec(QTextCodec.codecForName("UTF-8"))
            self.__outgoingStateSentHtml = stream.readAll()
            fileAccess.close()

        if QFile.exists(self.outgoingStateErrorFile):
            fileAccess.setFileName(self.outgoingStateErrorFile)
            fileAccess.open(QIODevice.ReadOnly)
            stream = QTextStream(fileAccess)
            stream.setCodec(QTextCodec.codecForName("UTF-8"))
            self.__outgoingStateErrorHtml = stream.readAll()
            fileAccess.close()

