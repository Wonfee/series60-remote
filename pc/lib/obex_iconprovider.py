# -*- coding: utf-8 -*-

# Copyright (c) 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from obex_items import *

class ObexIconProvider(QFileIconProvider):
    def icon(self,  item):
        if isinstance(item,  DirectoryItem):
            if not item.parent():
                if item.memType() == "DEV":
                    return QFileIconProvider.icon(self,  QFileIconProvider.Drive) or QIcon(":/drive-harddisk")
                else:
                    return QIcon(":/media-mmc")
            return QFileIconProvider.icon(self,  QFileIconProvider.Folder) or QIcon(":/inode-directory")
        
        elif isinstance(item,  FileItem):
            try:
                type = item.name().split(".")[-1:][0]
            except:
                return QIcon(":/application-octet-stream")
            
            if type == "doc":
                return QIcon(":/application-msword")
            elif type == "pdf":
                return QIcon(":/application-pdf")
            elif type == "xls":
                return QIcon(":/application-msexcel")
            elif type == "ppt":
                return QIcon(":/application-mspowerpoint")
            elif type in ["jar",  "jad"]:
                return QIcon(":/application-java")
            elif type in ["wav",  "wave"]:
                return QIcon(":/audio-wav")
            elif type in ["m3u",  "mp3",  "mp4", "wma",  "midi",  "aac",  "ogg",  "aif",  "aiff",  "flac",  "amr"]:
                return QIcon(":/audio-generic")
            elif type in ["avi",  "mpg",  "mpeg",  "3gp"]:
                return QIcon(":/video-generic")
            elif type in ["png",  "jpg",  "jpeg",  "tiff",  "bmp",  "svg",  "svgz",  "ico"]:
                return QIcon(":/image-generic")
            elif type in ["txt",  "xml",  "csv"]:
                return QFileIconProvider.icon(self,  QFileIconProvider.File) or QIcon(":/text-plain")
            
            return QIcon(":/unknown")
        return QIcon(":/unknown")
