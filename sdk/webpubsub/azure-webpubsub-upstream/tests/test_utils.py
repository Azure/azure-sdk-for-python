# coding=utf-8
# --------------------------------------------------------------------------
# Created on Mon Oct 18 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

import json
import base64


def build_connection_state(dct={}):
    return base64.b64encode(json.dumps(dct).encode('utf-8')).decode('ascii')


def parse_connection_state(s):
    return json.loads(base64.b64decode(s).decode('utf-8'))
