# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import datetime
from enum import Enum
from typing import Any, Union, NamedTuple, Optional
from typing_extensions import TypedDict, Required

from azure.core import CaseInsensitiveEnumMeta


class EntityMetadata(TypedDict, total=False):
    etag: Required[Optional[str]]
    """A string representation of the timestamp property. Used to provide optimistic concurrency."""

    timestamp: Required[Optional[datetime.datetime]]
    """A datetime value that is maintained on the server side to record the time an entity was last modified. The Table
    service uses the Timestamp property internally to provide optimistic concurrency."""

    id: str
    """The entity ID, which is generally the URL to the resource. This is not returned by default, and only returned if
    full metadata is requested."""

    type: str
    """The type name of the containing object. This is not returned by default, and only returned if full metadata is
    requested."""

    editLink: str
    """The link used to edit/update the entry, if the entity is updatable and the odata.id does not represent a URL
    that can be used to edit the entity. This is not returned by default, and only returned if full metadata is
    requested."""


class TableEntity(dict):
    """
    An Entity dictionary with additional metadata

    """

    _metadata: EntityMetadata = {"etag": None, "timestamp": None}

    @property
    def metadata(self) -> EntityMetadata:
        """Includes the metadata with etag and timestamp.

        :return: Dict of entity metadata
        :rtype: ~azure.data.tables.EntityMetadata
        """
        return self._metadata


class EdmType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """
    Used by :class:`~.EntityProperty` to represent the type of the entity property
    to be stored by the Table service.
    """

    BINARY = "Edm.Binary"
    """ Represents byte data. This type will be inferred for Python bytes. """

    INT64 = "Edm.Int64"
    """ Represents a number between -(2^31) and 2^31. Must be specified or numbers will default to INT32. """

    GUID = "Edm.Guid"
    """ Represents a GUID. This type will be inferred for uuid.UUID. """

    DATETIME = "Edm.DateTime"
    """ Represents a date. This type will be inferred for Python datetime objects. """

    STRING = "Edm.String"
    """ Represents a string. This type will be inferred for Python strings. """

    INT32 = "Edm.Int32"
    """ Represents a number between -(2^15) and 2^15. This is the default type for Python numbers. """

    DOUBLE = "Edm.Double"
    """ Represents a double. This type will be inferred for Python floating point numbers. """

    BOOLEAN = "Edm.Boolean"
    """ Represents a boolean. This type will be inferred for Python booleans. """


EntityProperty = NamedTuple("EntityProperty", [("value", Any), ("edm_type", Union[str, EdmType])])
"""
An entity property. Used to explicitly set :class:`~EdmType` when necessary.

Values which require explicit typing are GUID, INT64, and BINARY. Other EdmTypes
may be explicitly create as EntityProperty objects but need not be. For example,
the below with both create STRING typed properties on the entity::
    entity = TableEntity()
    entity.a = 'b'
    entity.x = EntityProperty('y', EdmType.STRING)

:param value:
:type value: Any
:param edm_type: Type of the value
:type edm_type: str or ~azure.data.tables.EdmType
"""
