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
            '4:+112345556789'
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
            PhoneNumberIdentifier(
                value='otherFormat',
                raw_id='4:207ffef6-9444-41fb-92ab-20eacaae2768'
            ),
            '4:207ffef6-9444-41fb-92ab-20eacaae2768'
        )
        # cspell:disable
        _assert_raw_id(
            PhoneNumberIdentifier(
                value='otherFormat',
                raw_id='4:207ffef6-9444-41fb-92ab-20eacaae2768_207ffef6-9444-41fb-92ab-20eacaae2768'
            ),
            '4:207ffef6-9444-41fb-92ab-20eacaae2768_207ffef6-9444-41fb-92ab-20eacaae2768'
        )
        _assert_raw_id(
            PhoneNumberIdentifier(
                value='otherFormat',
                raw_id='4:+112345556789_207ffef6-9444-41fb-92ab-20eacaae2768'
            ),
            '4:+112345556789_207ffef6-9444-41fb-92ab-20eacaae2768'
        )
        _assert_raw_id(
            MicrosoftBotIdentifier(
                bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130'
            ),
            '28:orgid:45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        _assert_raw_id(
            MicrosoftBotIdentifier(
                bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                is_resource_account_configured=False,
                cloud=CommunicationCloudEnvironment.PUBLIC
            ),
            '28:45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        _assert_raw_id(
            MicrosoftBotIdentifier(
                bot_id='01234567-89ab-cdef-0123-456789abcdef',
                is_resource_account_configured=False,
                cloud=CommunicationCloudEnvironment.GCCH
            ),
            '28:gcch-global:01234567-89ab-cdef-0123-456789abcdef'
        )
        _assert_raw_id(
            MicrosoftBotIdentifier(
                bot_id='01234567-89ab-cdef-0123-456789abcdef',
                is_resource_account_configured=False,
                cloud=CommunicationCloudEnvironment.DOD
            ),
            '28:dod-global:01234567-89ab-cdef-0123-456789abcdef'
        )
        _assert_raw_id(
            MicrosoftBotIdentifier(
                bot_id='01234567-89ab-cdef-0123-456789abcdef',
                is_resource_account_configured=True,
                cloud=CommunicationCloudEnvironment.PUBLIC
            ),
            '28:orgid:01234567-89ab-cdef-0123-456789abcdef'
        )
        _assert_raw_id(
            MicrosoftBotIdentifier(
                bot_id='01234567-89ab-cdef-0123-456789abcdef',
                is_resource_account_configured=True,
                cloud=CommunicationCloudEnvironment.GCCH
            ),
            '28:gcch:01234567-89ab-cdef-0123-456789abcdef'
        )
        _assert_raw_id(
            MicrosoftBotIdentifier(
                bot_id='01234567-89ab-cdef-0123-456789abcdef',
                is_resource_account_configured=True,
                cloud=CommunicationCloudEnvironment.DOD
            ),
            '28:dod:01234567-89ab-cdef-0123-456789abcdef'
        )
        # cspell:enable
        _assert_raw_id(
            UnknownIdentifier(
                identifier='28:ag08-global:01234567-89ab-cdef-0123-456789abcdef'
            ),
            '28:ag08-global:01234567-89ab-cdef-0123-456789abcdef'
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
                user_id='45ab2481-1c1c-4005-be24-0ffb879b1130'
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
            '28:45ab2481-1c1c-4005-be24-0ffb879b1130',
            MicrosoftBotIdentifier(
                bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
                cloud=CommunicationCloudEnvironment.PUBLIC,
                is_resource_account_configured=False
            )
        )
        _assert_communication_identifier(
            '28:gcch-global:01234567-89ab-cdef-0123-456789abcdef',
            MicrosoftBotIdentifier(
                bot_id='01234567-89ab-cdef-0123-456789abcdef',
                cloud=CommunicationCloudEnvironment.GCCH,
                is_resource_account_configured=False
            )
        )
        _assert_communication_identifier(
            '28:dod-global:01234567-89ab-cdef-0123-456789abcdef',
            MicrosoftBotIdentifier(
                bot_id='01234567-89ab-cdef-0123-456789abcdef',
                cloud=CommunicationCloudEnvironment.DOD,
                is_resource_account_configured=False
            )
        )
        _assert_communication_identifier(
            '28:orgid:01234567-89ab-cdef-0123-456789abcdef',
            MicrosoftBotIdentifier(
                bot_id='01234567-89ab-cdef-0123-456789abcdef',
                cloud=CommunicationCloudEnvironment.PUBLIC,
                is_resource_account_configured=True
            )
        )
        _assert_communication_identifier(
            '28:gcch:01234567-89ab-cdef-0123-456789abcdef',
            MicrosoftBotIdentifier(
                bot_id='01234567-89ab-cdef-0123-456789abcdef',
                cloud=CommunicationCloudEnvironment.GCCH,
                is_resource_account_configured=True
            )
        )
        _assert_communication_identifier(
            '28:dod:01234567-89ab-cdef-0123-456789abcdef',
            MicrosoftBotIdentifier(
                bot_id='01234567-89ab-cdef-0123-456789abcdef',
                cloud=CommunicationCloudEnvironment.DOD,
                is_resource_account_configured=True
            )
        )
        _assert_communication_identifier(
            '4:+112345556789',
            PhoneNumberIdentifier(
                value='+112345556789'
            )
        )
        _assert_communication_identifier(
            '4:112345556789',
            PhoneNumberIdentifier(
                value='112345556789'
            )
        )
        _assert_communication_identifier(
            '4:otherFormat',
            PhoneNumberIdentifier(
                value='otherFormat'
            )
        )
        _assert_communication_identifier(
            '4:207ffef6-9444-41fb-92ab-20eacaae2768',
            PhoneNumberIdentifier(
                value='207ffef6-9444-41fb-92ab-20eacaae2768'
            )
        )
        # cspell:disable
        _assert_communication_identifier(
            '4:207ffef6-9444-41fb-92ab-20eacaae2768_207ffef6-9444-41fb-92ab-20eacaae2768',
            PhoneNumberIdentifier(
                value='207ffef6-9444-41fb-92ab-20eacaae2768_207ffef6-9444-41fb-92ab-20eacaae2768'
            )
        )
        _assert_communication_identifier(
            '4:+112345556789_207ffef6-9444-41fb-92ab-20eacaae2768',
            PhoneNumberIdentifier(
                value='+112345556789_207ffef6-9444-41fb-92ab-20eacaae2768'
            )
        )
        # cspell:enable
        _assert_communication_identifier(
            '28:ag08-global:01234567-89ab-cdef-0123-456789abcdef',
            UnknownIdentifier(
                identifier='28:ag08-global:01234567-89ab-cdef-0123-456789abcdef'
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
        _assert_roundtrip('4:+112345556789')
        _assert_roundtrip('4:112345556789')
        _assert_roundtrip('4:otherFormat')
        _assert_roundtrip("4:207ffef6-9444-41fb-92ab-20eacaae2768")
        # cspell:disable
        _assert_roundtrip("4:207ffef6-9444-41fb-92ab-20eacaae2768_207ffef6-9444-41fb-92ab-20eacaae2768")
        _assert_roundtrip("4:+112345556789_207ffef6-9444-41fb-92ab-20eacaae2768")
        # cspell:enable
        _assert_roundtrip('28:45ab2481-1c1c-4005-be24-0ffb879b1130')
        _assert_roundtrip('28:gcch-global:01234567-89ab-cdef-0123-456789abcdef')
        _assert_roundtrip('28:dod-global:01234567-89ab-cdef-0123-456789abcdef')
        _assert_roundtrip('28:orgid:01234567-89ab-cdef-0123-456789abcdef')
        _assert_roundtrip('28:gcch:01234567-89ab-cdef-0123-456789abcdef')
        _assert_roundtrip('28:dod:01234567-89ab-cdef-0123-456789abcdef')
        _assert_roundtrip('28:dod:01234567-89ab-cdef-0123-456789abcdef')
        _assert_roundtrip('')

    def test_equality_based_on_raw_id(self):
        # CommunicationUserIdentifiers are equal.
        assert CommunicationUserIdentifier(
            id='8:acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
        ) == CommunicationUserIdentifier(
            id='8:acs:bbbcbc1e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
        )

        # CommunicationUserIdentifiers are not equal.
        assert CommunicationUserIdentifier(
            id='8:acs:6666e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
        ) != CommunicationUserIdentifier(
            id='8:acs:555e-9f06-482a-b5d8-20e3f26ef0cd_45ab2481-1c1c-4005-be24-0ffb879b1130'
        )

        # MicrosoftTeamsUserIdentifiers are equal.
        assert MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130'
        ) == MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        assert MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='PUBLIC'
        ) == MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='PUBLIC'
        )
        assert MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='DOD'
        ) == MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='DOD'
        )
        assert MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='GCCH'
        ) == MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='GCCH'
        )
        assert MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='GCCH',
            is_anonymous=False
        ) == MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='GCCH',
            is_anonymous=False
        )
        assert MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='GCCH',
            is_anonymous=True
        ) == MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='GCCH',
            is_anonymous=True
        )

        # MicrosoftTeamsUserIdentifiers are not equal.
        assert MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130'
        ) != MicrosoftTeamsUserIdentifier(
            user_id='55ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        assert MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='GCCH'
        ) != MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='DOD'
        )
        assert MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='GCCH',
            is_anonymous=False
        ) != MicrosoftTeamsUserIdentifier(
            user_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            cloud='GCCH',
            is_anonymous=True
        )

        # PhoneNumberIdentifiers are equal.
        assert PhoneNumberIdentifier(
            value='+112345556789'
        ) == PhoneNumberIdentifier(
            value='+112345556789'
        )

        # PhoneNumberIdentifiers are not equal.
        assert PhoneNumberIdentifier(
            value='+112345556789'
        ) != PhoneNumberIdentifier(
            value='+512345556789'
        )

        # MicrosoftBotIdentifiers are equal.
        assert MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130'
        ) == MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130'
        )
        assert MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.PUBLIC
        ) == MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.PUBLIC
        )
        assert MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.GCCH
        ) == MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.GCCH
        )
        assert MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=False,
        ) == MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.PUBLIC
        )
        assert MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=True,
        ) == MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=True,
            cloud=CommunicationCloudEnvironment.PUBLIC
        )
        assert MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
        ) == MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=True,
            cloud=CommunicationCloudEnvironment.PUBLIC
        )

        # MicrosoftBotIdentifiers are not equal.
        assert MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.DOD
        ) != MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.GCCH
        )
        assert MicrosoftBotIdentifier(
            bot_id='55666-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.DOD
        ) != MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.DOD
        )
        assert MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=True,
            cloud=CommunicationCloudEnvironment.GCCH
        ) != MicrosoftBotIdentifier(
            bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
            is_resource_account_configured=False,
            cloud=CommunicationCloudEnvironment.GCCH
        )

        # MicrosoftBotIdentifiers are equal.
        assert UnknownIdentifier(
            identifier='28:ag08-global:01234567-89ab-cdef-0123-456789abcdef'
        ) == UnknownIdentifier(
            identifier='28:ag08-global:01234567-89ab-cdef-0123-456789abcdef'
        )

        # MicrosoftBotIdentifiers are not equal.
        assert UnknownIdentifier(
            identifier='48:8888-global:01234567-89ab-cdef-0123-456789abcdef'
        ) != UnknownIdentifier(
            identifier='48:ag08-global:01234567-89ab-cdef-0123-456789abcdef'
        )

def test_default_cloud_for_bot_identifier_is_public():
    bot = MicrosoftBotIdentifier(
        bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130',
        is_resource_account_configured=False)

    assert bot.properties['cloud'] == CommunicationCloudEnvironment.PUBLIC

def test_default_is_resource_account_configured_for_bot_identifier_is_true():
    bot = MicrosoftBotIdentifier(bot_id='45ab2481-1c1c-4005-be24-0ffb879b1130')

    assert bot.properties['is_resource_account_configured'] is True


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
