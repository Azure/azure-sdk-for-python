# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
from datetime import datetime

def _get_repeatability_guid():
    return uuid.uuid4()

def _get_repeatability_timestamp():
    return datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
