# -*- coding: utf-8 -*-

# Copyright (c) 2010 Pierre-Yves Chibon <py@chibon.fr>

from lib.classes import Contact, ContactField

import sys
try:
    import ldif
    LDIF_FOUND = True
except ImportError:
    LDIF_FOUND = False

if LDIF_FOUND:
    class Series60LDIFParser(ldif.LDIFParser):
        def __init__(self, input, output = sys.stdout ):
            """ Initiate the parser """
            ldif.LDIFParser.__init__(self, input)
            self.writer = ldif.LDIFWriter(output)
            self.conversion = list()

        def handle(self, dn, entry):
            """ Actual business logic """
            self.conversion.append(LdifConverter().convertToContact(entry))

class LdifConverter:

    def __init__(self):
        """
        Init the converter
        Returns False if the python-ldap module could not be imported
        """

        self.address_fields = [  'city', 'country', 'extended_address', 'po_box',
                                'postal_code', 'state', 'street_address']

    @staticmethod
    def missingModules():
        if not LDIF_FOUND:
           return "python-ldap"
        return ""

    def convertToLdif(self, contact):
        """ Convert a contact object into a ldif object """
        entry = {'objectClass': ['top', 'person', 'organizationalPerson',
                'inetOrgPerson', 'mozillaAbPersonObsolete']}
        last_name = ""
        first_name = ""
        self.dict_address = {}

        for field,  value in contact:
            #print type(value), value

            if field.type() == 'last_name':
                last_name = value.encode('utf-8')
            elif field.type() == 'first_name':
                first_name = value.encode('utf-8')

            elif field.type() == 'phone_number' \
                        or field.type() == 'mobile_number' \
                        or field.type() == 'fax_number':

                if field.type() == 'mobile_number':
                    if 'mobile' in entry.keys():
                        entry['mobile'].append(value)
                    else:
                        entry['mobile'] = [value]

                elif field.type() == 'fax_number':
                    if 'fax' in entry.keys():
                        entry['fax'].append(value)
                    else:
                        entry['fax'] = [value]
                else:
                    if 'telephoneNumber' in entry.keys():
                        entry['telephoneNumber'].append(value)
                    else:
                        entry['telephoneNumber'] = [value]

            elif field.type() == 'email_address' and value != 'none':
                if 'email' in entry.keys():
                    entry['email'].append(value.encode('utf-8'))
                else:
                    entry['email'] = [value.encode('utf-8')]

            elif field.type() == 'url' and value != 'none':
                if field.location() != 'none':
                    if field.location.lower() == 'work':
                        if 'mozillaWorkUrl' in entry.keys():
                            entry['mozillaWorkUrl'].append(value.encode('utf-8'))
                        else:
                            entry['mozillaWorkUrl'] = [value.encode('utf-8')]
                    else:
                        if 'mozillaHomeUrl' in entry.keys():
                            entry['mozillaHomeUrl'].append(value.encode('utf-8'))
                        else:
                            entry['mozillaHomeUrl'] = [value.encode('utf-8')]
                else:
                    if 'url' in entry.keys():
                        entry['url'].append(value.encode('utf-8'))
                    else:
                        entry['url'] = [value.encode('utf-8')]

            elif field.type() == 'company_name' and value != 'none':
                if 'o' in entry.keys():
                    entry['o'].append(value.encode('utf-8'))
                else:
                    entry['o'] = [value.encode('utf-8')]

            elif field.type() == 'job_title' and value != 'none':
                if 'title' in entry.keys():
                    entry['title'].append(value.encode('utf-8'))
                else:
                    entry['title'] = [value.encode('utf-8')]

            elif field.type() == 'date':
                entry['birthyear'] = [value[0:4]]
                entry['birthmonth'] = [value[4:6]]
                entry['birthday'] = [value[6:8]]

            elif field.type() in self.address_fields:

                # Set the attribute of each address according to their location
                if field.type() == 'street_address':
                    if field.location().lower() == 'home':
                        if 'mozillaHomeStreet' in entry.keys():
                            entry['mozillaHomeStreet'].append(value.encode('utf-8'))
                        else:
                            entry['mozillaHomeStreet'] = [value.encode('utf-8')]
                    else:
                        if 'street' in entry.keys():
                            entry['street'].append(value.encode('utf-8'))
                        else:
                            entry['street'] = [value.encode('utf-8')]

                elif field.type() == 'state':
                    if field.location().lower() == 'home':
                        if 'mozillaHomeState' in entry.keys():
                            entry['mozillaHomeState'].append(value.encode('utf-8'))
                        else:
                            entry['mozillaHomeState'] = [value.encode('utf-8')]
                    else:
                        if 'st' in entry.keys():
                            entry['st'].append(value.encode('utf-8'))
                        else:
                            entry['st'] = [value.encode('utf-8')]

                elif field.type() == 'postal_code':
                    if field.location().lower() == 'home':
                        if 'mozillaHomePostalCode' in entry.keys():
                            entry['mozillaHomePostalCode'].append(value.encode('utf-8'))
                        else:
                            entry['mozillaHomePostalCode'] = [value.encode('utf-8')]
                    else:
                        if 'postalCode' in entry.keys():
                            entry['postalCode'].append(value.encode('utf-8'))
                        else:
                            entry['postalCode'] = [value.encode('utf-8')]

                elif field.type() == 'po_box':
                    if field.location().lower() == 'home':
                        if 'mozillaHomeStreet' in entry.keys():
                            entry['mozillaHomeStreet'].append(value.encode('utf-8'))
                        else:
                            entry['mozillaHomeStreet'] = [value.encode('utf-8')]
                    else:
                        if 'street' in entry.keys():
                            entry['street'].append(value.encode('utf-8'))
                        else:
                            entry['street'] = [value.encode('utf-8')]

                # not supported in ldif
                #elif field.type() == 'extended_address':

                elif field.type() == 'country':
                    if field.location().lower() == 'home':
                        if 'mozillaHomeCountryName' in entry.keys():
                            entry['mozillaHomeCountryName'].append(value.encode('utf-8'))
                        else:
                            entry['mozillaHomeCountryName'] = [value.encode('utf-8')]
                    else:
                        if 'c' in entry.keys():
                            entry['c'].append(value.encode('utf-8'))
                        else:
                            entry['c'] = [value.encode('utf-8')]

                elif field.type() == 'city':
                    if field.location().lower() == 'home':
                        if 'mozillaHomeLocalityName' in entry.keys():
                            entry['mozillaHomeLocalityName'].append(value.encode('utf-8'))
                        else:
                            entry['mozillaHomeLocalityName'] = [value.encode('utf-8')]
                    else:
                        if 'l' in entry.keys():
                            entry['l'].append(value.encode('utf-8'))
                        else:
                            entry['l'] = [value.encode('utf-8')]

        # Add Name and Full Name to the object
        entry['sn'] = [last_name]
        entry['givenName'] = [first_name]
        entry['cn'] = [ u'%s %s'.encode('utf-8') %(first_name, last_name) ]
        if 'mail' in entry.keys() and len(entry['mail']) > 0:
            dn = u'cn=%s %s, mail=%s'.encode('utf-8') %(first_name, last_name,
                            entry['mail'][0])
        else:
            dn = u'cn=%s %s'.encode('utf-8') %(first_name, last_name)

        output = ldif.CreateLDIF(dn, entry)
        return output

    def importLdifToContact(self, filename):
        """ Import a list of ldif from a file """
        file = open(filename, 'rb')
        parser = Series60LDIFParser(open(filename, 'rb'))
        return parser

    def convertToContact(self, entry):
        """ Convert a ldif object to a Contact object """
        con = Contact( name = unicode(entry['cn'][0], 'utf-8') )

        for el in entry.keys():
            if el == 'sn':
                for val in entry[el]:
                    con.addValue(ContactField('last_name', 'none'),
                        unicode(val, 'utf-8'))
            elif el == 'givenName':
                for val in entry[el]:
                    con.addValue(ContactField('first_name', 'none'),
                        unicode(val, 'utf-8'))
            elif el == 'title':
                for val in entry[el]:
                    con.addValue(ContactField('job_title', 'none'),
                        unicode(val, 'utf-8'))
            elif el == 'o':
                for val in entry[el]:
                    con.addValue(ContactField('company_name', 'none'),
                        unicode(val, 'utf-8'))
            elif el == 'telephoneNumber':
                for val in entry[el]:
                    con.addValue(ContactField('phone_number', 'none'),
                        unicode(val))
            elif el == 'homePhone':
                for val in entry[el]:
                    con.addValue(ContactField('phone_number', 'home'),
                        unicode(val))
            elif el == 'mobile':
                for val in entry[el]:
                    con.addValue(ContactField('mobile_number', 'none'),
                        unicode(val))
            elif el == 'mail':
                for val in entry[el]:
                    con.addValue(ContactField('email_address', 'none'),
                        unicode(val))
            elif el == 'mozillaSecondEmail':
                for val in entry[el]:
                    con.addValue(ContactField('email_address', 'none'),
                        unicode(val))
            elif el == 'mozillaSecondEmail':
                for val in entry[el]:
                    con.addValue(ContactField('email_address', 'none'),
                        unicode(val))
            elif el == 'mozillaHomeUrl':
                for val in entry[el]:
                    con.addValue(ContactField('url', 'home'),
                        unicode(val))
            elif el == 'mozillaWorkUrl':
                for val in entry[el]:
                    con.addValue(ContactField('url', 'work'),
                        unicode(val))
            ## Home address
            elif el == 'mozillaHomeStreet':
                for val in entry[el]:
                    con.addValue(ContactField('street_address', 'home'),
                        unicode(val, 'utf-8'))
            elif el == 'mozillaHomeLocalityName':
                for val in entry[el]:
                    con.addValue(ContactField('city', 'home'),
                        unicode(val, 'utf-8'))
            elif el == 'mozillaHomeCountryName':
                for val in entry[el]:
                    con.addValue(ContactField('country', 'home'),
                        unicode(val, 'utf-8'))
            elif el == 'mozillaHomePostalCode':
                for val in entry[el]:
                    con.addValue(ContactField('postal_code', 'home'),
                        unicode(val))
            elif el == 'mozillaHomeState':
                for val in entry[el]:
                    con.addValue(ContactField('state', 'home'),
                        unicode(val, 'utf-8'))
            ## Work Address
            elif el == 'postalCode':
                for val in entry[el]:
                    con.addValue(ContactField('postal_code', 'work'),
                        unicode(val))
            elif el == 'street':
                for val in entry[el]:
                    con.addValue(ContactField('street_address', 'work'),
                        unicode(val, 'utf-8'))
            elif el == 'l':
                for val in entry[el]:
                    con.addValue(ContactField('city', 'work'),
                        unicode(val, 'utf-8'))
            elif el == 'st':
                for val in entry[el]:
                    con.addValue(ContactField('state', 'work'),
                        unicode(val, 'utf-8'))
            elif el == 'c':
                for val in entry[el]:
                    con.addValue(ContactField('country', 'work'),
                        unicode(val, 'utf-8'))
            #else:
                #print el, entry[el]
        # Add birthday
        if 'birthyear' in entry.keys() and 'birthmonth' in entry.keys() \
            and 'birthday' in entry.keys():
            date = entry['birthyear'][0] + entry['birthmonth'][0] + entry['birthday'][0]
            con.addValue(ContactField('date', 'none'),
                        unicode(date))
        return con
