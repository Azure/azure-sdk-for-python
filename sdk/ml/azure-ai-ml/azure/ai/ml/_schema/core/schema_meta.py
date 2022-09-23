# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from collections import OrderedDict

from marshmallow import RAISE
from marshmallow.decorators import post_dump
from marshmallow.schema import Schema, SchemaMeta

module_logger = logging.getLogger(__name__)


class PatchedMeta:
    ordered = True
    unknown = RAISE


class PatchedBaseSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    @post_dump
    def remove_none(self, data, **kwargs):
        """Prevents from dumping attributes that are None, thus making the dump
        more compact."""
        return OrderedDict((key, value) for key, value in data.items() if value is not None)


class PatchedSchemaMeta(SchemaMeta):
    """Currently there is an open issue in marshmallow, that the "unknown"
    property is not inherited.

    We use a metaclass to inject a Meta class into all our Schema
    classes.
    """

    def __new__(cls, name, bases, dct):
        meta = dct.get("Meta")
        if meta is None:
            dct["Meta"] = PatchedMeta
        else:
            dct["Meta"].unknown = RAISE
            dct["Meta"].ordered = True

        bases = bases + (PatchedBaseSchema,)
        klass = super().__new__(cls, name, bases, dct)
        return klass
