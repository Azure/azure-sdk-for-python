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
            assert props == models.CommunicationIdentifierKind.MICROSOFT_TEAMS_APP

    def test_deprecated_bot_identifier(self):
        from azure.communication.identity._shared.models import _MicrosoftBotIdentifier

        with pytest.deprecated_call():
            bot = _MicrosoftBotIdentifier("bot_id", is_resource_account_configured=False, cloud="PUBLIC")
            assert bot.kind == models.CommunicationIdentifierKind.microsoft_bot
            assert bot.properties["bot_id"] == "bot_id" == bot.properties["app_id"]
            assert bot.properties["is_resource_account_configured"] is True
            assert bot.properties["cloud"] == "PUBLIC"
            with pytest.raises(KeyError):
                bot.properties["not_a_thing"]
            assert isinstance(bot, models.MicrosoftTeamsAppIdentifier)
            assert isinstance(bot, models.CommunicationIdentifier)
