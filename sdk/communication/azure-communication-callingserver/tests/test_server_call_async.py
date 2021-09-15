# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import _test_utils_async
import _test_constants

from typing import List
from parameterized import parameterized
from azure.communication.callingserver._shared.models import CommunicationIdentifier, CommunicationUserIdentifier
from azure.communication.callingserver._generated.models import (
    CancelAllMediaOperationsResult,
    AddParticipantResult
    )
from azure.communication.callingserver._models import (
    PlayAudioOptions
    )

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

def data_source_test_play_audio():
    options = PlayAudioOptions(
            loop = True,
            audio_file_id = _test_constants.AUDIO_FILE_ID,
            callback_uri = _test_constants.CALLBACK_URI,
            operation_context = _test_constants.OPERATION_CONTEXT
            )
    parameters = []
    parameters.append((
        _test_constants.ClientType_ConnectionString,
        _test_constants.SERVER_CALL_ID,
        _test_constants.AUDIO_FILE_URI,
        options,
        ))

    parameters.append((
        _test_constants.ClientType_ManagedIdentity,
        _test_constants.SERVER_CALL_ID,
        _test_constants.AUDIO_FILE_URI,
        options,
        True,
        ))

    return parameters

def data_source_test_add_participant():
    parameters = []
    parameters.append((
        _test_constants.ClientType_ConnectionString,
        _test_constants.SERVER_CALL_ID,
        CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
        _test_constants.CALLBACK_URI,
        _test_constants.PHONE_NUMBER,
        _test_constants.OPERATION_CONTEXT,
        ))

    parameters.append((
        _test_constants.ClientType_ManagedIdentity,
        _test_constants.SERVER_CALL_ID,
        CommunicationUserIdentifier(_test_constants.RESOURCE_SOURCE),
        _test_constants.CALLBACK_URI,
        _test_constants.PHONE_NUMBER,
        _test_constants.OPERATION_CONTEXT,
        True,
        ))

    return parameters

def data_source_test_remove_participant():

    parameters = []
    parameters.append((
        _test_constants.ClientType_ConnectionString,
        _test_constants.SERVER_CALL_ID,
        _test_constants.PARTICIPANT_ID,
        ))

    parameters.append((
        _test_constants.ClientType_ManagedIdentity,
        _test_constants.SERVER_CALL_ID,
        _test_constants.PARTICIPANT_ID,
        True,
        ))

    return parameters

def verify_play_audio_result(result):
    # type: (CancelAllMediaOperationsResult) -> None
    assert "dummyId" == result.operation_id
    assert "running" == result.status
    assert _test_constants.OPERATION_CONTEXT == result.operation_context
    assert 200 == result.result_info.code
    assert "dummyMessage" == result.result_info.message

def verify_add_participant_result(result):
    # type: (AddParticipantResult) -> None
    assert _test_constants.PARTICIPANT_ID == result.participant_id

@parameterized.expand(data_source_test_play_audio())
@pytest.mark.asyncio
async def test_play_audio_succeed(
    test_name, # type: str
    server_call_id, # type: str
    audio_file_uri, # type: str
    options, # type: PlayAudioOptions
    use_managed_identity = False # type: bool
    ):

    server_call = _test_utils_async.create_mock_server_call(
        server_call_id,
        status_code=202,
        payload=_test_constants.PlayAudioResponsePayload,
        use_managed_identity=use_managed_identity
        )

    result = await server_call.play_audio(audio_file_uri, options)
    verify_play_audio_result(result)

@parameterized.expand(data_source_test_play_audio())
@pytest.mark.asyncio
async def test_play_audio_failed(
    test_name, # type: str
    server_call_id, # type: str
    audio_file_uri, # type: str
    options, # type: PlayAudioOptions
    use_managed_identity = False # type: bool
    ):

    server_call = _test_utils_async.create_mock_server_call(
        server_call_id,
        status_code=404,
        payload=_test_constants.ErrorPayload,
        use_managed_identity = use_managed_identity
        )

    raised = False
    try:
        await server_call.play_audio(audio_file_uri, options)
    except:
        raised = True
    assert raised == True

@parameterized.expand(data_source_test_add_participant())
@pytest.mark.asyncio
async def test_add_participant_succeed(
    test_name, # type: str
    server_call_id, # type: str
    participant, # type: CommunicationIdentifier
    callback_uri, # type: str
    alternate_caller_id, # type: str
    operation_context, # type: str
    use_managed_identity = False # type: bool
    ):

    server_call = _test_utils_async.create_mock_server_call(
        server_call_id,
        status_code=202,
        payload=_test_constants.AddParticipantResultPayload,
        use_managed_identity=use_managed_identity
        )

    result = await server_call.add_participant(
        participant = participant,
        callback_uri = callback_uri,
        alternate_caller_id = alternate_caller_id,
        operation_context = operation_context
        )

    verify_add_participant_result(result)

@parameterized.expand(data_source_test_add_participant())
@pytest.mark.asyncio
async def test_add_participant_failed(
    test_name, # type: str
    server_call_id, # type: str
    participant, # type: CommunicationIdentifier
    callback_uri, # type: str
    alternate_caller_id, # type: str
    operation_context, # type: str
    use_managed_identity = False # type: bool
    ):

    server_call = _test_utils_async.create_mock_server_call(
        server_call_id,
        status_code=404,
        payload=_test_constants.ErrorPayload,
        use_managed_identity = use_managed_identity
        )

    raised = False
    try:
        await server_call.add_participant(
            participant = participant,
            callback_uri = callback_uri,
            alternate_caller_id = alternate_caller_id,
            operation_context = operation_context
            )
    except:
        raised = True
    assert raised == True

@parameterized.expand(data_source_test_remove_participant())
@pytest.mark.asyncio
async def test_remove_participant_succeed(
    test_name, # type: str
    server_call_id, # type: str
    participant_id, # type: str
    use_managed_identity = False # type: bool
    ):

    server_call = _test_utils_async.create_mock_server_call(
        server_call_id,
        status_code=202,
        payload=None,
        use_managed_identity=use_managed_identity
        )

    await server_call.remove_participant(
        participant_id = participant_id
        )
    assert server_call.server_call_id == _test_constants.SERVER_CALL_ID

@parameterized.expand(data_source_test_remove_participant())
@pytest.mark.asyncio
async def test_remove_participant_failed(
    test_name, # type: str
    server_call_id, # type: str
    participant_id, # type: str
    use_managed_identity = False # type: bool
    ):

    server_call = _test_utils_async.create_mock_server_call(
        server_call_id,
        status_code=404,
        payload=_test_constants.ErrorPayload,
        use_managed_identity = use_managed_identity
        )

    raised = False
    try:
        await server_call.remove_participant(
            participant_id = participant_id
            )
    except:
        raised = True
    assert raised == True

@pytest.mark.asyncio
async def test_start_recording_relative_uri_fails():
    server_call_id = "aHR0cHM6Ly9jb252LXVzd2UtMDguY29udi5za3lwZS5jb20vY29udi8tby1FWjVpMHJrS3RFTDBNd0FST1J3P2k9ODgmZT02Mzc1Nzc0MTY4MDc4MjQyOTM"
    server_call = _test_utils_async.create_calling_server_client_async().initialize_server_call(server_call_id)
    with pytest.raises(ValueError):
        await server_call.start_recording("/not/absolute/uri")
