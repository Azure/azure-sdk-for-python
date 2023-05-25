# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import azure.communication.phonenumbers._shared.models as models

test_user_id = "test_user_id"
test_bot_id = "test_bot_id"
test_unknown_id = "test_unknown_id"
test_phone_number = "+123456789101"

def test_communication_user_identifier():
    id = "some_id"
    comm_user = models.CommunicationUserIdentifier(id)
    assert comm_user.kind == models.CommunicationIdentifierKind.COMMUNICATION_USER
    assert comm_user.raw_id == id
    assert comm_user.properties["id"] == id

def test_phone_number_identifier():
    phone_num = models.PhoneNumberIdentifier(test_phone_number)
    assert phone_num.kind == models.CommunicationIdentifierKind.PHONE_NUMBER
    assert phone_num.raw_id == f"{models.PHONE_NUMBER_PREFIX}{test_phone_number}"
    assert phone_num.properties["value"] == test_phone_number

def test_unknown_identifier():
    identifier = test_unknown_id
    unknown = models.UnknownIdentifier(identifier)
    assert unknown.kind == models.CommunicationIdentifierKind.UNKNOWN
    assert unknown.raw_id == identifier
    assert unknown.properties == {}

def test_microsoft_teams_user_identifier():
    user_id = test_user_id
    teams_user = models.MicrosoftTeamsUserIdentifier(user_id)
    assert teams_user.kind == models.CommunicationIdentifierKind.MICROSOFT_TEAMS_USER
    assert teams_user.raw_id == f"{models.TEAMS_USER_PUBLIC_CLOUD_PREFIX}{user_id}"
    assert teams_user.properties["user_id"] == user_id
    assert teams_user.properties["is_anonymous"] == False
    assert teams_user.properties["cloud"] == models.CommunicationCloudEnvironment.PUBLIC

def test_identifier_from_raw_id_phone_number():
    raw_id = f"{models.PHONE_NUMBER_PREFIX}{test_phone_number}"
    identifier = models.identifier_from_raw_id(raw_id)
    assert isinstance(identifier, models.PhoneNumberIdentifier)

def test_identifier_from_raw_id_teams_user():
    user_id = test_user_id
    raw_id = f"{models.TEAMS_USER_PUBLIC_CLOUD_PREFIX}{user_id}"
    identifier = models.identifier_from_raw_id(raw_id)
    assert isinstance(identifier, models.MicrosoftTeamsUserIdentifier)

def test_identifier_from_raw_id_unknown():
    raw_id = test_unknown_id
    identifier = models.identifier_from_raw_id(raw_id)
    assert isinstance(identifier, models.UnknownIdentifier)

def test_microsoft_teams_user_identifier_anonymous():
    user_id = test_user_id
    teams_user = models.MicrosoftTeamsUserIdentifier(user_id, is_anonymous=True)
    assert teams_user.kind == models.CommunicationIdentifierKind.MICROSOFT_TEAMS_USER
    assert teams_user.raw_id == f'{models.TEAMS_USER_ANONYMOUS_PREFIX}{user_id}'
    assert teams_user.properties["user_id"] == user_id
    assert teams_user.properties["is_anonymous"] == True
    assert teams_user.properties["cloud"] == models.CommunicationCloudEnvironment.PUBLIC

def test_microsoft_teams_user_identifier_cloud_types():
    user_id = test_user_id
    for cloud, prefix in zip(
        [models.CommunicationCloudEnvironment.DOD, models.CommunicationCloudEnvironment.GCCH],
        [models.TEAMS_USER_DOD_CLOUD_PREFIX, models.TEAMS_USER_GCCH_CLOUD_PREFIX]
    ):
        teams_user = models.MicrosoftTeamsUserIdentifier(user_id, cloud=cloud)
        assert teams_user.kind == models.CommunicationIdentifierKind.MICROSOFT_TEAMS_USER
        assert teams_user.raw_id == f'{prefix}{user_id}'
        assert teams_user.properties["user_id"] == user_id
        assert teams_user.properties["is_anonymous"] == False
        assert teams_user.properties["cloud"] == cloud

def test_microsoft_bot_identifier():
    bot_id = test_bot_id
    bot = models.MicrosoftBotIdentifier(bot_id)
    assert bot.kind == models.CommunicationIdentifierKind.MICROSOFT_BOT
    assert bot.raw_id == f'{models.BOT_PUBLIC_CLOUD_PREFIX}{bot_id}'
    assert bot.properties["bot_id"] == bot_id
    assert bot.properties["is_resource_account_configured"] == True
    assert bot.properties["cloud"] == models.CommunicationCloudEnvironment.PUBLIC

def test_microsoft_bot_identifier_cloud_types():
    bot_id = test_bot_id
    for cloud, prefix in zip(
        [models.CommunicationCloudEnvironment.DOD, models.CommunicationCloudEnvironment.GCCH],
        [models.BOT_DOD_CLOUD_PREFIX, models.BOT_GCCH_CLOUD_PREFIX]
    ):
        bot = models.MicrosoftBotIdentifier(bot_id, cloud=cloud)
        assert bot.kind == models.CommunicationIdentifierKind.MICROSOFT_BOT
        assert bot.raw_id == f'{prefix}{bot_id}'
        assert bot.properties["bot_id"] == bot_id
        assert bot.properties["is_resource_account_configured"] == True
        assert bot.properties["cloud"] == cloud

def test_microsoft_bot_identifier_global():
    bot_id = test_bot_id
    bot = models.MicrosoftBotIdentifier(bot_id, is_resource_account_configured=False)
    assert bot.kind == models.CommunicationIdentifierKind.MICROSOFT_BOT
    assert bot.raw_id == f'{models.BOT_PREFIX}{bot_id}'
    assert bot.properties["bot_id"] == bot_id
    assert bot.properties["is_resource_account_configured"] == False
    assert bot.properties["cloud"] == models.CommunicationCloudEnvironment.PUBLIC

def test_microsoft_bot_identifier_global_cloud_types():
    bot_id = test_bot_id
    for cloud, prefix in zip(
        [models.CommunicationCloudEnvironment.DOD, models.CommunicationCloudEnvironment.GCCH],
        [models.BOT_DOD_CLOUD_GLOBAL_PREFIX, models.BOT_GCCH_CLOUD_GLOBAL_PREFIX]
    ):
        bot = models.MicrosoftBotIdentifier(bot_id, is_resource_account_configured=False, cloud=cloud)
        assert bot.kind == models.CommunicationIdentifierKind.MICROSOFT_BOT
        assert bot.raw_id == f'{prefix}{bot_id}'
        assert bot.properties["bot_id"] == bot_id
        assert bot.properties["is_resource_account_configured"] == False
        assert bot.properties["cloud"] == cloud

def test_identifier_from_raw_id_microsoft_bot():
    bot_id = test_bot_id
    raw_id = f"{models.BOT_PREFIX}{bot_id}"
    identifier = models.identifier_from_raw_id(raw_id)
    assert isinstance(identifier, models.MicrosoftBotIdentifier)

def test_identifier_from_raw_id_microsoft_bot_returns_unknown():
    bot_id = test_bot_id
    raw_id = f"not_a_prefix:{bot_id}"
    identifier = models.identifier_from_raw_id(raw_id)
    assert isinstance(identifier, models.UnknownIdentifier)

def test_identifier_from_raw_id_microsoft_bot_cloud_types():
    bot_id = test_bot_id
    for prefix in [models.BOT_GCCH_CLOUD_GLOBAL_PREFIX, models.BOT_PUBLIC_CLOUD_PREFIX, models.BOT_DOD_CLOUD_GLOBAL_PREFIX, models.BOT_GCCH_CLOUD_PREFIX, models.BOT_DOD_CLOUD_PREFIX]:
        raw_id = f"{prefix}:{bot_id}"
        identifier = models.identifier_from_raw_id(raw_id)
        assert isinstance(identifier, models.MicrosoftBotIdentifier)

def test_identifier_from_raw_id_microsoft_teams_user():
    user_id = test_user_id
    for prefix in [models.TEAMS_USER_ANONYMOUS_PREFIX, models.TEAMS_USER_PUBLIC_CLOUD_PREFIX, models.TEAMS_USER_DOD_CLOUD_PREFIX, models.TEAMS_USER_GCCH_CLOUD_PREFIX]:
        raw_id = f"{prefix}:{user_id}"
        identifier = models.identifier_from_raw_id(raw_id)
        assert isinstance(identifier, models.MicrosoftTeamsUserIdentifier)

def test_identifier_from_raw_id_communication_user():
    id = test_user_id
    for prefix in [models.ACS_USER_PREFIX, models.ACS_USER_DOD_CLOUD_PREFIX, models.ACS_USER_GCCH_CLOUD_PREFIX, models.SPOOL_USER_PREFIX]:
        raw_id = f"{prefix}:{id}"
        identifier = models.identifier_from_raw_id(raw_id)
        assert isinstance(identifier, models.CommunicationUserIdentifier)