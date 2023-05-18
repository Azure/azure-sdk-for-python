# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.communication.phonenumbers._shared.models import (
    CommunicationIdentifierKind,
    CommunicationCloudEnvironment,
    CommunicationUserIdentifier,
    PhoneNumberIdentifier,
    UnknownIdentifier,
    MicrosoftTeamsUserIdentifier,
    identifier_from_raw_id
)


def test_communication_user_identifier():
    id = "some_id"
    comm_user = CommunicationUserIdentifier(id)
    assert comm_user.kind == CommunicationIdentifierKind.COMMUNICATION_USER
    assert comm_user.raw_id == id
    assert comm_user.properties["id"] == id


def test_phone_number_identifier():
    value = "+18001234567"
    phone_num = PhoneNumberIdentifier(value)
    assert phone_num.kind == CommunicationIdentifierKind.PHONE_NUMBER
    assert phone_num.raw_id == f"4:{value}"
    assert phone_num.properties["value"] == value


def test_unknown_identifier():
    identifier = "some_unknown_id"
    unknown = UnknownIdentifier(identifier)
    assert unknown.kind == CommunicationIdentifierKind.UNKNOWN
    assert unknown.raw_id == identifier
    assert unknown.properties == {}


def test_microsoft_teams_user_identifier():
    user_id = "some_user_id"
    teams_user = MicrosoftTeamsUserIdentifier(user_id)
    assert teams_user.kind == CommunicationIdentifierKind.MICROSOFT_TEAMS_USER
    assert teams_user.raw_id == f"8:orgid:{user_id}"
    assert teams_user.properties["user_id"] == user_id
    assert teams_user.properties["is_anonymous"] == False
    assert teams_user.properties["cloud"] == CommunicationCloudEnvironment.PUBLIC


def test_identifier_from_raw_id_phone_number():
    value = "+123456789101"
    raw_id = f"4:{value}"
    identifier = identifier_from_raw_id(raw_id)
    assert isinstance(identifier, PhoneNumberIdentifier)


def test_identifier_from_raw_id_teams_user():
    user_id = "some_user_id"
    raw_id = f"8:orgid:{user_id}"
    identifier = identifier_from_raw_id(raw_id)
    assert isinstance(identifier, MicrosoftTeamsUserIdentifier)


def test_identifier_from_raw_id_unknown():
    raw_id = "some_unknown_id"
    identifier = identifier_from_raw_id(raw_id)
    assert isinstance(identifier, UnknownIdentifier)
