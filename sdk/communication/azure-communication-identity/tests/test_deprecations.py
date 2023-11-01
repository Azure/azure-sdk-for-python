# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import azure.communication.identity as models 

class TestDeprecations:
    
    def test_deprecated_bot_identifier(self):
        with pytest.deprecated_call():
            bot = models.MicrosoftBotIdentifier("test")
    
    def test_deprecated_bot_kind(self):
        with pytest.deprecated_call():
            props = models.CommunicationIdentifierKind.MICROSOFT_BOT
            assert props == models.CommunicationIdentifierKind.MICROSOFT_BOT
            