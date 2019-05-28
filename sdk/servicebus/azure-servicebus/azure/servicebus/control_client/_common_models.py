# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# pylint: disable=too-few-public-methods


class WindowsAzureData(object):

    ''' This is the base of data class.
    It is only used to check whether it is instance or not. '''

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value


class Feed(object):
    pass


class _Base64String(str):
    pass


class HeaderDict(dict):

    def __getitem__(self, index):
        return super(HeaderDict, self).__getitem__(index.lower())


class _dict_of(dict):

    """a dict which carries with it the xml element names for key,val.
    Used for deserializaion and construction of the lists"""

    def __init__(self, pair_xml_element_name, key_xml_element_name,
                 value_xml_element_name):
        self.pair_xml_element_name = pair_xml_element_name
        self.key_xml_element_name = key_xml_element_name
        self.value_xml_element_name = value_xml_element_name
        super(_dict_of, self).__init__()


class _list_of(list):

    """a list which carries with it the type that's expected to go in it.
    Used for deserializaion and construction of the lists"""

    def __init__(self, list_type, xml_element_name=None):
        self.list_type = list_type
        if xml_element_name is None:
            self.xml_element_name = list_type.__name__
        else:
            self.xml_element_name = xml_element_name
        super(_list_of, self).__init__()


class _scalar_list_of(list):
    """a list of scalar types which carries with it the type that's
    expected to go in it along with its xml element name.
    Used for deserializaion and construction of the lists"""

    def __init__(self, list_type, xml_element_name):
        self.list_type = list_type
        self.xml_element_name = xml_element_name
        super(_scalar_list_of, self).__init__()


class _xml_attribute:
    """a accessor to XML attributes
    expected to go in it along with its xml element name.
    Used for deserialization and construction"""

    def __init__(self, xml_element_name):
        self.xml_element_name = xml_element_name


try:
    _unicode_type = unicode
    _strtype = basestring
except NameError:
    _unicode_type = str
    _strtype = str
