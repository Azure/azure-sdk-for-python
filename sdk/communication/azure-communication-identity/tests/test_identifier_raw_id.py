# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import unittest
from azure.communication.identity import *

class IdentifierRawIdTest(unittest.TestCase):
    def test_raw_id(self):
        _assert_raw_id(
            CommunicationUserIdentifier(
                id='8:acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
            ),
            '8:acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        _assert_raw_id(
            CommunicationUserIdentifier(
                id='8:gcch-acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
            ),
            '8:gcch-acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        _assert_raw_id(
            CommunicationUserIdentifier(
                id='someFutureFormat'
            ),
            'someFutureFormat'
        )
        _assert_raw_id(
            MicrosoftTeamsUserIdentifier(
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130'
            ),
            '8:orgid:45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        _assert_raw_id(
            MicrosoftTeamsUserIdentifier(
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                cloud='PUBLIC'
            ),
            '8:orgid:45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        _assert_raw_id(
            MicrosoftTeamsUserIdentifier(
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                cloud='DOD'
            ),
            '8:dod:45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        _assert_raw_id(
            MicrosoftTeamsUserIdentifier(
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                cloud='GCCH'
            ),
            '8:gcch:45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        _assert_raw_id(
            MicrosoftTeamsUserIdentifier(
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                is_anonymous=False
            ),
            '8:orgid:45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        _assert_raw_id(
            MicrosoftTeamsUserIdentifier(
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                is_anonymous=True
            ),
            '8:teamsvisitor:45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        _assert_raw_id(
            MicrosoftTeamsUserIdentifier(
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                raw_id='8:orgid:legacyFormat'
            ),
            '8:orgid:legacyFormat'
        )
        _assert_raw_id(
            PhoneNumberIdentifier(
                value='+112345556789'
            ),
            '4:112345556789'
        )
        _assert_raw_id(
            PhoneNumberIdentifier(
                value='112345556789'
            ),
            '4:112345556789'
        )
        _assert_raw_id(
            PhoneNumberIdentifier(
                value='+112345556789',
                raw_id='4:otherFormat'
            ),
            '4:otherFormat'
        )
        _assert_raw_id(
            UnknownIdentifier(
                identifier='28:45ab2481-1c1c-4005-be24-0ffb879b1130'
            ),
            '28:45ab2481-1c1c-4005-be24-0ffb879b1130'
        )

    def test_identifier_from_raw_id(self):
        _assert_communication_identifier(
            '8:acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130',
            CommunicationUserIdentifier(
                id='8:acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
            )
        )
        _assert_communication_identifier(
            '8:spool:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130',
            CommunicationUserIdentifier(
                id='8:spool:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
            )
        )
        _assert_communication_identifier(
            '8:dod-acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130',
            CommunicationUserIdentifier(
                id='8:dod-acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
            )
        )
        _assert_communication_identifier(
            '8:gcch-acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130',
            CommunicationUserIdentifier(
                id='8:gcch-acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
            )
        )
        _assert_communication_identifier(
            '8:acs:something',
            CommunicationUserIdentifier(
                id='8:acs:something'
            )
        )
        _assert_communication_identifier(
            '8:orgid:45ab2481-1c1c-4005-be24-0ffb879b1130',
            MicrosoftTeamsUserIdentifier(
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                cloud='PUBLIC',
                is_anonymous=False
            )
        )
        _assert_communication_identifier(
            '8:dod:45ab2481-1c1c-4005-be24-0ffb879b1130',
            MicrosoftTeamsUserIdentifier(
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                cloud='DOD',
                is_anonymous=False
            )
        )
        _assert_communication_identifier(
            '8:gcch:45ab2481-1c1c-4005-be24-0ffb879b1130',
            MicrosoftTeamsUserIdentifier(
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                cloud='GCCH',
                is_anonymous=False
            )
        )
        _assert_communication_identifier(
            '8:teamsvisitor:45ab2481-1c1c-4005-be24-0ffb879b1130',
            MicrosoftTeamsUserIdentifier(
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                is_anonymous=True
            )
        )
        _assert_communication_identifier(
            '8:orgid:legacyFormat',
            MicrosoftTeamsUserIdentifier(
                user_id='legacyFormat',
                cloud='PUBLIC',
                is_anonymous=False
            )
        )
        _assert_communication_identifier(
            '4:112345556789',
            PhoneNumberIdentifier(
                value='+112345556789'
            )
        )
        _assert_communication_identifier(
            '4:otherFormat',
            PhoneNumberIdentifier(
                value='+otherFormat'
            )
        )
        _assert_communication_identifier(
            '28:45ab2481-1c1c-4005-be24-0ffb879b1130',
            UnknownIdentifier(
                identifier='28:45ab2481-1c1c-4005-be24-0ffb879b1130'
            )
        )
        _assert_communication_identifier(
            '',
            UnknownIdentifier(
                identifier=''
            )
        )
        with pytest.raises(Exception):
            identifier_from_raw_id(None)

    def test_roundtrip(self):
        _assert_roundtrip('8:acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130')
        _assert_roundtrip('8:spool:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130')
        _assert_roundtrip('8:dod-acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130')
        _assert_roundtrip('8:gcch-acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130')
        _assert_roundtrip('8:acs:something')
        _assert_roundtrip('8:orgid:45ab2481-1c1c-4005-be24-0ffb879b1130')
        _assert_roundtrip('8:dod:45ab2481-1c1c-4005-be24-0ffb879b1130')
        _assert_roundtrip('8:gcch:45ab2481-1c1c-4005-be24-0ffb879b1130')
        _assert_roundtrip('8:teamsvisitor:45ab2481-1c1c-4005-be24-0ffb879b1130')
        _assert_roundtrip('8:orgid:legacyFormat')
        _assert_roundtrip('4:112345556789')
        _assert_roundtrip('4:otherFormat')
        _assert_roundtrip('28:45ab2481-1c1c-4005-be24-0ffb879b1130')
        _assert_roundtrip('')


def _assert_raw_id(identifier, want):
    # type: (CommunicationIdentifier, str) -> None
    assert identifier.raw_id == want


def _assert_communication_identifier(raw_id, want):
    # type: (str, CommunicationIdentifier) -> None
    got = identifier_from_raw_id(raw_id)
    assert got.raw_id == want.raw_id
    assert got.kind == want.kind
    assert len(got.properties) == len(want.properties)
    for key in want.properties:
        assert key in got.properties
        assert got.properties[key] == want.properties[key]


def _assert_roundtrip(raw_id):
    # type: (str) -> None
    assert identifier_from_raw_id(raw_id).raw_id == raw_id