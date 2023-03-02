# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from marshmallow import fields

module_logger = logging.getLogger(__name__)


class RouteSchema:
    port = fields.Str()
    path = fields.Str()
