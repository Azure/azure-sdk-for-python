# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._shared._error import _ERROR_ATTRIBUTE_MISSING


class Entity(dict):
    """
    An entity object. Can be accessed as a dict or as an obj. The attributes of
    the entity will be created dynamically. For example, the following are both
    valid::
        entity = Entity()
        entity.a = 'b'
        entity['x'] = 'y'
    """

    def __getattr__(self, name):
        try:
            if name is not None:
                return self[name]
            return name
        except KeyError:
            raise AttributeError(_ERROR_ATTRIBUTE_MISSING.format('Entity', name))

    __setattr__ = dict.__setitem__

    def __delattr__(self, name):
        try:
            if name is not None:
                del self[name]
        except KeyError:
            raise AttributeError(_ERROR_ATTRIBUTE_MISSING.format('Entity', name))

    def __dir__(self):
        return dir({}) + list(self.keys())


class EntityProperty(object):
    """
    An entity property. Used to explicitly set :class:`~EdmType` when necessary.

    Values which require explicit typing are GUID, INT32, and BINARY. Other EdmTypes
    may be explicitly create as EntityProperty objects but need not be. For example,
    the below with both create STRING typed properties on the entity::
        entity = Entity()
        entity.a = 'b'
        entity.x = EntityProperty(EdmType.STRING, 'y')
    """

    def __init__(self, type=None, value=None, encrypt=False):  # pylint:disable=W0622
        """
        Represents an Azure Table. Returned by list_tables.

        :param str type: The type of the property.
        :param any value: The value of the property.
        :param bool encrypt: Indicates whether or not the property should be encrypted.
        """
        self.type = type
        self.value = value
        self.encrypt = encrypt


class Table(object):
    """
    Represents an Azure Table. Returned by list_tables.

    :ivar str name: The name of the table.
    """


class EdmType(object):
    """
    Used by :class:`~.EntityProperty` to represent the type of the entity property
    to be stored by the Table service.
    """

    BINARY = 'Edm.Binary'
    ''' Represents byte data. Must be specified. '''

    INT64 = 'Edm.Int64'
    ''' Represents a number between -(2^31) and 2^31. This is the default type for Python numbers. '''

    GUID = 'Edm.Guid'
    ''' Represents a GUID. Must be specified. '''

    DATETIME = 'Edm.DateTime'
    ''' Represents a date. This type will be inferred for Python datetime objects. '''

    STRING = 'Edm.String'
    ''' Represents a string. This type will be inferred for Python strings. '''

    INT32 = 'Edm.Int32'
    ''' Represents a number between -(2^15) and 2^15. Must be specified or numbers will default to INT64. '''

    DOUBLE = 'Edm.Double'
    ''' Represents a double. This type will be inferred for Python floating point numbers. '''

    BOOLEAN = 'Edm.Boolean'
    ''' Represents a boolean. This type will be inferred for Python bools. '''
