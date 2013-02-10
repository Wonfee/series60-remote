# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import lib.chatwindowstyle
from lib.classes import *

class ChatMessageView(QWebView):
    def __init__(self,  parent):
        super(ChatMessageView,  self).__init__(parent)

        # HACK: We need Main()
        #main = qApp.property("main").toPyObject()

        #self.main = main
        #self.log = main.log

        # This is neeed for checks of consecutive messages
        self.__latestType = None
        self.__latestTime = None
        self.__latestPriority = MessagePriority.History

        # Security settings, we don't need this stuff
        self.settings().setAttribute(QWebSettings.JavascriptEnabled,  False)
        self.settings().setAttribute(QWebSettings.JavaEnabled,  False)
        self.settings().setAttribute(QWebSettings.PluginsEnabled,  False)
        self.settings().setAttribute(QWebSettings.PrivateBrowsingEnabled,  False)
        self.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled,  False)
        self.settings().setAttribute(QWebSettings.LocalStorageEnabled,  False)
        self.settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls,  False)

        # The settings of this chat window
        self.__contact = None
        self.__device = None
        self.__initialLayedOut = False
        self.currentChatStyle = None
        self.currentChatStyleVariant = ""
        self.groupConsecutiveMessages = True
        self.compact = False

        self.nameColors = ["red", "blue" , "gray", "magenta", "violet", "#808000", "yellowgreen",
                                        "darkred", "darkgreen", "darksalmon", "darkcyan",  "#B07D2B",
                                        "mediumpurple", "peru", "olivedrab", "#B01712", "darkorange", "slateblue",
                                        "slategray", "goldenrod", "orangered", "tomato", "#1E90FF", "steelblue",
                                        "deeppink", "saddlebrown", "coral", "royalblue" ]


        # Always scroll to the last message (with the highest priority) when the page is loaded
        self.connect(self,  SIGNAL("loadFinished(bool)"),  self.checkScroll)

        # Keep a list of messages (we need them when the style is changed)
        self.__messages = list()

        # The message which is scrolled to when the loading is finished
        # The geometry of the element is 0 when the page isn't yet loaded
        self.__scrollToMessage = None

    def init(self,  contact,  device):
        self.__contact = contact
        self.__device = device

    def setGroupConsecutiveMessages(self,  groupConsecutiveMessages):
        self.groupConsecutiveMessages = groupConsecutiveMessages
        if self.currentChatStyle:
            self.reload()

    def setCompact(self,  compact):
        self.compact = compact
        if self.currentChatStyle:
            self.reload()

    def setStyle(self,  style,  variant="",  groupConsecutiveMessages=False,  compact=False):
        self.currentChatStyle = style
        self.currentChatStyleVariant = variant
        self.groupConsecutiveMessages = groupConsecutiveMessages
        self.compact = compact
        self.reload()

    def setStyleName(self,  style,  variant="",  groupConsecutiveMessages=False,  compact=False,  directory=""):
        self.currentChatStyle = lib.chatwindowstyle.ChatWindowStyle(style,  directory)
        self.currentChatStyle.listVariants()
        self.currentChatStyleVariant = variant
        self.groupConsecutiveMessages = groupConsecutiveMessages
        self.compact = compact
        self.reload()

    def setStyleVariant(self,  variant):
        self.currentChatStyleVariant = variant
        if self.currentChatStyle:
            self.reload()

    def reload(self):
        self.__latestType = None
        self.__latestTime = None
        self.__latestPriority = MessagePriority.History
        self.writeTemplate()

    def styleHTML(self):
        style = QString("""body{background-color:%1;font-family:%2;font-size:%3;color:%4}
td{font-family:%5;font-size:%6;color:%7}
input{font-family:%8;font-size:%9pt;color:%10}
.history{color:%11}""")

        # The default font family and size of QWebView is really ugly
        browser = QTextBrowser()
        background = browser.palette().color(QPalette.Base).name()
        fontfamily = browser.font().family()
        if browser.font().pointSize() != -1:
            fontsize = str(browser.font().pointSize()) + "pt"
        else:
            fontsize = str(browser.font().pixelSize()) + "px"
        color = browser.palette().color(QPalette.Text).name()
        del browser

        style = style.arg(background)
        style = style.arg(fontfamily)
        style = style.arg(fontsize)
        style = style.arg(color)

        style = style.arg(fontfamily)
        style = style.arg(fontsize)
        style = style.arg(color)

        style = style.arg(fontfamily)
        style = style.arg(fontsize)
        style = style.arg(color)

        style = style.arg("#aaaa7f")

        return style

    def formatStyleKeywords(self,  sourceHTML,  message=None):
        resultHTML = sourceHTML

        if not self.currentChatStyle:
            return str()

        if isinstance(message,  type(None)):
            # Style formatting for header and footer.
            resultHTML = resultHTML.replace("%chatName%",  self.__contact.name())
            resultHTML = resultHTML.replace("%sourceName%",  self.__device.name())
            resultHTML = resultHTML.replace("%destinationName%",  self.__contact.name())
            resultHTML = resultHTML.replace("%timeOpened%",  unicode(QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate)))

            # Look for %timeOpened{X}%
            timeRegExp = QRegExp("%timeOpened\\{([^}]*)\\}%")
            textPos = timeRegExp.indexIn(resultHTML)
            while textPos >= 0:
                time = unicode(QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate))
                resultHTML = resultHTML.replace( timeRegExp.cap(0) , time ) # TODO: use keyword value
                textPos = timeRegExp.indexIn(resultHTML, textPos)

            if self.__contact.hasPicture():
                incomingIcon = "data:image/jpg;base64," + self.__contact.picture()
            else:
                incomingIcon = "Incoming/buddy_icon.png"
            outgoingIcon = "Outgoing/buddy_icon.png"

            resultHTML = resultHTML.replace("%incomingIconPath%",  incomingIcon)
            resultHTML = resultHTML.replace("%outgoingIconPath%",  outgoingIcon)

        else:
            # Style formatting for messages(incoming, outgoing, status)

            if message.type() == MessageType.Incoming:
                name = message.contact().name()
                screenName = str(message.contact().id())
            else:
                name = message.device().name()
                screenName = str(message.device().id())

            name = unicode(Qt.escape(name))

            if message.dateTime().date() == QDate.currentDate():
                time = unicode(message.dateTime().time().toString(Qt.DefaultLocaleLongDate))
            else:
                time = unicode(message.dateTime().toString(Qt.DefaultLocaleShortDate))

            time = time.strip() # whitespace at the end seems to break Glossyk style

            msg = message.message()
            msg = Qt.escape(msg)
            msg = unicode(msg.replace("\n",  "<br />"))

            if message.priority() == MessagePriority.History:
                # We want to use a different color for history messages, defaults to #aaaa7f in our CSS
                msg = "<span class=\"history\">" + msg + "</span>"

            icon = ""
            if message.contact().hasPicture() and message.type() == MessageType.Incoming:
                # Create a temporary image (it gets automatically deleted when the chat is closed)
                # filename = "S60Remote-contact-" + str(message.contact().id()) + ".jpg"
                # file = QTemporaryFile(self)
                # file.setFileName(QDir.tempPath() + QString(QDir.separator()) + filename)
                # if file.open():
                #    picture = message.contact().picture()
                #    data = base64.decodestring(picture)
                #    file.write(data)
                #    file.close()

                # Don't create a file, use the data scheme
                icon = "data:image/jpg;base64," + message.contact().picture()
            if not icon:
                if message.type() == MessageType.Incoming:
                    icon = "Incoming/buddy_icon.png"
                else:
                    icon = "Outgoing/buddy_icon.png"

            resultHTML = resultHTML.replace("%sender%",  name)
            resultHTML = resultHTML.replace("%senderScreenName%",  screenName)
            resultHTML = resultHTML.replace("%senderStatusIcon%",  "")
            resultHTML = resultHTML.replace("%time%",  time)
            resultHTML = resultHTML.replace("%service%",  "S60")
            resultHTML = resultHTML.replace("%message%",   msg)
            resultHTML = resultHTML.replace("%userIconPath%",  icon)
            resultHTML = resultHTML.replace("%stateElementId%",  "msST" + str(message.id()))

            # Set message direction("rtl"(Right-To-Left) or "ltr"(Left-to-right))
            resultHTML = resultHTML.replace("%messageDirection%",  "ltr")

            # Look for %time{X}%
            timeRegExp = QRegExp("%time\\{([^}]*)\\}%")
            textPos = timeRegExp.indexIn(resultHTML)
            while textPos >= 0:
                resultHTML = resultHTML.replace( timeRegExp.cap(0) , time ) # TODO: use keyword value
                textPos = timeRegExp.indexIn(resultHTML, textPos)

            # Look for %textbackgroundcolor{X}%
            bgColor = "inherit" # TODO: use X value
            textBackgroundRegExp = QRegExp("%textbackgroundcolor\\{([^}]*)\\}%")
            textPos = textBackgroundRegExp.indexIn(resultHTML)
            while textPos >= 0:
                resultHTML = resultHTML.replace(textBackgroundRegExp.cap(0), bgColor )
                textPos = textBackgroundRegExp.indexIn(resultHTML, textPos)

            hash_ = hash(message.contact().id() % len(self.nameColors))
            colorName = self.nameColors[hash_]
            lightColorName = ""

            senderColorRegExp = QRegExp("%senderColor(?:\\{([^}]*)\\})?%")
            textPos = senderColorRegExp.indexIn(resultHTML)
            while textPos >= 0:
                light = 100
                doLight = False
                if senderColorRegExp.numCaptures() >= 1:
                    light,  doLight = senderColorRegExp.cap(1).toInt()

                # Lazily init light color
                if doLight and lightColorName == "":
                    lightColorName = QColor(colorName).light(light).name()

                if doLight:
                    resultHTML = resultHTML.replace(senderColorRegExp.cap(0), lightColorName)
                else:
                    resultHTML = resultHTML.replace(senderColorRegExp.cap(0), colorName)
                textPos = senderColorRegExp.indexIn(resultHTML, textPos)

        return resultHTML

    def writeTemplate(self):
        # NOTE: About styles
        # Order of style tag in the template is important.
        # mainStyle take over all other style definition (which is what we want).
        #
        # S60RemoteStyle: Series60-Remote appearance configuration into a style. It loaded first because
        # we don't want Series60-Remote settings to override CSS Chat Window Style.
        # baseStyle: Import the main.css from the Chat Window Style
        # mainStyle: Currrent variant CSS url.

        if self.currentChatStyle:
            # FIXME: Maybe this string should be loaded from a file, then parsed for args.

            variant = self.currentChatStyleVariant
            if self.compact and self.currentChatStyle.hasCompact(variant):
                variant = self.currentChatStyle.compact(variant)

            xhtmlBase = QString("""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<style id="S60RemoteStyle" type="text/css" media="screen,print">
       %1
</style>
<style id="baseStyle" type="text/css" media="screen,print">
       @import url("main.css");
       *{ word-wrap:break-word; }
</style>
<style id="mainStyle" type="text/css" media="screen,print">
       @import url("%2");
</style>
</head>
<body>
%3
<div id="Chat">
</div>
%4
</body>
</html>""")

            xhtmlBase = xhtmlBase.arg(self.styleHTML())
            if self.currentChatStyleVariant:
                xhtmlBase = xhtmlBase.arg("Variants/" + variant + ".css")
            else:
                xhtmlBase = xhtmlBase.arg("")
            xhtmlBase = xhtmlBase.arg(self.formatStyleKeywords(self.currentChatStyle.headerHtml()))
            xhtmlBase = xhtmlBase.arg(self.formatStyleKeywords(self.currentChatStyle.footerHtml()))

            base = QUrl.fromLocalFile(self.currentChatStyle.stylePath)
            self.setHtml(xhtmlBase,  base)

            for message in self.__messages:
                # This is needed when the style was changed
                self.appendMessage(message,  restore=True)

        else:
            xhtmlBase = self.tr("Chat theme could not be found, or is invalid.")
            self.setHtml(xhtmlBase)

    def appendMessage(self,  message,  restore=False):
        if not restore:
            self.__messages.append(message)

        if not self.currentChatStyle:
            return

        formattedMessageHtml = ""
        chatElement = self.page().mainFrame().findFirstElement("#Chat")

        if chatElement.isNull():
            self.log.error("Chat Element was null !")
            return

        consecutiveMessage = False
        if self.groupConsecutiveMessages:
            # Check if the message can be handled as consecutive message
            timeout = 10 * 60
            consecutiveMessage = message.type() == self.__latestType and \
                                                    self.__latestTime and self.__latestTime.addSecs(timeout) >= message.dateTime()

        if message.type() == MessageType.Incoming:
            if consecutiveMessage:
                formattedMessageHtml = self.currentChatStyle.nextIncomingHtml()
            else:
                formattedMessageHtml = self.currentChatStyle.incomingHtml()
        elif message.type() == MessageType.Outgoing:
            if consecutiveMessage:
                formattedMessageHtml = self.currentChatStyle.nextOutgoingHtml()
            else:
                formattedMessageHtml = self.currentChatStyle.outgoingHtml()
        elif message.type() == MessageType.Internal:
            formattedMessageHtml = self.currentChatStyle.statusHtml()

        # The span tag is used to get the whole element when the page is loaded completly so it is possible to scroll to the latest unread message
        formattedMessageHtml = "\n<span id=\"S60RemoteMessage_" + str(message.id()) + "\">\n" + formattedMessageHtml + "\n</span>\n"
        formattedMessageHtml = self.formatStyleKeywords(formattedMessageHtml,  message)

        insertElement = self.page().mainFrame().findFirstElement("#insert")

        if consecutiveMessage:
            # Replace the insert block, because it's a consecutive message.
            insertElement.replace(formattedMessageHtml)
        else:
            insertElement.removeFromDocument()
            chatElement.appendInside(formattedMessageHtml)

        self.__latestType = message.type()
        self.__latestTime = message.dateTime()

        if message.priority() == MessagePriority.History \
            or message.priority() > self.__latestPriority:

            self.__latestPriority = message.priority()

            # We scroll to this message when the page is loaded...
            self.__scrollToMessage = message

            # Reset the priority after 1 second
            # (so we jump to the first unread message and the user has enough time to read it)
            QTimer.singleShot(1000,  self.clearPriority)

    def clearPriority(self):
        self.__latestPriority = MessagePriority.Low

    def checkScroll(self):
        if self.__scrollToMessage:
            # If it's the first message stay at the top of the page
            if self.__scrollToMessage == self.__messages[0]:
                self.__scrollToMessage = None
            else:
                element = self.page().mainFrame().findFirstElement("#S60RemoteMessage_" + str(self.__scrollToMessage.id()))
                if element and element.geometry().y() != 0:

                    # Scroll only if there is a scrollbar.. otherwise we wait until we get one ;)
                    if self.page().mainFrame().scrollBarMaximum(Qt.Vertical) > 0:
                        self.page().mainFrame().setScrollPosition(QPoint(0, element.geometry().y()))

                        self.__scrollToMessage = None

        if not self.__initialLayedOut:
            # When we change the content of a QWebElement no signal is emitted, so we use contentsSizeChanged
            # TODO: Find a better way ;)
            self.__initialLayedOut = True
            self.disconnect(self,  SIGNAL("loadFinished(bool)"),  self.checkScroll)
            self.connect(self.page().mainFrame(),  SIGNAL("contentsSizeChanged(const QSize &)"),  self.checkScroll)
