# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

import base64
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_contacts_edit
import ui.ui_contacts_edit_name
import ui.ui_contacts_edit_address
import widget.ImageButton
from lib.classes import *

# FIXME! Workaround for broken QFormLayout.setLayout
# Remove this when we no longer support Python 2.5
# BUG: http://www.riverbankcomputing.com/pipermail/pyqt/2009-March/022407.html
def QFormLayout_addLayout(self, layout, row, column, rowSpan, columnSpan, alignment=0):
    if column == 0:
        role = QFormLayout.LabelRole
    else:
        role = QFormLayout.FieldRole
    if rowSpan != 1 or columnSpan != 1:
        raise ValueError('rowSpan and columnSpan must be 1')
    self.setLayout(row, role, layout)

QFormLayout.addLayout = QFormLayout_addLayout

class ContactsEdit(QDialog,  ui.ui_contacts_edit.Ui_ContactsEdit):
    def __init__(self, parent, main,  contact=None):
        super(ContactsEdit,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper
        
        self.contact = contact

        self.setupUi(self)
        main.setupButtonBox(self.buttonBox)
        
        # Change color of the TextBrowser to a normal background color
        pal = QPalette()
        pal.setColor(QPalette.Base,  self.palette().color(QPalette.Window))
        self.general_address.setPalette(pal)
        self.home_address.setPalette(pal)
        self.business_address.setPalette(pal)
        
        self.preserveValues = list()
        self.removeLineButtons = list()

        self.generateDialogs()
        self.generateList()
        self.retranslateFields()
        self.makeConnections()
        
        self.connect(self.buttonBox,  SIGNAL("clicked ( QAbstractButton * )"),  self.clickedButton)
        
        if contact:
            self.setWindowTitle(self.tr("Edit contact \"%1\"...").arg(contact.name()))
            self.setWindowIcon(QIcon(":/user-properties"))
            self.showContact(contact)
        else:
            self.setWindowIcon(QIcon(":/list-add-user"))
        
       
        self.show()
    
    def generateDialogs(self):
        self.editNameDialog = QDialog()
        self.editGeneralAddressDialog = QDialog()
        self.editHomeAddressDialog = QDialog()
        self.editBusinessAddressDialog = QDialog()
        
        self.editName = ui.ui_contacts_edit_name.Ui_ContactsEditName()
        self.editName.setupUi(self.editNameDialog)
        self.main.setupButtonBox(self.editName.buttonBox)

        self.editGeneralAddress = ui.ui_contacts_edit_address.Ui_ContactsEditAddress()
        self.editGeneralAddress.setupUi(self.editGeneralAddressDialog)
        self.main.setupButtonBox(self.editGeneralAddress.buttonBox)

        self.editHomeAddress = ui.ui_contacts_edit_address.Ui_ContactsEditAddress()
        self.editHomeAddress.setupUi(self.editHomeAddressDialog)
        self.main.setupButtonBox(self.editHomeAddress.buttonBox)

        self.editBusinessAddress = ui.ui_contacts_edit_address.Ui_ContactsEditAddress()
        self.editBusinessAddress.setupUi(self.editBusinessAddressDialog)
        self.main.setupButtonBox(self.editBusinessAddress.buttonBox)
        
        self.connect(self.editNameButton,  SIGNAL("clicked()"),  self.editNameDialog,  SLOT("show()"))
        self.connect(self.editGeneralAddressButton,  SIGNAL("clicked()"),  self.editGeneralAddressDialog,  SLOT("show()"))
        self.connect(self.editHomeAddressButton,  SIGNAL("clicked()"),  self.editHomeAddressDialog,  SLOT("show()"))
        self.connect(self.editBusinessAddressButton,  SIGNAL("clicked()"),  self.editBusinessAddressDialog,  SLOT("show()"))
        
        self.connect(self.editName.last_name,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateName())
        self.connect(self.editName.first_name ,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateName())
        self.connect(self.editName.title,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateName())
        self.connect(self.editName.suffix,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateName())
        
        self.connect(self.editGeneralAddress.po_box,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("none"))
        self.connect(self.editGeneralAddress.extension,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("none"))
        self.connect(self.editGeneralAddress.street,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("none"))
        self.connect(self.editGeneralAddress.zip_code,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("none"))
        self.connect(self.editGeneralAddress.city,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("none"))
        self.connect(self.editGeneralAddress.state,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("none"))
        self.connect(self.editGeneralAddress.country,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("none"))
        
        self.connect(self.editHomeAddress.po_box,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("home"))
        self.connect(self.editHomeAddress.extension,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("home"))
        self.connect(self.editHomeAddress.street,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("home"))
        self.connect(self.editHomeAddress.zip_code,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("home"))
        self.connect(self.editHomeAddress.city,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("home"))
        self.connect(self.editHomeAddress.state,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("home"))
        self.connect(self.editHomeAddress.country,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("home"))
        
        self.connect(self.editBusinessAddress.po_box,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("work"))
        self.connect(self.editBusinessAddress.extension,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("work"))
        self.connect(self.editBusinessAddress.street,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("work"))
        self.connect(self.editBusinessAddress.zip_code,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("work"))
        self.connect(self.editBusinessAddress.city,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("work"))
        self.connect(self.editBusinessAddress.state,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("work"))
        self.connect(self.editBusinessAddress.country,  SIGNAL("textChanged( const QString & )"),  lambda x : self.updateAddress("work"))
    
    def generateList(self):
        self.fields = dict()
        self.fields["none"] = { "last_name" : [],  "first_name" : [],  "job_title" : [],  "company_name" : [],  "phone_number" : [],  "mobile_number" : [], 
                               "pager_number" : [],  "fax_number" : [],  "email_address" : [],  "url" : [],  "postal_address" : [], "po_box" : [], 
                               "extended_address" : [],  "street_address" : [],  "postal_code" : [],  "city" : [],  "state" : [],  "country" : [],  
                               "dtmf_string" : [],  "date" : [],  "note" : [],  "thumbnail_image" : [],  "prefix" : [],  "suffix" : [],  "second_name" : [], 
                               "video_number" : [],  "voip" : [],  "push_to_talk" : [],  "share_view" : [],  "sip_id" : [] }
        self.fields["home"] = { "phone_number" : [], "mobile_number" : [],  "fax_number" : [],  "email_address" : [],  "url" : [],  "postal_address" : [], 
                               "po_box" : [],  "extended_address" : [],  "street_address" : [],  "postal_code" : [],  "city" : [],  "state" : [],  "country" : [], 
                              "video_number" : [],  "voip" : [] }
        self.fields["work"] = { "phone_number" : [],  "mobile_number" : [],  "fax_number" : [],  "email_address" : [],  "url" : [],  "postal_address" : [], 
                               "po_box" : [],  "extended_address" : [],  "street_address" : [],  "postal_code" : [],  "city" : [],  "state" : [],  "country" : [], 
                              "video_number" : [],  "voip" : [] }
        
        self.fields["none"]["last_name"].append( self.editName.last_name )
        self.fields["none"]["first_name"].append( self.editName.first_name )
        self.fields["none"]["job_title"].append( self.jobtitle_1 )
        self.fields["none"]["company_name"].append( self.company )
        self.fields["none"]["phone_number"].append( self.general_telephone_1 )
        self.fields["none"]["mobile_number"].append( self.general_mobile_1 )
        self.fields["none"]["pager_number"].append( self.general_pager_1 )
        self.fields["none"]["fax_number"].append( self.general_fax_1 )
        self.fields["none"]["email_address"].append( self.general_mail_1 )
        self.fields["none"]["url"].append( self.general_web_1 )
        self.fields["none"]["postal_address"].append( self.editGeneralAddress.street )
        self.fields["none"]["po_box"].append( self.editGeneralAddress.po_box )
        self.fields["none"]["extended_address"].append( self.editGeneralAddress.extension )
        # street_address gets stored as postal_address
        #self.fields["none"]["street_address"].append( self.editGeneralAddress.street )   WTF?
        self.fields["none"]["postal_code"].append( self.editGeneralAddress.zip_code )
        self.fields["none"]["city"].append( self.editGeneralAddress.city )
        self.fields["none"]["state"].append( self.editGeneralAddress.state )
        self.fields["none"]["country"].append( self.editGeneralAddress.country )
        self.fields["none"]["dtmf_string"].append( self.general_dtmf_1 )
        self.fields["none"]["date"].append( self.birthday )
        self.fields["none"]["note"].append( self.notes_1 )
        self.fields["none"]["thumbnail_image"].append( self.thumbButton )
        self.fields["none"]["prefix"].append( self.editName.title )
        self.fields["none"]["suffix"].append( self.editName.suffix )
        self.fields["none"]["second_name"].append( self.nickname )
        self.fields["none"]["video_number"].append( self.general_video_1 )
        self.fields["none"]["voip"].append( self.general_internettel_1 )
        self.fields["none"]["push_to_talk"].append( self.general_ptt_1 )
        self.fields["none"]["share_view"].append( self.general_shareview_1 )
        self.fields["none"]["sip_id"].append( self.general_sip_1 )
        
        self.fields["home"]["phone_number"].append( self.home_telephone_1 )
        self.fields["home"]["mobile_number"].append( self.home_mobile_1 )
        self.fields["home"]["fax_number"].append( self.home_fax_1 )
        self.fields["home"]["email_address"].append( self.home_mail_1 )
        self.fields["home"]["url"].append( self.home_web_1 )
        self.fields["home"]["postal_address"].append( self.editHomeAddress.street )
        self.fields["home"]["po_box"].append( self.editHomeAddress.po_box )
        self.fields["home"]["extended_address"].append( self.editHomeAddress.extension )
        #self.fields["home"]["street_address"].append( self.editHomeAddress.street )
        self.fields["home"]["postal_code"].append( self.editHomeAddress.zip_code )
        self.fields["home"]["city"].append( self.editHomeAddress.city )
        self.fields["home"]["state"].append( self.editHomeAddress.state )
        self.fields["home"]["country"].append( self.editHomeAddress.country )
        self.fields["home"]["video_number"].append( self.home_video_1 )
        self.fields["home"]["voip"].append( self.home_internettel_1 )
    
        self.fields["work"]["phone_number"].append( self.business_telephone_1 )
        self.fields["work"]["mobile_number"].append( self.business_mobile_1 )
        self.fields["work"]["fax_number"].append( self.business_fax_1 )
        self.fields["work"]["email_address"].append( self.business_mail_1 )
        self.fields["work"]["url"].append( self.business_web_1 )
        self.fields["work"]["postal_address"].append( self.editBusinessAddress.street )
        self.fields["work"]["po_box"].append( self.editBusinessAddress.po_box )
        self.fields["work"]["extended_address"].append( self.editBusinessAddress.extension )
        #self.fields["work"]["street_address"].append( self.editBusinessAddress.street )
        self.fields["work"]["postal_code"].append( self.editBusinessAddress.zip_code )
        self.fields["work"]["city"].append( self.editBusinessAddress.city )
        self.fields["work"]["state"].append( self.editBusinessAddress.state )
        self.fields["work"]["country"].append( self.editBusinessAddress.country )
        self.fields["work"]["video_number"].append( self.business_video_1 )
        self.fields["work"]["voip"].append( self.business_internettel_1 )
    
    def makeConnections(self):
        self.connect(self.add_jobtitle,  SIGNAL("clicked()"),  lambda : self.add(ContactField("job_title",  "none")))
        
        self.connect(self.add_general_telephone,  SIGNAL("clicked()"),  lambda : self.add(ContactField("phone_number",  "none")))
        self.connect(self.add_general_mobile,  SIGNAL("clicked()"),  lambda : self.add(ContactField("mobile_number",  "none")))
        self.connect(self.add_general_video,  SIGNAL("clicked()"),  lambda : self.add(ContactField("video_number",  "none")))
        self.connect(self.add_general_fax,  SIGNAL("clicked()"),  lambda : self.add(ContactField("fax_number",  "none")))
        self.connect(self.add_general_pager,  SIGNAL("clicked()"),  lambda : self.add(ContactField("pager_number",  "none")))
        self.connect(self.add_general_internettel,  SIGNAL("clicked()"),  lambda : self.add(ContactField("voip",  "none")))
        self.connect(self.add_general_ptt,  SIGNAL("clicked()"),  lambda : self.add(ContactField("push_to_talk",  "none")))
        self.connect(self.add_general_shareview,  SIGNAL("clicked()"),  lambda : self.add(ContactField("share_view",  "none")))
        self.connect(self.add_general_sip,  SIGNAL("clicked()"),  lambda : self.add(ContactField("sip_id",  "none")))
        self.connect(self.add_general_mail,  SIGNAL("clicked()"),  lambda : self.add(ContactField("email_address",  "none")))
        self.connect(self.add_general_web,  SIGNAL("clicked()"),  lambda : self.add(ContactField("url",  "none")))
        self.connect(self.add_general_dtmf,  SIGNAL("clicked()"),  lambda : self.add(ContactField("dtmf_string",  "none")))
        
        self.connect(self.add_home_telephone,  SIGNAL("clicked()"),  lambda : self.add(ContactField("phone_number",  "home")))
        self.connect(self.add_home_mobile,  SIGNAL("clicked()"),  lambda : self.add(ContactField("mobile_number",  "home")))
        self.connect(self.add_home_video,  SIGNAL("clicked()"),  lambda : self.add(ContactField("video_number",  "home")))
        self.connect(self.add_home_fax,  SIGNAL("clicked()"),  lambda : self.add(ContactField("fax_number",  "home")))
        self.connect(self.add_home_internettel,  SIGNAL("clicked()"),  lambda : self.add(ContactField("voip",  "home")))
        self.connect(self.add_home_mail,  SIGNAL("clicked()"),  lambda : self.add(ContactField("email_address",  "home")))
        self.connect(self.add_home_web,  SIGNAL("clicked()"),  lambda : self.add(ContactField("url",  "home")))

        self.connect(self.add_business_telephone,  SIGNAL("clicked()"),  lambda : self.add(ContactField("phone_number",  "work")))
        self.connect(self.add_business_mobile,  SIGNAL("clicked()"),  lambda : self.add(ContactField("mobile_number",  "work")))
        self.connect(self.add_business_video,  SIGNAL("clicked()"),  lambda : self.add(ContactField("video_number",  "work")))
        self.connect(self.add_business_fax,  SIGNAL("clicked()"),  lambda : self.add(ContactField("fax_number",  "work")))
        self.connect(self.add_business_internettel,  SIGNAL("clicked()"),  lambda : self.add(ContactField("voip",  "work")))
        self.connect(self.add_business_mail,  SIGNAL("clicked()"),  lambda : self.add(ContactField("email_address",  "work")))
        self.connect(self.add_business_web,  SIGNAL("clicked()"),  lambda : self.add(ContactField("url",  "work")))

        self.connect(self.add_note,  SIGNAL("clicked()"),  lambda : self.add(ContactField("note",  "none")))

    def retranslateFields(self):
        # Translate all strings correctly
        self.nickname_label.setText(ContactFields.SecondName.toString())
        self.company_label.setText(ContactFields.CompanyName.toString())
        self.jobtitle_label.setText(ContactFields.JobTitle.toString())
        self.birthday_label.setText(ContactFields.Date.toString())
        
        self.general_telephone_label.setText(ContactFields.PhoneNumber.toString())
        self.general_mobile_label.setText(ContactFields.MobileNumber.toString())
        self.general_video_label.setText(ContactFields.VideoNumber.toString())
        self.general_fax_label.setText(ContactFields.FaxNumber.toString())
        self.general_pager_label.setText(ContactFields.PagerNumber.toString())
        self.general_internettel_label.setText(ContactFields.Voip.toString())
        self.general_ptt_label.setText(ContactFields.PushToTalk.toString())
        self.general_shareview_label.setText(ContactFields.ShareView.toString())
        self.general_sip_label.setText(ContactFields.SipId.toString())
        self.general_mail_label.setText(ContactFields.EmailAddress.toString())
        self.general_web_label.setText(ContactFields.Url.toString())
        self.general_dtmf_label.setText(ContactFields.DtmfString.toString())
        
        self.home_telephone_label.setText(ContactFields.PhoneNumber.toString())
        self.home_mobile_label.setText(ContactFields.MobileNumber.toString())
        self.home_video_label.setText(ContactFields.VideoNumber.toString())
        self.home_fax_label.setText(ContactFields.FaxNumber.toString())
        self.home_internettel_label.setText(ContactFields.Voip.toString())
        self.home_mail_label.setText(ContactFields.EmailAddress.toString())
        self.home_web_label.setText(ContactFields.Url.toString())

        self.business_telephone_label.setText(ContactFields.PhoneNumber.toString())
        self.business_mobile_label.setText(ContactFields.MobileNumber.toString())
        self.business_video_label.setText(ContactFields.VideoNumber.toString())
        self.business_fax_label.setText(ContactFields.FaxNumber.toString())
        self.business_internettel_label.setText(ContactFields.Voip.toString())
        self.business_mail_label.setText(ContactFields.EmailAddress.toString())
        self.business_web_label.setText(ContactFields.Url.toString())

        self.editName.last_name_label.setText(ContactFields.LastName.toString())
        self.editName.first_name_label.setText(ContactFields.FirstName.toString())
        self.editName.title_label.setText(ContactFields.Prefix.toString())
        self.editName.suffix_label.setText(ContactFields.Suffix.toString())

        for loc in [self.editGeneralAddress,  self.editHomeAddress,  self.editBusinessAddress]:
            loc.po_box_label.setText(ContactFields.PoBox.toString())
            loc.extension_label.setText(ContactFields.ExtendedAddress.toString())
            loc.street_label.setText(ContactFields.StreetAddress.toString())
            loc.zip_code_label.setText(ContactFields.PostalCode.toString())
            loc.city_label.setText(ContactFields.City.toString())
            loc.state_label.setText(ContactFields.State.toString())
            loc.country_label.setText(ContactFields.Country.toString())

    def add(self,  field):
        listField = self.fields[field.location()][field.type()]
        
        if field.type() == "job_title":
            layout = self.jobLayout
        elif field.type() == "note":
            layout = self.notesLayout
        elif field.location() == "none":
            layout = self.generalNumbersLayout
        elif field.location() == "home":
            layout = self.homeNumbersLayout
        elif field.location() == "work":
            layout = self.businessNumbersLayout

        if not field.type() == "note":
            for item in range(layout.rowCount()):
                layoutitem = layout.itemAt(item,  QFormLayout.LabelRole)
                if layoutitem != None:
                    text = layoutitem.widget().text()                    
                    if text == field.toString():
                        pos = item
                        num = 1
                    elif unicode(text).startswith(unicode(field.toString())[:-1]):
                        pos = item
                        num = int(unicode(text).rsplit("(", 1)[1].split(")", 1)[0])

        if field.type() == "note":
            addLayout = QVBoxLayout()
            addLineEdit = QTextEdit()
        else:
            addLayout = QHBoxLayout()
            addLineEdit = QLineEdit()
        
        addButton = QToolButton()
        addButton.setIcon(QIcon(":/list-remove"))
        
        self.removeLineButtons.append(addButton)
        
        addLayout.addWidget(addLineEdit)
        addLayout.addWidget(addButton)
        
        if field.type() == "note":
            layout.addLayout(addLayout)
        else:
            layout.insertRow(pos+1,  field.toString(num+1),  addLayout)
        listField.append(addLineEdit)
        
        self.connect(addButton,  SIGNAL("clicked()"),  lambda : self.deleteRow(layout,  addLineEdit,  addButton,  addLayout,  field.type()!="note"))
        self.connect(addButton,  SIGNAL("clicked()"),  lambda : self.deleteField(listField,  addLineEdit))

    def deleteRow(self,  layout,  line,  button,  myLayout,  reparentLabel):
        try:
            line.setParent(None)
            button.setParent(None)
            if reparentLabel:
                layout.labelForField(myLayout).setParent(None)
            myLayout.setParent(None)
        except:
            pass
    
    def deleteField(self,  listField,  lineEdit):
        try:
            listField.remove(lineEdit)
        except:
            pass

    def showContact(self,  contact):
        self.preserveValues = list()
        for field,  value in contact:
            try:
                fieldList = self.fields[field.location()][field.type()]
                last = fieldList[len(fieldList)-1]
            except:
                self.preserveValues.append((field,  value))
                continue
            
            if isinstance(last,  QLineEdit):
                if last.text():
                    self.add(field)
            elif isinstance(last,  QTextEdit):
                if last.toPlainText():
                    self.add(field)
            elif isinstance(last,  QDateEdit):
                if last.date() != QDate(2000,  1,  1):
                    self.add(field)

            last = fieldList[len(fieldList)-1]
            if field.isPicture():
                data = base64.decodestring(value)
                image = QImage().fromData(data)
                pixmap = QPixmap().fromImage(image)
                last.setPicture(pixmap,  value)
                last.updateGui()
            else:
                if isinstance(last,  QLineEdit):
                    last.setText(value)
                elif isinstance(last,  QTextEdit):
                    last.setText(value)
                elif isinstance(last,  QDateEdit):
                    value = QDate.fromString(value,  "yyyyMMdd")
                    last.setDate(value)
    
    def updateName(self):
        title = first = unicode(self.editName.title.text())
        first = unicode(self.editName.first_name.text())
        last = unicode(self.editName.last_name.text())
        suffix = unicode(self.editName.suffix.text())
        
        name = ""
        
        if title:
            name += title + " "
        if first:
            name += first + " "
        if last:
            name += last + " "
        if suffix:
            name += suffix + " "
        self.name.setText(name)
    
    def updateAddress(self,  location):
        if location == "home":
            browser = self.home_address
        elif location == "work":
            browser = self.business_address
        else:
            browser = self.general_address
        
        browser.clear()
        
        street = unicode(self.fields[location]["postal_address"][0].text())
        po_box = unicode(self.fields[location]["po_box"][0].text())
        extension = unicode(self.fields[location]["extended_address"][0].text())
        postal_code = unicode(self.fields[location]["postal_code"][0].text())
        city = unicode(self.fields[location]["city"][0].text())
        state = unicode(self.fields[location]["state"][0].text())
        country = unicode(self.fields[location]["country"][0].text())
        
        if street and po_box:
            browser.insertPlainText(street + " " + po_box + '\n')
        elif street:
            browser.insertPlainText(street +'\n')
        elif po_box:
            browser.insertPlainText(po_box +'\n')
        
        if extension:
            browser.insertPlainText(extension + '\n')
        
        if postal_code and city:
            browser.insertPlainText(postal_code + " " + city + '\n')
        elif postal_code:
            browser.insertPlainText(postal_code +'\n')
        elif city:
            browser.insertPlainText(city +'\n')

        if state:
            browser.insertPlainText(state + '\n')
        if country:
            browser.insertPlainText(country + '\n')
    
    def reset(self):
        for button in self.removeLineButtons:
            button.click()

        for location in self.fields.keys():
            for type in self.fields[location].keys():
                for entry in self.fields[location][type]:
                    if type == "date":
                        entry.setDate(QDate(2000,  1,  1))
                    else:
                        entry.clear()
    
    def clickedButton(self,  button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ResetRole:
            self.reset()
            if self.contact:
                self.showContact(self.contact)

    def accept(self):
        if not self.connection.connected():
            QMessageBox.critical(None,
                self.tr("No active connection."),
                self.tr("""You aren't connected to a mobile phone.
All changes will get lost."""),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            self.close()
        
        if self.contact:
            contact = Contact(id=self.contact.id(),  idOnPhone=self.contact.idOnPhone())
        else:
            contact = Contact()

        first = unicode(self.editName.first_name.text())
        last = unicode(self.editName.last_name.text())
        
        if first and last:
            name = last + " " + first
        elif first:
            name = first
        else:
            name = last

        contact.setName(name)
        
        for location in self.fields.keys():
            for type in self.fields[location].keys():
                for entry in self.fields[location][type]:
                    if isinstance(entry,  QLineEdit):
                        if entry.text():
                            contact.addValue(ContactField(type,  location),  unicode(entry.text()))
                    elif isinstance(entry,  QTextEdit):
                        if entry.toPlainText():
                            contact.addValue(ContactField(type,  location),  unicode(entry.toPlainText()))
                    elif isinstance(entry,  QDateEdit):
                        if entry.date() != QDate(2000,  1,  1):
                            date = entry.date().toString("yyyyMMdd")
                            contact.addValue(ContactField(type,  location),  unicode(date))
                    elif isinstance(entry,  widget.ImageButton.ImageButton):
                        if entry.data():
                            contact.addValue(ContactField(type,  location),  unicode(entry.data()))
                    else:
                        self.log.error(QString("Unhandled type: %1").arg(str(entry)))
        
        for field,  value in self.preserveValues:
            contact.addValue(field,  value)
        
        if self.contact:
            remove,  add = self.database.contactChange(contact)
            self.connection.contactChange(contact,  remove,  add)
        else:
            #contact.setId(self.database.contactAdd(contact))
            self.connection.contactAdd(contact)
        
        self.close()
        self.main.emit(SIGNAL("updateContact"),  contact)
