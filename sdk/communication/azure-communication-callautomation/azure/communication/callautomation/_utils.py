# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING, Dict, Any, List, Optional, Union
from datetime import datetime

from ._shared.models import (
    CommunicationIdentifier,
    CommunicationUserIdentifier,
    PhoneNumberIdentifier,
    MicrosoftTeamsUserIdentifier,
    MicrosoftTeamsAppIdentifier,
    UnknownIdentifier,
    CommunicationIdentifierKind,
)
from ._generated.models import (
    CommunicationIdentifierModel,
    CommunicationUserIdentifierModel,
    PhoneNumberIdentifierModel,
    CallLocator,
    ExternalStorage,
    RecordingStorageKind,
    MicrosoftTeamsAppIdentifierModel,
)

if TYPE_CHECKING:
    from ._models import (
    ServerCallLocator,
    GroupCallLocator,
    RoomCallLocator,
    AzureBlobContainerRecordingStorage,
    AzureCommunicationsRecordingStorage
)

def build_external_storage(
    recording_storage: Union['AzureCommunicationsRecordingStorage',
                             'AzureBlobContainerRecordingStorage'] = None
) -> Optional[ExternalStorage]:
    request: Optional[ExternalStorage] = None
    if recording_storage:
        if recording_storage.kind == RecordingStorageKind.AZURE_BLOB_STORAGE:
            if not recording_storage.container_url:
                raise ValueError(
                    "Please provide container_url"
                    "when you set the recording_storage as AzureBlobContainerRecordingStorage"
                    )
            request = ExternalStorage(
                recording_storage_kind=recording_storage.kind,
                recording_destination_container_url=recording_storage.container_url
                )
    return request

def build_call_locator(
    call_locator: Optional[Union['ServerCallLocator', 'GroupCallLocator','RoomCallLocator']],
    server_call_id: Optional[str],
    group_call_id: Optional[str],
    room_id: Optional[str],
    args: List[Union['ServerCallLocator', 'GroupCallLocator','RoomCallLocator']] = None,
) -> CallLocator:
    """Build the generated callLocator object from args in kwargs with support for legacy models.

    :param args: Any positional parameters provided. This may include the legacy model. The new method signature
     does not support positional params, so if there's anything here, it's the old model.
    :type args: list[ServerCallLocator or GroupCallLocator or RoomCallLocator]
    :param call_locator: If the legacy call_locator was provided via keyword arg.
    :type call_locator: ServerCallLocator or GroupCallLocator or RoomCallLocator or None
    :param server_call_id: If the new server_call_id was provided via keyword arg.
    :type server_call_id: str or None
    :param group_call_id: If the new group_call_id was provided via keyword arg.
    :type group_call_id: str or None
    :param room_id: If the new room_id was provided via keyword arg.
    :type room_id: str or None
    :return: Generated CallLocator for the request body.
    """
    request: Optional[CallLocator] = None
    if args:
        if len(args) > 1:
            raise TypeError(f"Unexpected positional arguments: {args[1:]}")
        request = args[0]._to_generated()  # pylint:disable=protected-access

    if call_locator:
        if request is not None:
            raise ValueError(
                "Received multiple values for call_locator. "
                "Please provide either 'group_call_id' or 'server_call_id'."
            )
        request = call_locator._to_generated()  # pylint:disable=protected-access
    if group_call_id:
        if request is not None:
            raise ValueError(
                "Received multiple values for call locator. "
                "Please provide either 'group_call_id' or 'server_call_id'."
            )
        request = CallLocator(group_call_id=group_call_id, kind="groupCallLocator")
    if server_call_id:
        if request is not None:
            raise ValueError(
                "Received multiple values for call locator. "
                "Please provide either 'group_call_id' or 'server_call_id'."
            )
        request = CallLocator(server_call_id=server_call_id, kind="serverCallLocator")
    if room_id:
        if request is not None:
            raise ValueError(
                "Received multiple values for call locator. "
                "Please provide either 'group_call_id' or 'server_call_id' or 'room_id'."
            )
        request = CallLocator(room_id=room_id, kind="roomCallLocator")
    return request

def process_repeatability_first_sent(keywords: Dict[str, Any]) -> None:
    if "headers" in keywords:
        if "Repeatability-First-Sent" not in keywords["headers"]:
            keywords["headers"]["Repeatability-First-Sent"] = get_repeatability_timestamp()
    else:
        keywords["headers"] = {"Repeatability-First-Sent": get_repeatability_timestamp()}


def get_repeatability_timestamp() -> str:
    return datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")


def serialize_identifier(identifier: CommunicationIdentifier) -> Dict[str, Any]:
    """Serialize the Communication identifier into CommunicationIdentifierModel

    :param identifier: Identifier object
    :type identifier: CommunicationIdentifier
    :return: CommunicationIdentifierModel
    :rtype: dict[str, any]
    """
    try:
        request_model = {"raw_id": identifier.raw_id}
        if identifier.kind and identifier.kind != CommunicationIdentifierKind.UNKNOWN:
            request_model[identifier.kind] = dict(identifier.properties)
        return request_model
    except AttributeError:
        raise TypeError(f"Unsupported identifier type: {identifier.__class__.__name__}") from None


def serialize_phone_identifier(identifier: Optional[PhoneNumberIdentifier]) -> Optional[PhoneNumberIdentifierModel]:
    """Serialize the Communication identifier into CommunicationIdentifierModel

    :param identifier: PhoneNumberIdentifier
    :type identifier: PhoneNumberIdentifier
    :return: PhoneNumberIdentifierModel
    :rtype: ~azure.communication.callautomation._generated.models.PhoneNumberIdentifierModel
    """
    if identifier is None:
        return None
    try:
        if identifier.kind and identifier.kind == CommunicationIdentifierKind.PHONE_NUMBER:
            request_model = PhoneNumberIdentifierModel(value=identifier.properties["value"])
            return request_model
    except AttributeError:
        pass
    raise TypeError(f"Unsupported phone identifier type: {identifier.__class__.__name__}")


def serialize_communication_user_identifier(
    identifier: Optional[CommunicationUserIdentifier],
) -> Optional[CommunicationUserIdentifierModel]:
    """Serialize the CommunicationUserIdentifier into CommunicationUserIdentifierModel

    :param identifier: CommunicationUserIdentifier
    :type identifier: CommunicationUserIdentifier
    :return: CommunicationUserIdentifierModel
    :rtype: ~azure.communication.callautomation._generated.models.CommunicationUserIdentifierModel
    """
    if identifier is None:
        return None
    try:
        if identifier.kind and identifier.kind == CommunicationIdentifierKind.COMMUNICATION_USER:
            request_model = CommunicationUserIdentifierModel(id=identifier.properties["id"])
            return request_model
    except AttributeError:
        pass
    raise TypeError(f"Unsupported user identifier type: {identifier.__class__.__name__}")


def serialize_msft_teams_app_identifier(
    identifier: Optional[MicrosoftTeamsAppIdentifier],
) -> Optional[MicrosoftTeamsAppIdentifierModel]:
    """Serialize the MicrosoftTeamsAppIdentifier into MicrosoftTeamsAppIdentifierModel

    :param identifier: MicrosoftTeamsAppIdentifier
    :type identifier: MicrosoftTeamsAppIdentifier
    :return: MicrosoftTeamsAppIdentifierModel
    :rtype: ~azure.communication.callautomation._generated.models.MicrosoftTeamsAppIdentifierModel
    """
    if identifier is None:
        return None
    try:
        if identifier.kind and identifier.kind == CommunicationIdentifierKind.MICROSOFT_TEAMS_APP:
            request_model = MicrosoftTeamsAppIdentifierModel(app_id=identifier.properties["app_id"])
            return request_model
    except AttributeError:
        pass
    raise TypeError(f"Unsupported user identifier type: {identifier.__class__.__name__}")


def deserialize_identifier(identifier_model: CommunicationIdentifierModel) -> CommunicationIdentifier:
    """
    Deserialize the CommunicationIdentifierModel into Communication Identifier

    :param identifier_model: CommunicationIdentifierModel
    :type identifier_model: CommunicationIdentifierModel
    :return: CommunicationIdentifier
    :rtype: ~azure.communication.callautomation.CommunicationIdentifier
    """
    raw_id = identifier_model.raw_id

    if identifier_model.communication_user:
        return CommunicationUserIdentifier(raw_id, raw_id=raw_id)
    if identifier_model.phone_number:
        return PhoneNumberIdentifier(identifier_model.phone_number.value, raw_id=raw_id)
    if identifier_model.microsoft_teams_user:
        return MicrosoftTeamsUserIdentifier(
            raw_id=raw_id,
            user_id=identifier_model.microsoft_teams_user.user_id,
            is_anonymous=identifier_model.microsoft_teams_user.is_anonymous,
            cloud=identifier_model.microsoft_teams_user.cloud,
        )
    if identifier_model.microsoft_teams_app:
        return MicrosoftTeamsAppIdentifier(
            raw_id=raw_id,
            app_id=identifier_model.microsoft_teams_app.app_id,
            cloud=identifier_model.microsoft_teams_app.cloud,
        )
    return UnknownIdentifier(raw_id)


def deserialize_phone_identifier(identifier_model: PhoneNumberIdentifierModel) -> Union[PhoneNumberIdentifier, None]:
    """
    Deserialize the PhoneNumberIdentifierModel into PhoneNumberIdentifier

    :param identifier_model: PhoneNumberIdentifierModel
    :type identifier_model: PhoneNumberIdentifierModel
    :return: PhoneNumberIdentifier
    :rtype: ~azure.communication.callautomation.PhoneNumberIdentifier
    """
    if identifier_model:
        return PhoneNumberIdentifier(identifier_model.value)
    return None


def deserialize_comm_user_identifier(
    identifier_model: CommunicationUserIdentifierModel,
) -> Union[CommunicationUserIdentifier, None]:
    """
    Deserialize the CommunicationUserIdentifierModel into CommunicationUserIdentifier

    :param identifier_model: CommunicationUserIdentifierModel
    :type identifier_model: CommunicationUserIdentifierModel
    :return: CommunicationUserIdentifier
    :rtype: ~azure.communication.callautomation.CommunicationUserIdentifier
    """
    return CommunicationUserIdentifier(id=identifier_model.id) if identifier_model else None


def deserialize_msft_teams_app_identifier(
    identifier_model: MicrosoftTeamsAppIdentifierModel,
) -> Union[MicrosoftTeamsAppIdentifier, None]:
    """
    Deserialize the MicrosoftTeamsAppIdentifierModel into MicrosoftTeamsAppIdentifier

    :param identifier_model: MicrosoftTeamsAppIdentifierModel
    :type identifier_model: MicrosoftTeamsAppIdentifierModel
    :return: MicrosoftTeamsAppIdentifier
    :rtype: ~azure.communication.callautomation.MicrosoftTeamsAppIdentifier
    """
    if identifier_model:
        return MicrosoftTeamsAppIdentifier(identifier_model.app_id)
    return None
