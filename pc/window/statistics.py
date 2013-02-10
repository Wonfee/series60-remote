# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

import datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Matplotlib
try:
    import matplotlib
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
    from matplotlib.figure import Figure
    from matplotlib.font_manager import FontProperties
    from matplotlib.ticker import ScalarFormatter
except ImportError:
    USE_MATPLOTLIB = False
else:
    USE_MATPLOTLIB= True

import ui.ui_statistics
from lib.classes import *

if USE_MATPLOTLIB:
    class PositiveFormatter(ScalarFormatter):
        def pprint_val(self, x):
            return ScalarFormatter.pprint_val(self, abs(x))

class Statistics(QDialog,  ui.ui_statistics.Ui_Statistics):
    def __init__(self, parent, main,  contact=None):
        super(Statistics,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.setupUi(self)
        main.setupButtonBox(self.buttonBox)

        self.graphLayout = StatisticGraphLayout.Stacked
        self.lastRequest = None

        self.connect(self.statisticTab,  SIGNAL("currentChanged(int)"),  lambda x : self.refreshStatistic())
        self.connect(self.infoBrowser,  SIGNAL("anchorClicked(const QUrl &)"),  self.refreshStatistic)
        self.connect(self.filterBox,  SIGNAL("currentIndexChanged(int)"),  lambda x : self.refreshStatistic(reset=False))
        self.connect(self.contactBox,  SIGNAL("currentIndexChanged(int)"),  lambda x : self.refreshStatistic(reset=False))
        self.connect(self.viewBox,  SIGNAL("currentIndexChanged(int)"),  lambda x : self.refreshStatistic())
        self.connect(self.stackedAction,  SIGNAL("triggered()"),  self.stackedGraph)
        self.connect(self.separateAction,  SIGNAL("triggered()"),  self.separateGraph)

        self.show()

        if USE_MATPLOTLIB:
            self.log.info(QString("Matplotlib found - generating statistics"))
        else:
            self.log.info(QString("Matplotlib not found :-("))

        # On older versions of matplotlib the default size of the matplotlib widget is incorrect
        if USE_MATPLOTLIB:
            self.log.info(QString("Using matplotlib version %1").arg(matplotlib.__version__))
            if not matplotlib.compare_versions(matplotlib.__version__,  '0.98.6svn'):
                self.log.warning(QString("too old version of matplotlib - faking widget size"))
                self.resize(self.size().width()+1, self.size().height()+1)
                self.resize(self.size().width()-1, self.size().height()-1)

        self.insertContacts(contact)
        self.refreshStatistic()

    def insertContacts(self,  currentContact):
        self.contactBox.addItem(self.tr("All"),  QVariant(Contact()))
        self.contactBox.insertSeparator(1)

        for contact in self.database.contactsWithMessages():
            self.contactBox.addItem(contact.name(),  QVariant(contact))

        index = 0
        if currentContact:
            index = self.contactBox.findText(currentContact.name())
            if index == -1:
                index = 0

        self.contactBox.setCurrentIndex(index)

    def refreshStatistic(self,  url=None,  reset=True):
        if self.statisticTab.currentIndex() == 0:
        
            if USE_MATPLOTLIB:
                self.statisticPlot.addAction(self.stackedAction)
                self.statisticPlot.addAction(self.separateAction)

                self.statisticPlot.ax.clear()
                self.statisticPlot.format_labels()

            if reset or not self.lastRequest:
                request = StatisticsRequest()
            else:
                request = self.lastRequest

            request.setStatisticFor(StatisticFor.Periods)
            if url == QUrl('#YearsAndMonths'):
                request.setPeriod(StatisticPeriod.YearsAndMonths)
            elif url == QUrl('#Years'):
                request.setPeriod(StatisticPeriod.Years)
            elif url == QUrl('#Months'):
                request.setPeriod(StatisticPeriod.Months)
            elif url == QUrl('#Days'):
                request.setPeriod(StatisticPeriod.Days)
                
            elif url:
                parts = str(url.toString()).split("#")[1:]
                for part in parts:
                    key,  value = part.split("_")
                    if key == "Year":
                        request.setPeriod(StatisticPeriod.Months)
                        request.setYear(int(value))
                    elif key == "Month":
                        request.setPeriod(StatisticPeriod.Days)
                        request.setMonth(int(value))
                    elif key == "Day":
                        request.setPeriod(StatisticPeriod.Hours)
                        request.setDay(int(value))

            elif reset or not self.lastRequest:
                if self.viewBox.currentIndex() == 0:
                    request.setPeriod(StatisticPeriod.YearsAndMonths)
                elif self.viewBox.currentIndex() == 1:
                    request.setPeriod(StatisticPeriod.Years)
                elif self.viewBox.currentIndex() == 2:
                    request.setPeriod(StatisticPeriod.Months)
                elif self.viewBox.currentIndex() == 3:
                    request.setPeriod(StatisticPeriod.Days)
                elif self.viewBox.currentIndex() == 4:
                    request.setPeriod(StatisticPeriod.Weekdays)
                else:
                    request.setPeriod(StatisticPeriod.Hours)

            if self.filterBox.currentIndex() == 0:
                request.setType(MessageType.All)
            elif self.filterBox.currentIndex() == 1:
                request.setType(MessageType.Incoming)
            else:
                request.setType(MessageType.Outgoing)

            request.setContact(self.contactBox.itemData(self.contactBox.currentIndex()).toPyObject())

            self.lastRequest = request
            get = self.database.statistics(request)
            period = get.request().period()

            cursor = self.infoBrowser.textCursor()

            if USE_MATPLOTLIB:
                # This is needed to show also zero values
                # (e.g. days where no message was sent when view is set to month)
                
                # The list is filled with zeros which are replaced by the correct values afterwards
                # So days/months where no data is available has zero by default in the plot
                
                if not get:
                    y1 = []
                    x = []
                
                elif period == StatisticPeriod.Years:
                    first = get[0].year()
                    last = get[-1].year()
                    y1 = [0 for i in range(last - first + 1)]
                    x = [str(first+i) for i in range(last - first + 1)]
                
                elif period == StatisticPeriod.YearsAndMonths:
                    first = get[0]
                    last = get[-1]
                    
                    months = last.year() - first.year() + 1
                    months *= 12
                    months -= first.month() - 1
                    months -= 12 - last.month()
                    
                    y1 = list()
                    x = list()
                    cur = QDate(first.year(),  first.month(),  1)
                    for month in range(months):
                        y1.append(0)
                        #x.append(unicode(cur.toString("MMM yy")))
                        x.append(datetime.datetime(cur.year(),  cur.month(),  1))
                        cur = cur.addMonths(1)
                    
                elif period == StatisticPeriod.Months:
                    y1 = [0 for i in range(12)]
                    x = [unicode(self.main.locale.standaloneMonthName(i+1)) for i in range(12)]
                
                elif period == StatisticPeriod.Days:
                    mon = get.request().month()
                    year =  get.request().year()
                    if mon and year:
                        days = QDate(year,  mon,  1).daysInMonth()
                    else:
                        days = 31
                    y1 = [0 for i in range(days)]
                    x = [str(i+1) for i in range(days)]
                
                elif period == StatisticPeriod.Weekdays:
                    y1 = [0 for i in range(7)]
                    x = [unicode(self.main.locale.standaloneDayName(i+1)) for i in range(7)]
                
                elif period == StatisticPeriod.Hours:
                    y1 = [0 for i in range(24)]
                    x = [str(QTime(i,  0,  0).toString("hh:mm")) for i in range(24)]
                
                if get.request().type() == MessageType.All:
                    y2 = y1[:]
                else:
                    y2 = None
                
            html = ""

            if period == StatisticPeriod.YearsAndMonths:
                first = True
                curYear = None
            else:
                html += "<p><table border='1' cellspacing='2' cellpadding='3'>"
                html += self.tableHead(get)

            for line in get:
                if USE_MATPLOTLIB:
                    if period == StatisticPeriod.Years:
                        key = line.year() - get[0].year()
                    elif period == StatisticPeriod.YearsAndMonths:
                        first = get[0]
                        
                        key = line.year() - first.year() + 1
                        key *= 12
                        key -= first.month() - 1
                        key -= 12 - line.month()
                        
                        key -= 1
                    if period == StatisticPeriod.Months:
                        key = line.month() - 1
                    elif period == StatisticPeriod.Days:
                        key = line.day() - 1
                    elif period == StatisticPeriod.Weekdays:
                        key = line.weekday() -1
                    elif period == StatisticPeriod.Hours:
                        key = line.hour()

                    if request.type() == MessageType.All:
                        y1[key] = line.incoming()
                        
                        if self.graphLayout == StatisticGraphLayout.Stacked:
                            y2[key] = line.total()
                        elif self.graphLayout == StatisticGraphLayout.Separate:
                            y2[key] = -line.outgoing()
                        
                    else:
                        if line.incoming() != None:
                            y1[key] = line.incoming()
                        else:
                            y1[key] = line.outgoing()

                if period == StatisticPeriod.YearsAndMonths:
                    if line.year() != curYear:
                        if first:
                            first = not first
                        else:
                            html += "</table></p>"

                        html += "<p><h3><a href='#Year_" + str(line.year()) + "' title='" + str(line.year()) + "'>" + str(line.year()) + "</a></h3></p>"
                        html += "<p><table border='1' cellspacing='2' cellpadding='3'>"
                        html += self.tableHead(get)
                        curYear = line.year()

                html += self.tableLine(line,  period != StatisticPeriod.YearsAndMonths)

            if not get:
                if get.request().contact():
                    html += "<p><b>" + self.tr("No data for this contact available!") + "</b></p>"
                else:
                    html += "<p><b>" + self.tr("No data available!") + "</b></p>"
            
            html += "</table></p>"
            
            if period != StatisticPeriod.YearsAndMonths and self.viewBox.currentIndex() == 0:
                html += "<p><a href='#YearsAndMonths'><b>" + self.tr("go back to summary...") + "</b></a></p>"
            elif period != StatisticPeriod.Years and self.viewBox.currentIndex() == 1:
                html += "<p><a href='#Years'><b>" + self.tr("go back to summary...") + "</b></a></p>"
            elif period != StatisticPeriod.Months and self.viewBox.currentIndex() == 2:
                html += "<p><a href='#Months'><b>" + self.tr("go back to summary...") + "</b></a></p>"
            elif period != StatisticPeriod.Days and self.viewBox.currentIndex() == 3:
                html += "<p><a href='#Days'><b>" + self.tr("go back to summary...") + "</b></a></p>"
            
            self.infoBrowser.setHtml(html)

            if USE_MATPLOTLIB:
                self.statisticPlot.ytitle= self.tr("All Messages")
                
                if get: 
                    if y1 and y2:
                        self.fill_plot(x,  y1,  0,  'green',  unicode(self.tr("Incoming messages")))
                        if self.graphLayout == StatisticGraphLayout.Stacked:
                            self.fill_plot(x,  y1,  y2,  'red',  unicode(self.tr("Outgoing messages")))
                        elif self.graphLayout == StatisticGraphLayout.Separate:
                            self.statisticPlot.ax.yaxis.set_major_formatter(PositiveFormatter())
                            self.fill_plot(x,  y2,  0,  'red',  unicode(self.tr("Outgoing messages")))
                    elif request.type() == MessageType.Incoming:
                        self.fill_plot(x,  y1,  0,  'green',  unicode(self.tr("Incoming messages")))
                        self.statisticPlot.ytitle= self.tr("Incoming Messages")
                    elif request.type() == MessageType.Outgoing:
                        self.fill_plot(x,  y1,  0,  'red',  unicode(self.tr("Outgoing messages")))
                        self.statisticPlot.ytitle= self.tr("Outgoing Messages")

                    self.statisticPlot.ax.legend(shadow=True,  loc='best',  prop=FontProperties(size=8))
                    self.statisticPlot.fig.autofmt_xdate()

                    self.statisticPlot.draw()

        elif self.statisticTab.currentIndex() == 1:
            request = StatisticsRequest()
            request.setStatisticFor(StatisticFor.Contacts)
            request.setRange(0,  14)

            if self.filterBox.currentIndex() == 0:
                request.setType(MessageType.All)
            elif self.filterBox.currentIndex() == 1:
                request.setType(MessageType.Incoming)
            else:
                request.setType(MessageType.Outgoing)

            get = self.database.statistics(request)
            general = self.database.statisticsGeneral()

            if USE_MATPLOTLIB:
                labels = list()
                fracs = list()

            html = "<table border='1' cellspacing='2' cellpadding='3'>"
            html += "<tr><th>" + self.tr("Contact") + "</th><th>" + self.tr("Percent") + "</th><th>" + self.tr("Incoming") + "</th>" + \
                                           "<th>" + self.tr("Outgoing") + "</th><th>" + self.tr("Total") + "</th></tr>"

            sum_incoming,  sum_outgoing,  sum_total,  i = 0, 0, 0,  0
            for contact,  incoming,  outgoing,  total in get:
                i += 1
                sum_incoming += incoming
                sum_outgoing += outgoing
                sum_total += total

                if USE_MATPLOTLIB:
                    if i < 5:
                        labels.append(contact.name())
                        fracs.append(float(total)/general["total"]*100)
                    elif i == 5:
                        labels.append(unicode(self.tr("Others")))
                        fracs.append(float(general["total"]-sum_total)/general["total"]*100)

                html += "<tr><td>" + contact.name() + "</td><td>" + '%.3f' % (float(total)/general["total"]*100) + "%" + \
                "</td><td>" + str(incoming) + "</td>" + "<td>" + str(outgoing) + "</td><td><b>" + str(total) + "</b></td></td>"

            if general["total"]-sum_total > 0:
                html += "<tr><td><i>" + self.tr("Others") + "</i></td><td>" + '%.3f' % (float(general["total"]-sum_total)/general["total"]*100) + \
                "%</td><td>" + str(general["incoming"]-sum_incoming) + "</td>" + "<td>" + str(general["outgoing"]-sum_outgoing) + \
                "</td><td><b>" + str(general["total"]-sum_total) + "</b></td></td>"

            html += "<tr><td><b><u>" + self.tr("Total") + "</u></b></td><td>100%" + \
            "</td><td>" + str(general["incoming"]) + "</td>" + "<td>" + str(general["outgoing"]) + \
            "</td><td><b>" + str(general["total"]) + "</b></td></td>"

            html += "</table>"
            
            if not get:
                html = self.tr("No data available!")
            
            self.contactInfo.setHtml(html)

            if USE_MATPLOTLIB:
                if get:
                    explode=(0.05, 0, 0, 0,  0)

                    patches,  texts,  autotexts = self.contactPlot.ax.pie(fracs,  labels=labels,  explode=explode,  autopct='%1.1f%%', shadow=True,
                                                                          labeldistance=1.1)
                    for i in texts:
                        i.set_size(8)
                    for i in autotexts:
                        i.set_size(7)
                    self.contactPlot.ax.set_aspect("equal")
                    self.contactPlot.format_labels()

        elif self.statisticTab.currentIndex() == 2:
            general = self.database.statisticsGeneral()
            
            if general["days"] == 0:
                incomingPerDay = 0
                outgoingPerDay = 0
            else:
                incomingPerDay = general["incoming"]/general["days"]
                outgoingPerDay = general["outgoing"]/general["days"]
            
            self.generalBrowser.setText(self.tr("""<p><b>General statistics</b></p>
            <p><b>%1</b> incoming messages, <b>%2</b> outgoing messages, <b>%3</b> total messages.<br />
            The total number of stored days is <b>%4</b>.<br />
            You receive <b>%5</b> and send <b>%6</b> messages per day on average.<br />
            There are alltogether <b>%7</b> contacts in my database, <b>%8</b> of them are shown on your mobile phone.<br />
            The average length of an incoming message is <b>%9</b> chars, of an outgoing message <b>%10</b> chars.</p>""").arg(general["incoming"]).arg(general["outgoing"]).arg(general["total"]).arg(general["days"]).arg(incomingPerDay).arg(outgoingPerDay).arg(general["contacts"]).arg(general["contactsShown"]).arg(general["incoming_avglength"]).arg(general["outgoing_avglength"]))

    def fill_plot(self,  x,  y1,  y2=0,  color='black',  label=''):
        ticks = list()
        if isinstance(x[0],  basestring):
            ticks = x
            x = range(len(x))

        self.statisticPlot.ax.plot(x, y1, color=color,  label=label)
        self.statisticPlot.ax.fill_between(x,  y2,  y1,  facecolor=color)
        self.statisticPlot.ax.plot(x, y1,  color='black')

        self.statisticPlot.ax.set_xbound(x[0],  x[len(x)-1])

        if ticks:
            self.statisticPlot.ax.set_xticks(range(len(x)))
            self.statisticPlot.ax.set_xticklabels(ticks)

    def tableHead(self,  respone):
        period = respone.request().period()

        ret = "<tr>"

        if respone.containsYear() and period != StatisticPeriod.YearsAndMonths:
            ret += "<th>" +  self.tr("Year") + "</th>"
        if respone.containsMonth():
            ret += "<th>" +  self.tr("Month") + "</th>"
        if respone.containsDay():
            ret += "<th>" +  self.tr("Day") + "</th>"
        if respone.containsWeekday():
            ret += "<th>" +  self.tr("Weekday") + "</th>"
        if respone.containsHour():
            ret += "<th>" +  self.tr("Hour") + "</th>"
        if respone.containsIncoming():
            ret += "<th>" +  self.tr("Incoming") + "</th>"
        if respone.containsOutgoing():
            ret += "<th>" +  self.tr("Outgoing") + "</th>"
        if respone.containsTotal():
            ret += "<th>" +  self.tr("Total") + "</th>"

        ret += "</tr>"
        return ret

    def tableLine(self,  line,  showYear=True):
        ret = "<tr>"
        href = ""
        if line.year() != None:
            href += "#Year_" + str(line.year())
            title = str(line.year())
            if showYear:
                ret += "<td><b><a title='" + title + "' href='" + href + "'>" + str(line.year()) + "</a></b></td>"

        if line.month() != None:
            href += "#Month_" + str(line.month())

            if line.year() != None:
                title = QDate(line.year(),  line.month(),  1).toString("MMMM yyyy")
            else:
                title = self.main.locale.standaloneMonthName(line.month())

            ret += "<td><b><a title='" + title + "' href='" + href + "'>" + self.main.locale.standaloneMonthName(line.month()) + "</a></b></td>"

        if line.day() != None:
            href += "#Day_" + str(line.day())

            if line.year() != None and line.month() != None:
                title = QDate(line.year(),  line.month(),  line.day()).toString("dd. MMMM yyyy")
            else:
                title = str(line.day())

            ret += "<td><b><a title='" + title + "' href='" + href + "'>" + str(line.day()) + "</a></b></td>"

        if line.weekday() != None:
            ret += "<td><b>" + self.main.locale.standaloneDayName(line.weekday()) + "</a></b></td>"

        if line.hour() != None:
            ret += "<td><b>" + QTime(line.hour(),  0,  0).toString("hh:mm") + "</b></td>"

        if line.incoming() != None:
            ret += "<td>" + str(line.incoming()) + "</td>"

        if line.outgoing() != None:
            ret += "<td>" + str(line.outgoing()) + "</td>"

        if line.total() != None:
            ret += "<td>" + str(line.total()) + "</td>"

        ret += "</tr>"
        return ret

    def stackedGraph(self):
        if self.graphLayout != StatisticGraphLayout.Stacked:
            self.graphLayout = StatisticGraphLayout.Stacked
            self.refreshStatistic(reset=False)

    def separateGraph(self):
        if self.graphLayout != StatisticGraphLayout.Separate:
            self.graphLayout = StatisticGraphLayout.Separate
            self.refreshStatistic(reset=False)
