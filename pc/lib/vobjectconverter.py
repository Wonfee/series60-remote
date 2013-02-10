# -*- coding: utf-8 -*-

# Copyright (c) 2010 Pierre-Yves Chibon <py@chibon.fr>

from lib.classes import Contact, ContactField

try:
    import vobject
    VOBJECT_FOUND = True
except ImportError:
    VOBJECT_FOUND = False

class VObjectConverter:

    def __init__(self):
        """
        Init the converter
        Returns False if the python-vobject module could not be imported
        """

        self.address_fields = [  'city', 'country', 'extended_address', 'po_box',
                                'postal_code', 'state', 'street_address']

    @staticmethod
    def missingModules():
       if not VOBJECT_FOUND:
          return "python-vobject"
       return ""

    def convertToVObject(self, contact):
        """ Convert a contact object into a vCard object """
        c = vobject.vCard()
        last_name = ""
        first_name = ""
        self.dict_address = {}

        for field,  value in contact:
            if field.type() == 'last_name':
                last_name = unicode(value)
            elif field.type() == 'first_name':
                first_name = unicode(value)

            elif field.type() == 'phone_number' \
                        or field.type() == 'mobile_number' \
                        or field.type() == 'fax_number':

                c.add('tel').value = unicode(value)
                if field.type() == 'mobile_number':
                    if field.location() != 'none':
                        c.tel_list[-1].type_param = ["CELL",
                            field.location().upper()]
                    else:
                        c.tel_list[-1].type_param = "CELL"
                elif field.type() == 'fax_number':
                    if field.location() != 'none':
                        c.tel_list[-1].type_param = ["FAX",
                            field.location().upper()]
                    else:
                        c.tel_list[-1].type_param = "FAX"
                else:
                    if field.location() != 'none':
                        c.tel_list[-1].type_param = field.location().upper()

            elif field.type() == 'email_address' and value != 'none':
                c.add('email').value = unicode(value)
                if field.location() != 'none':
                    c.email_list[-1].type_param = field.location().upper()

            elif field.type() == 'url' and value != 'none':
                c.add('url').value = unicode(value)
                if field.location() != 'none':
                    c.url_list[-1].type_param = field.location().upper()

            elif field.type() == 'company_name' and value != 'none':
                c.add('org').value = [unicode(value)]

            elif field.type() == 'job_title' and value != 'none':
                c.add('role').value = unicode(value)

            elif field.type() == 'date':
                c.add('bday').value = unicode(value)
                if field.location() != 'none':
                    c.bday_list[-1].type_param = field.location().upper()

            elif field.type() in self.address_fields:
                # If address location not know yet
                if not field.location() in self.dict_address.keys():
                    # add it to the dict
                    self.dict_address[field.location()] = vobject.vcard.Address()

                # Set the attribute of each address according to their location
                if field.type() == 'street_address':
                    self.dict_address[field.location()].street = unicode(value)
                elif field.type() == 'state':
                    self.dict_address[field.location()].region = unicode(value)
                elif field.type() == 'postal_code':
                    self.dict_address[field.location()].code = unicode(value)
                elif field.type() == 'po_box':
                    self.dict_address[field.location()].box = unicode(value)
                elif field.type() == 'extended_address':
                    self.dict_address[field.location()].extended = unicode(value)
                elif field.type() == 'country':
                    self.dict_address[field.location()].country = unicode(value)
                elif field.type() == 'city':
                    self.dict_address[field.location()].city = unicode(value)

            elif field.isPicture():
                pic = c.add('photo')
                pic.type_param = "JPEG"
                pic.encoding_param = "BASE64"
                pic.value = unicode(value)

        # Add the addresses to the object
        cnt = 0
        for k in self.dict_address.keys():
            c.add('adr').value = self.dict_address[k]
            c.adr_list[cnt].type_param = k.upper()
            cnt += 1

        # Add Name and Full Name to the object
        c.add('n')
        c.n.value = vobject.vcard.Name( family = last_name, given = first_name )
        c.add('fn')
        c.fn.value = '%s %s' %(first_name, last_name)

        return c

    def importVCardToContact(self, filename):
        """ Import a list of vCard from a file """
        file = open(filename, 'r')
        contactfile = file.read()
        file.close()
        return vobject.readComponents(contactfile)

    def convertToContact(self, c):
        """ Convert a Contact object to a vCard object """
        con = Contact(name = c.fn.value )
        flagaddress = True
        for el in c.getSortedChildren():
            #if len(el.params.keys()) > 0:
                #print el.name, el.params[u'TYPE'], el.value
            #else:
                #print el.name, el.value

            if el.name == 'N':
                con.addValue(ContactField('last_name', 'none'),
                        unicode(c.n.value.family))
                con.addValue(ContactField('first_name', 'none'),
                        unicode(c.n.value.given))
            elif el.name == 'ROLE':
                con.addValue(ContactField('job_title', 'none'),
                        unicode(el.value))
            elif el.name == 'ORG':
                for val in el.value:
                    con.addValue(ContactField('company_name', 'none'),
                        unicode(val))
            elif el.name == 'BDAY':
                con.addValue(ContactField('date', 'none'),
                        unicode(el.value))
            elif el.name == 'URL':
                con.addValue(ContactField('url', 'none'),
                        unicode(el.value))
            elif el.name == 'TEL':
                if len(el.params.keys()) == 0:
                    #print 'tel none'
                    con.addValue(ContactField('phone_number', 'none'),
                        unicode(el.value))
                else:
                    params = el.params[u'TYPE']
                    if len(params) == 1:
                        if u'HOME' in params:
                            #print 'tel home'
                            con.addValue(ContactField('phone_number', 'home'),
                                unicode(el.value))
                        elif u'WORK' in params:
                            #print 'tel work'
                            con.addValue(ContactField('phone_number', 'work'),
                                unicode(el.value))
                        elif u'CELL' in params:
                            #print 'cell none'
                            con.addValue(ContactField('mobile_number', 'none'),
                                unicode(el.value))
                        elif u'FAX' in params:
                            #print 'fax none'
                            con.addValue(ContactField('fax_number', 'none'),
                                unicode(el.value))
                    elif len(params) == 2:
                        if u'HOME' in params and u'CELL' in params:
                            #print 'cell home'
                            con.addValue(
                                ContactField('mobile_number', 'home'),
                                unicode(el.value)
                            )
                        elif u'HOME' in params and u'FAX' in params:
                            #print 'fax home'
                            con.addValue(
                                ContactField('fax_number', 'home'),
                                unicode(el.value)
                            )
                        elif u'WORK' in params and u'CELL' in params:
                            #print 'cell work'
                            con.addValue(
                                ContactField('mobile_number', 'work'),
                                unicode(el.value)
                            )
                        elif u'WORK' in params and u'FAX' in params:
                            #print 'fax work'
                            con.addValue(
                                ContactField('fax_number', 'work'),
                                unicode(el.value)
                            )
            elif el.name == 'EMAIL':
                if len(el.params.keys()) == 0:
                    con.addValue(ContactField('email_address', 'none'),
                        unicode(el.value))
                else:
                    param = el.params[u'TYPE'][0]
                    con.addValue(ContactField('email_address', param.lower()),
                        unicode(el.value))
            elif el.name == 'ADR' and flagaddress:
                for adr in c.adr_list:
                    if len(adr.params.keys()) > 0:
                        location = unicode(adr.params[u'TYPE'][0].lower())
                    else:
                        location = u'none'
                    [po_box, extended_address, street_address,
                    city, state, postal_code, country] = \
                            adr.serialize().split(':')[1].split(';')
                    #print po_box, extended_address, street_address, \
                    #city, state, postal_code, country
                    if street_address.strip() != '':
                        con.addValue(ContactField('street_address', location),
                                    unicode(street_address.strip(), 'utf-8'))
                    if state.strip() != '':
                        con.addValue(ContactField('state', location),
                                    unicode(state.strip(), 'utf-8'))
                    if postal_code.strip() != '':
                        con.addValue(ContactField('postal_code', location),
                                    unicode(postal_code.strip(), 'utf-8'))
                    if po_box.strip() != '':
                        con.addValue(ContactField('po_box', location),
                                    unicode(po_box.strip(), 'utf-8'))
                    if extended_address.strip() != '':
                        con.addValue(ContactField('extended_address', location),
                                    unicode(extended_address.strip(), 'utf-8'))
                    if country.strip() != '':
                        con.addValue(ContactField('country', location),
                                    unicode(country.strip(), 'utf-8'))
                    if city.strip() != '':
                        con.addValue(ContactField('city', location),
                                    unicode(city.strip(), 'utf-8'))
                flagaddress = False
            #else:
                #if len(el.params.keys()) > 0:
                    #print el.name, el.params[u'TYPE'], el.value
                #else:
                    #print el.name, el.value
        return con
