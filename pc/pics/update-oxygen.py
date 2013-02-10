#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

import sys
import os
import shutil

def copy(src,  dst):
    if not os.path.exists(src):
        print "FAILED TO COPY " + src + ", File does not exist"
        return
    
    if not os.path.exists(dst):
        print "CREATE " + dst
        shutil.copy(src, dst)
    elif file(src).read() != file(dst).read():
        shutil.copy(src, dst)
        print "UPDATE " + dst

try:
    root = sys.argv[1]
    if not root.endswith("/"):
        root += "/"
except:
    root = "/usr/share/icons/oxygen/"

if not os.path.exists("oxygen/"):
    os.mkdir("oxygen/")

if not os.path.exists("oxygen/scalable"):
    os.mkdir("oxygen/scalable")

for line in file.readlines(file("oxygen-icon-list")):
   line = line.strip()
   line = line.split(" ")
   filename = line[0]
   try:
      destname = line[1]
   except:
      destname = filename.split("/")[1]

   try:
      option = line[2]
   except:
      option = ""

   try:
      svgoption = line[3]
   except:
      svgoption = ""

   if option == "size-64":
      sizename = "64x64/" + filename
   elif option == "size-16":
      sizename = "16x16/" + filename
   else:
      sizename = "32x32/" + filename

   destname += ".png"
   sizename += ".png"
   svgsrc = svgdest = "scalable/" + filename + ".svgz"
   svgdir = "scalable/" + filename.split("/")[0]

   if option == "svg-size-32" or svgoption == "svg-size-32":
      svgsrc = "scalable/" + filename.split("/")[0] + "/small/32x32/" + filename.split("/")[1] + ".svgz"
   elif option == "svg-size-16" or svgoption == "svg-size-16":
      svgsrc = "scalable/" + filename.split("/")[0] + "/small/16x16/" + filename.split("/")[1] + ".svgz"

   if not os.path.exists("oxygen/" + svgdir):
      os.mkdir("oxygen/" + svgdir)

   if not option == "only-svgz":
        copy(root + sizename, "oxygen/" + destname)
   copy(root + svgsrc, "oxygen/" + svgdest)
