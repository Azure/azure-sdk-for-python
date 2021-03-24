# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
from azure.communication.chat._communication_identifier_serializer import CommunicationUserIdentifierSerializer
from azure.communication.chat._generated.models import(
    CommunicationIdentifierModel,
    MicrosoftTeamsUserIdentifierModel,
    CommunicationUserIdentifierModel,
    PhoneNumberIdentifierModel
)
from azure.communication.chat._shared.models import(
    CommunicationUserIdentifier,
    CommunicationCloudEnvironment,
    UnknownIdentifier,
    PhoneNumberIdentifier,
    MicrosoftTeamsUserIdentifier
)

class CommunicationUserIdentifierSerializerTest(unittest.TestCase):
    def setUp(self):
        self.testPhoneNumber="+12223334444"
        self.testUserModel = CommunicationUserIdentifierModel(id="User Id")
        self.testPhoneNumberModel = PhoneNumberIdentifierModel(value=self.testPhoneNumber)
        self.testTeamsUserModel = MicrosoftTeamsUserIdentifierModel(user_id="Microsoft Teams User Id",
                                                                   is_anonymous=True,
                                                                   cloud=CommunicationCloudEnvironment.Public)


    def test_missing_property_deserializer_throws(self):
        models_with_missing_property = [
            CommunicationIdentifierModel(
            ), # missing id
            CommunicationIdentifierModel(
                communication_user=CommunicationUserIdentifierModel(id="id")
            ), # missing id
            CommunicationIdentifierModel(
                raw_id="someid",
                microsoft_teams_user=MicrosoftTeamsUserIdentifierModel(user_id="teamsid",
                cloud=CommunicationCloudEnvironment.Public)
            ), # missing is_anonymous
            CommunicationIdentifierModel(
                microsoft_teams_user=MicrosoftTeamsUserIdentifierModel(user_id="teamsid",
                is_anonymous=True,
                cloud=CommunicationCloudEnvironment.Public)
            ), # missing id
            CommunicationIdentifierModel(
                raw_id="someid",
                microsoft_teams_user=MicrosoftTeamsUserIdentifierModel(user_id="teamsid",
                is_anonymous=True)
            ) # missing cloud,
        ]

        for model in models_with_missing_property:
            self.assertRaises(ValueError, lambda : CommunicationUserIdentifierSerializer.deserialize(model))


    def test_serialize_communication_user(self):
        communication_identifier_model = CommunicationUserIdentifierSerializer.serialize(
            CommunicationUserIdentifier(identifier="an id")
        )

        assert communication_identifier_model.communication_user.id is "an id"

    def test_deserialize_communication_user(self):
        communication_identifier_actual = CommunicationUserIdentifierSerializer.deserialize(
            CommunicationIdentifierModel(
                raw_id="an id",
                communication_user=self.testUserModel
            )
        )

        communication_identifier_expected = CommunicationUserIdentifier(identifier="an id")

        assert isinstance(communication_identifier_actual, CommunicationUserIdentifier)
        assert communication_identifier_actual.identifier == communication_identifier_expected.identifier

    def test_serialize_unknown_identifier(self):
        unknown_identifier_model = CommunicationUserIdentifierSerializer.serialize(
            UnknownIdentifier(identifier="an id")
        )

        assert unknown_identifier_model.raw_id is "an id"

    def test_deserialize_unknown_identifier(self):
        unknown_identifier_actual = CommunicationUserIdentifierSerializer.deserialize(
            CommunicationIdentifierModel(
                raw_id="an id"
            )
        )

        unknown_identifier_expected = UnknownIdentifier("an id")

        assert isinstance(unknown_identifier_actual, UnknownIdentifier)
        assert unknown_identifier_actual.raw_id == unknown_identifier_expected.raw_id

    def test_serialize_phone_number(self):
        phone_number_identifier_model = CommunicationUserIdentifierSerializer.serialize(
            PhoneNumberIdentifier("phonenumber")
        )

        assert phone_number_identifier_model.phone_number.value is "phonenumber"

    def test_deserialize_phone_number(self):
        phone_number_identifier_actual = CommunicationUserIdentifierSerializer.deserialize(
            CommunicationIdentifierModel(
                raw_id="someid",
                phone_number=self.testPhoneNumberModel
            )
        )

        phone_number_identifier_expected = PhoneNumberIdentifier(self.testPhoneNumber, raw_id="someid")

        assert isinstance(phone_number_identifier_actual, PhoneNumberIdentifier)
        assert phone_number_identifier_actual.phone_number == phone_number_identifier_expected.phone_number
        assert phone_number_identifier_actual.raw_id == phone_number_identifier_expected.raw_id

    def test_serialize_teams_user(self):
        teams_user_identifier_model = CommunicationUserIdentifierSerializer.serialize(
            MicrosoftTeamsUserIdentifier(
                user_id="teamsid",
                cloud=CommunicationCloudEnvironment.Public,
                raw_id="someid"
            )
        )

        assert teams_user_identifier_model.microsoft_teams_user.user_id is "teamsid"
        assert teams_user_identifier_model.microsoft_teams_user.cloud is CommunicationCloudEnvironment.Public
        assert teams_user_identifier_model.raw_id is "someid"

    def test_deserialize_teams_user(self):
        teams_user_identifier_actual = CommunicationUserIdentifierSerializer.deserialize(
            CommunicationIdentifierModel(
                raw_id="someid",
                microsoft_teams_user=self.testTeamsUserModel
            )
        )

        teams_user_identifier_expected = MicrosoftTeamsUserIdentifier(
            raw_id="someid",
            user_id="Microsoft Teams User Id",
            cloud=CommunicationCloudEnvironment.Public,
            is_anonymous=True
        )

        assert isinstance(teams_user_identifier_actual, MicrosoftTeamsUserIdentifier)
        assert teams_user_identifier_actual.raw_id == teams_user_identifier_expected.raw_id
        assert teams_user_identifier_actual.user_id == teams_user_identifier_expected.user_id
        assert teams_user_identifier_actual.is_anonymous== teams_user_identifier_expected.is_anonymous
        assert teams_user_identifier_actual.cloud == teams_user_identifier_expected.cloud

    def test_serialize_foreign_throws(self):
        foreign_obj = "Foreign object"
        self.assertRaises(
            TypeError,
            lambda : CommunicationUserIdentifierSerializer.serialize(foreign_obj)
        )

if __name__ == "__main__":
    unittest.main()