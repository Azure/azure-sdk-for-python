# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import azure.communication.callautomation as models 

class TestDeprecations:
    
    def test_deprecated_bot_identifier(self):
        with pytest.deprecated_call():
            bot = models.MicrosoftBotIdentifier("test")
    
    def test_deprecated_bot_properties(self):
        with pytest.deprecated_call():
            props = models.MicrosoftBotProperties()