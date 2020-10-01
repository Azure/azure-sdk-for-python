# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .base import IntegrationTestBase, ReplayableTest, LiveTest
from .exceptions import AzureTestError, AzureNameError, NameInUseError, ReservedResourceNameError
from .decorators import live_only, record_only, AllowLargeResponse
from .patches import mock_in_unit_test, patch_time_sleep_api, patch_long_run_operation_delay
from .preparers import AbstractPreparer, SingleValueReplacer
from .recording_processors import (
    RecordingProcessor, SubscriptionRecordingProcessor,
    LargeRequestBodyProcessor, LargeResponseBodyProcessor, LargeResponseBodyReplacer, AuthenticationMetadataFilter,
    OAuthRequestResponsesFilter, DeploymentNameReplacer, GeneralNameReplacer, AccessTokenReplacer, RequestUrlNormalizer,
)
from .utilities import create_random_name, get_sha1_hash

__all__ = ['IntegrationTestBase', 'ReplayableTest', 'LiveTest',
           'AzureTestError', 'AzureNameError', 'NameInUseError', 'ReservedResourceNameError',
           'mock_in_unit_test', 'patch_time_sleep_api', 'patch_long_run_operation_delay',
           'AbstractPreparer', 'SingleValueReplacer', 'AllowLargeResponse',
           'RecordingProcessor', 'SubscriptionRecordingProcessor',
           'LargeRequestBodyProcessor', 'LargeResponseBodyProcessor', 'LargeResponseBodyReplacer',
           'AuthenticationMetadataFilter', 'OAuthRequestResponsesFilter',
           'DeploymentNameReplacer', 'GeneralNameReplacer',
           'AccessTokenReplacer', 'RequestUrlNormalizer',
           'live_only', 'record_only',
           'create_random_name', 'get_sha1_hash']
__version__ = '0.5.2'
