# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import base64
from datetime import datetime, timedelta


def generate_token_with_custom_expiry(valid_for_seconds):
    return generate_token_with_custom_expiry_epoch((datetime.now() + timedelta(seconds=valid_for_seconds)).timestamp())


def generate_token_with_custom_expiry_epoch(expires_on_epoch):
    expiry_json = f'{{"exp": {str(expires_on_epoch)} }}'
    base64expiry = base64.b64encode(expiry_json.encode("utf-8")).decode("utf-8").rstrip("=")
    token_template = f"""eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
        {base64expiry}.adM-ddBZZlQ1WlN3pdPBOF5G4Wh9iZpxNP_fSvpF4cWs"""
    return token_template
