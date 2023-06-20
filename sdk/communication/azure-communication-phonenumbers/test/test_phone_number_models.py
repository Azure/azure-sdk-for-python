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
    comm_user = models.CommunicationUserIdentifier(test_user_id)
    assert comm_user.kind == models.CommunicationIdentifierKind.COMMUNICATION_USER
    assert comm_user.raw_id == test_user_id
    assert comm_user.properties["id"] == test_user_id

def test_phone_number_identifier():
    phone_num = models.PhoneNumberIdentifier(test_phone_number)
    assert phone_num.kind == models.CommunicationIdentifierKind.PHONE_NUMBER
    assert phone_num.raw_id == f"{models.PHONE_NUMBER_PREFIX}{test_phone_number}"
    assert phone_num.properties["value"] == test_phone_number

def test_unknown_identifier():
    unknown = models.UnknownIdentifier(test_unknown_id)
    assert unknown.kind == models.CommunicationIdentifierKind.UNKNOWN
    assert unknown.raw_id == test_unknown_id
    assert unknown.properties == {}

def test_microsoft_teams_user_identifier():
    teams_user = models.MicrosoftTeamsUserIdentifier(test_user_id)
    assert teams_user.kind == models.CommunicationIdentifierKind.MICROSOFT_TEAMS_USER
    assert teams_user.raw_id == f"{models.TEAMS_USER_PUBLIC_CLOUD_PREFIX}{test_user_id}"
    assert teams_user.properties["user_id"] == test_user_id
    assert teams_user.properties["is_anonymous"] == False
    assert teams_user.properties["cloud"] == models.CommunicationCloudEnvironment.PUBLIC

def test_identifier_from_raw_id_phone_number():
    raw_id = f"{models.PHONE_NUMBER_PREFIX}{test_phone_number}"
    identifier = models.identifier_from_raw_id(raw_id)
    assert isinstance(identifier, models.PhoneNumberIdentifier)

def test_identifier_from_raw_id_teams_user():
    raw_id = f"{models.TEAMS_USER_PUBLIC_CLOUD_PREFIX}{test_user_id}"
    identifier = models.identifier_from_raw_id(raw_id)
    assert isinstance(identifier, models.MicrosoftTeamsUserIdentifier)

def test_identifier_from_raw_id_unknown():
    identifier = models.identifier_from_raw_id(test_unknown_id)
    assert isinstance(identifier, models.UnknownIdentifier)

def test_microsoft_teams_user_identifier_anonymous():
    teams_user = models.MicrosoftTeamsUserIdentifier(test_user_id, is_anonymous=True)
    assert teams_user.kind == models.CommunicationIdentifierKind.MICROSOFT_TEAMS_USER
    assert teams_user.raw_id == f'{models.TEAMS_USER_ANONYMOUS_PREFIX}{test_user_id}'
    assert teams_user.properties["user_id"] == test_user_id
    assert teams_user.properties["is_anonymous"] == True
    assert teams_user.properties["cloud"] == models.CommunicationCloudEnvironment.PUBLIC

def test_microsoft_teams_user_identifier_cloud_types():
    for cloud, prefix in zip(
        [models.CommunicationCloudEnvironment.DOD, models.CommunicationCloudEnvironment.GCCH],
        [models.TEAMS_USER_DOD_CLOUD_PREFIX, models.TEAMS_USER_GCCH_CLOUD_PREFIX]
    ):
        teams_user = models.MicrosoftTeamsUserIdentifier(test_user_id, cloud=cloud)
        assert teams_user.kind == models.CommunicationIdentifierKind.MICROSOFT_TEAMS_USER
        assert teams_user.raw_id == f'{prefix}{test_user_id}'
        assert teams_user.properties["user_id"] == test_user_id
        assert teams_user.properties["is_anonymous"] == False
        assert teams_user.properties["cloud"] == cloud

def test_microsoft_bot_identifier():
    bot = models.MicrosoftBotIdentifier(test_bot_id)
    assert bot.kind == models.CommunicationIdentifierKind.MICROSOFT_BOT
    assert bot.raw_id == f'{models.BOT_PUBLIC_CLOUD_PREFIX}{test_bot_id}'
    assert bot.properties["bot_id"] == test_bot_id
    assert bot.properties["is_resource_account_configured"] == True
    assert bot.properties["cloud"] == models.CommunicationCloudEnvironment.PUBLIC

def test_microsoft_bot_identifier_cloud_types():
    for cloud, prefix in zip(
        [models.CommunicationCloudEnvironment.DOD, models.CommunicationCloudEnvironment.GCCH],
        [models.BOT_DOD_CLOUD_PREFIX, models.BOT_GCCH_CLOUD_PREFIX]
    ):
        bot = models.MicrosoftBotIdentifier(test_bot_id, cloud=cloud)
        assert bot.kind == models.CommunicationIdentifierKind.MICROSOFT_BOT
        assert bot.raw_id == f'{prefix}{test_bot_id}'
        assert bot.properties["bot_id"] == test_bot_id
        assert bot.properties["is_resource_account_configured"] == True
        assert bot.properties["cloud"] == cloud

def test_microsoft_bot_identifier_global():
    bot = models.MicrosoftBotIdentifier(test_bot_id, is_resource_account_configured=False)
    assert bot.kind == models.CommunicationIdentifierKind.MICROSOFT_BOT
    assert bot.raw_id == f'{models.BOT_PREFIX}{test_bot_id}'
    assert bot.properties["bot_id"] == test_bot_id
    assert bot.properties["is_resource_account_configured"] == False
    assert bot.properties["cloud"] == models.CommunicationCloudEnvironment.PUBLIC

def test_microsoft_bot_identifier_global_cloud_types():
    for cloud, prefix in zip(
        [models.CommunicationCloudEnvironment.DOD, models.CommunicationCloudEnvironment.GCCH],
        [models.BOT_DOD_CLOUD_GLOBAL_PREFIX, models.BOT_GCCH_CLOUD_GLOBAL_PREFIX]
    ):
        bot = models.MicrosoftBotIdentifier(test_bot_id, is_resource_account_configured=False, cloud=cloud)
        assert bot.kind == models.CommunicationIdentifierKind.MICROSOFT_BOT
        assert bot.raw_id == f'{prefix}{test_bot_id}'
        assert bot.properties["bot_id"] == test_bot_id
        assert bot.properties["is_resource_account_configured"] == False
        assert bot.properties["cloud"] == cloud

def test_identifier_from_raw_id_microsoft_bot():
    raw_id = f"{models.BOT_PREFIX}{test_bot_id}"
    identifier = models.identifier_from_raw_id(raw_id)
    assert isinstance(identifier, models.MicrosoftBotIdentifier)

def test_identifier_from_raw_id_microsoft_bot_returns_unknown():
    raw_id = f"not_a_prefix:{test_bot_id}"
    identifier = models.identifier_from_raw_id(raw_id)
    assert isinstance(identifier, models.UnknownIdentifier)

def test_identifier_from_raw_id_microsoft_bot_cloud_types():
    for prefix in [models.BOT_GCCH_CLOUD_GLOBAL_PREFIX, models.BOT_PUBLIC_CLOUD_PREFIX, models.BOT_DOD_CLOUD_GLOBAL_PREFIX, models.BOT_GCCH_CLOUD_PREFIX, models.BOT_DOD_CLOUD_PREFIX]:
        raw_id = f"{prefix}:{test_bot_id}"
        identifier = models.identifier_from_raw_id(raw_id)
        assert isinstance(identifier, models.MicrosoftBotIdentifier)

def test_identifier_from_raw_id_microsoft_teams_user():
    for prefix in [models.TEAMS_USER_ANONYMOUS_PREFIX, models.TEAMS_USER_PUBLIC_CLOUD_PREFIX, models.TEAMS_USER_DOD_CLOUD_PREFIX, models.TEAMS_USER_GCCH_CLOUD_PREFIX]:
        raw_id = f"{prefix}:{test_user_id}"
        identifier = models.identifier_from_raw_id(raw_id)
        assert isinstance(identifier, models.MicrosoftTeamsUserIdentifier)

def test_identifier_from_raw_id_communication_user():
    for prefix in [models.ACS_USER_PREFIX, models.ACS_USER_DOD_CLOUD_PREFIX, models.ACS_USER_GCCH_CLOUD_PREFIX, models.SPOOL_USER_PREFIX]:
        raw_id = f"{prefix}:{test_user_id}"
        identifier = models.identifier_from_raw_id(raw_id)
        assert isinstance(identifier, models.CommunicationUserIdentifier)

def test_communication_user_identifier_equality():
    user1 = models.CommunicationUserIdentifier(test_user_id)
    user2 = models.CommunicationUserIdentifier(test_user_id)
    user3 = models.CommunicationUserIdentifier(test_unknown_id)
    assert user1 == user2
    assert user1 != user3

def test_phone_number_identifier_equality():
    phone1 = models.PhoneNumberIdentifier(test_phone_number)
    phone2 = models.PhoneNumberIdentifier(test_phone_number)
    phone3 = models.PhoneNumberIdentifier("+0987654321")
    assert phone1 == phone2
    assert phone1 != phone3

def test_microsoft_bot_identifier_equality():
    bot1 = models.MicrosoftBotIdentifier(test_bot_id)
    bot2 = models.MicrosoftBotIdentifier(test_bot_id)
    bot3 = models.MicrosoftBotIdentifier(test_unknown_id)
    assert bot1 == bot2
    assert bot1 != bot3

def test_microsoft_teams_user_identifier_equality():
    user1 = models.MicrosoftTeamsUserIdentifier(test_user_id)
    user2 = models.MicrosoftTeamsUserIdentifier(test_user_id)
    user3 = models.MicrosoftTeamsUserIdentifier(test_unknown_id)
    assert user1 == user2
    assert user1 != user3