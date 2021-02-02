# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
from azure.communication.chat._shared.communication_identifier_serializer import CommunicationUserIdentifierSerializer
from azure.communication.chat._shared.models import(
    CommunicationIdentifierKind,
    CommunicationIdentifierModel,
    CommunicationUserIdentifier,
    CommunicationCloudEnvironment,
    UnknownIdentifier,
    PhoneNumberIdentifier,
    MicrosoftTeamsUserIdentifier
)

class CommunicationUserIdentifierSerializerTest(unittest.TestCase):

    def test_missing_property_deserializer_throws(self):
        models_with_missing_property = [
            CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.Unknown
            ), # missing id
            CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.CommunicationUser
            ), # missing id
            CommunicationIdentifierModel(
                id="someid",
                kind=CommunicationIdentifierKind.PhoneNumber
            ), # missing phone number
            CommunicationIdentifierModel(
                id="someid",
                microsoft_teams_user_id="teamsid",
                kind=CommunicationIdentifierKind.MicrosoftTeamsUser,
                cloud=CommunicationCloudEnvironment.Public
            ), # missing is_anonymous
            CommunicationIdentifierModel(
                id="some id",
                is_anonymous=True,
                kind=CommunicationIdentifierKind.MicrosoftTeamsUser,
                cloud=CommunicationCloudEnvironment.Public
            ), # missing microsoft_teams_user_id
            CommunicationIdentifierModel(
                microsoft_teams_user_id="teamsid",
                is_anonymous=True,
                kind=CommunicationIdentifierKind.MicrosoftTeamsUser,
                cloud=CommunicationCloudEnvironment.Public
            ), # missing id
            CommunicationIdentifierModel(
                id="someid",
                is_anonymous=True,
                microsoft_teams_user_id="teamsid",
                kind=CommunicationIdentifierKind.MicrosoftTeamsUser
            ) # missing cloud,
        ]

        for model in models_with_missing_property:
            self.assertRaises(ValueError, lambda : CommunicationUserIdentifierSerializer.deserialize(model))

    def test_serialize_communication_user(self):
        communication_identifier_model = CommunicationUserIdentifierSerializer.serialize(
            CommunicationUserIdentifier("an id")
        )

        assert communication_identifier_model.kind is CommunicationIdentifierKind.CommunicationUser
        assert communication_identifier_model.id is "an id"

    def test_deserialize_communication_user(self):
        communication_identifier_actual = CommunicationUserIdentifierSerializer.deserialize(
            CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.CommunicationUser,
                id="an id"
            )
        )

        communication_identifier_expected = CommunicationUserIdentifier("an id")

        assert isinstance(communication_identifier_actual, CommunicationUserIdentifier)
        assert communication_identifier_actual == communication_identifier_actual

    def test_serialize_unknown_identifier(self):
        unknown_identifier_model = CommunicationUserIdentifierSerializer.serialize(
            UnknownIdentifier("an id")
        )

        assert unknown_identifier_model.kind is CommunicationIdentifierKind.Unknown
        assert unknown_identifier_model.id is "an id"

    def test_deserialize_unknown_identifier(self):
        unknown_identifier_actual = CommunicationUserIdentifierSerializer.deserialize(
            CommunicationIdentifierModel(
                kind=CommunicationIdentifierKind.Unknown,
                id="an id"
            )
        )

        unknown_identifier_expected = UnknownIdentifier("an id")

        assert isinstance(unknown_identifier_actual, UnknownIdentifier)
        assert unknown_identifier_actual.identifier == unknown_identifier_expected.identifier

    def test_serialize_phone_number(self):
        phone_number_identifier_model = CommunicationUserIdentifierSerializer.serialize(
            PhoneNumberIdentifier("phonenumber")
        )

        assert phone_number_identifier_model.kind is CommunicationIdentifierKind.PhoneNumber
        assert phone_number_identifier_model.phone_number is "phonenumber"

    def test_deserialize_phone_number(self):
        phone_number_identifier_actual = CommunicationUserIdentifierSerializer.deserialize(
            CommunicationIdentifierModel(
                id="someid",
                kind=CommunicationIdentifierKind.PhoneNumber,
                phone_number="phonenumber"
            )
        )

        phone_number_identifier_expected = PhoneNumberIdentifier("phonenumber", identifier="someid")

        assert isinstance(phone_number_identifier_actual, PhoneNumberIdentifier)
        assert phone_number_identifier_actual.phone_number == phone_number_identifier_expected.phone_number
        assert phone_number_identifier_actual.identifier == phone_number_identifier_expected.identifier

    def test_serialize_teams_user(self):
        teams_user_identifier_model = CommunicationUserIdentifierSerializer.serialize(
            MicrosoftTeamsUserIdentifier(
                "teamsid",
                cloud=CommunicationCloudEnvironment.Public,
                identifier="someid"
            )
        )

        assert teams_user_identifier_model.kind is CommunicationIdentifierKind.MicrosoftTeamsUser
        assert teams_user_identifier_model.microsoft_teams_user_id is "teamsid"
        assert teams_user_identifier_model.communication_cloud_environment is CommunicationCloudEnvironment.Public
        assert teams_user_identifier_model.id is "someid"

    def test_deserialize_teams_user(self):
        teams_user_identifier_actual = CommunicationUserIdentifierSerializer.deserialize(
            CommunicationIdentifierModel(
                id="someid",
                kind=CommunicationIdentifierKind.MicrosoftTeamsUser,
                microsoft_teams_user_id="teamsid",
                is_anonymous=True,
                communication_cloud_environment="PUBLIC"
            )
        )

        teams_user_identifier_expected = MicrosoftTeamsUserIdentifier(
            "teamsid",
            identifier="someid",
            cloud=CommunicationCloudEnvironment.Public,
            is_anonymous=True
        )

        assert isinstance(teams_user_identifier_actual, MicrosoftTeamsUserIdentifier)
        assert teams_user_identifier_actual.identifier == teams_user_identifier_expected.identifier
        assert teams_user_identifier_actual.user_id == teams_user_identifier_expected.user_id
        assert teams_user_identifier_actual.is_anonymous== teams_user_identifier_expected.is_anonymous
        assert teams_user_identifier_actual.cloud == teams_user_identifier_expected.cloud

    def test_serialize_foreign_throws(self):
        foreign_obj = "Foreign object"
        self.assertRaises(
            TypeError,
            lambda : CommunicationUserIdentifierSerializer.serialize(foreign_obj)
        )

    def test_deserialize_unknown_kind(self):
        unknown_identifier = CommunicationUserIdentifierSerializer.deserialize(
            CommunicationIdentifierModel(
                kind="foreign",
                id="an id"
            )
        )

        assert isinstance(unknown_identifier, UnknownIdentifier)
        assert unknown_identifier.identifier == "an id"
        

if __name__ == "__main__":
    unittest.main()