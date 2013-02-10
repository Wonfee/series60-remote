# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

import math
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class OrdinalNumberFormatter(object):
    @staticmethod
    def toString(number):
        main = qApp.property("main").toPyObject()

        locale = main.locale

        if locale.language() == QLocale.English:
            ones = number % 10
            tens = math.floor(number / 10.0) % 10

            if tens == 1:
                return str(number) + "th"

            if ones == 1:
                return str(number) + "st"
            if ones == 2:
                return str(number) + "nd"
            if ones == 3:
                return str(number) + "rd"
            return str(number) + "th"

        else:
            # Fallback...
            return str(number) + '.'
