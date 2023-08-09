# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

PROXY_URL = os.getenv("PROXY_URL", "https://localhost:5001").rstrip("/")
TEST_SETTING_FILENAME = "testsettings_local.cfg"
