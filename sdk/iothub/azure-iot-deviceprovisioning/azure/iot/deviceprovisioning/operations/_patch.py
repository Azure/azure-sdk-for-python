# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import sys
from io import IOBase
from typing import IO, Any, Callable, Dict, Optional, TypeVar, Union, cast

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.paging import ItemPaged
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from ._operations import (
    DeviceRegistrationStateOperations as DeviceRegistrationStateOperationsGenerated,
)
from ._operations import EnrollmentGroupOperations as EnrollmentGroupOperationsGenerated
from ._operations import EnrollmentOperations as EnrollmentOperationsGenerated
from ._operations import (
    build_device_registration_state_query_request,
    build_enrollment_group_query_request,
    build_enrollment_query_request,
)

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[
    Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]
]


def _extract_data_default(pipeline_response, **kwargs):
    response = pipeline_response.http_response
    response_json = response.json() if response.content else None
    continuation = response.headers.get("x-ms-continuation", None)
    cls: ClsType[JSON] = kwargs.pop("cls", None)
    if cls:
        return cls(pipeline_response, cast(JSON, response_json), {})
    return continuation or None, cast(JSON, response_json)


class EnrollmentOperations(EnrollmentOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.iot.deviceprovisioning.DeviceProvisioningClient`'s
        :attr:`enrollment` attribute.
    """

    @distributed_trace
    def query(  # type: ignore[override]
        self,
        query_specification: Union[JSON, IO],
        *,
        top: Optional[int] = None,
        **kwargs: Any,
    ) -> ItemPaged[JSON]:
        """Query the device enrollment records.

        Query the device enrollment records.

        :param query_specification: The query specification. Is either a JSON type or a IO type.
         Required.
        :type query_specification: JSON or IO
        :keyword top: Page size. Default value is None.
        :paramtype top: Optional[int]
        :return: list of JSON object
        :rtype: ~azure.core.paging.ItemPaged[JSON]
        :raises ~azure.core.exceptions.HttpResponseError

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                query_specification = {
                    "query": "str"  # Required.
                }

                # response body for status code(s): 200
                response == [
                    {
                        "attestation": {
                            "type": "str",  # Attestation Type. Required. Known values
                              are: "none", "tpm", "x509", and "symmetricKey".
                            "symmetricKey": {
                                "primaryKey": "str",  # Optional. Primary symmetric
                                  key.
                                "secondaryKey": "str"  # Optional. Secondary
                                  symmetric key.
                            },
                            "tpm": {
                                "endorsementKey": "str",  # Required.
                                "storageRootKey": "str"  # Optional. TPM attestation
                                  method.
                            },
                            "x509": {
                                "caReferences": {
                                    "primary": "str",  # Optional. Primary and
                                      secondary CA references.
                                    "secondary": "str"  # Optional. Primary and
                                      secondary CA references.
                                },
                                "clientCertificates": {
                                    "primary": {
                                        "certificate": "str",  # Optional.
                                          Certificate and Certificate info.
                                        "info": {
                                            "issuerName": "str",  #
                                              Required.
                                            "notAfterUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "notBeforeUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "serialNumber": "str",  #
                                              Required.
                                            "sha1Thumbprint": "str",  #
                                              Required.
                                            "sha256Thumbprint": "str",  #
                                              Required.
                                            "subjectName": "str",  #
                                              Required.
                                            "version": 0  # Required.
                                        }
                                    },
                                    "secondary": {
                                        "certificate": "str",  # Optional.
                                          Certificate and Certificate info.
                                        "info": {
                                            "issuerName": "str",  #
                                              Required.
                                            "notAfterUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "notBeforeUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "serialNumber": "str",  #
                                              Required.
                                            "sha1Thumbprint": "str",  #
                                              Required.
                                            "sha256Thumbprint": "str",  #
                                              Required.
                                            "subjectName": "str",  #
                                              Required.
                                            "version": 0  # Required.
                                        }
                                    }
                                },
                                "signingCertificates": {
                                    "primary": {
                                        "certificate": "str",  # Optional.
                                          Certificate and Certificate info.
                                        "info": {
                                            "issuerName": "str",  #
                                              Required.
                                            "notAfterUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "notBeforeUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "serialNumber": "str",  #
                                              Required.
                                            "sha1Thumbprint": "str",  #
                                              Required.
                                            "sha256Thumbprint": "str",  #
                                              Required.
                                            "subjectName": "str",  #
                                              Required.
                                            "version": 0  # Required.
                                        }
                                    },
                                    "secondary": {
                                        "certificate": "str",  # Optional.
                                          Certificate and Certificate info.
                                        "info": {
                                            "issuerName": "str",  #
                                              Required.
                                            "notAfterUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "notBeforeUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "serialNumber": "str",  #
                                              Required.
                                            "sha1Thumbprint": "str",  #
                                              Required.
                                            "sha256Thumbprint": "str",  #
                                              Required.
                                            "subjectName": "str",  #
                                              Required.
                                            "version": 0  # Required.
                                        }
                                    }
                                }
                            }
                        },
                        "registrationId": "str",  # This id is used to uniquely identify a
                          device registration of an enrollment."nA case-insensitive string (up to 128
                          characters long) of alphanumeric characters plus certain special characters :
                          . _ -. No special characters allowed at start or end. Required.
                        "allocationPolicy": "str",  # Optional. The allocation policy of this
                          resource. This policy overrides the tenant level allocation policy for this
                          individual enrollment or enrollment group. Possible values include 'hashed':
                          Linked IoT hubs are equally likely to have devices provisioned to them,
                          'geoLatency':  Devices are provisioned to an IoT hub with the lowest latency
                          to the device.If multiple linked IoT hubs would provide the same lowest
                          latency, the provisioning service hashes devices across those hubs, 'static'
                          : Specification of the desired IoT hub in the enrollment list takes priority
                          over the service-level allocation policy, 'custom': Devices are provisioned
                          to an IoT hub based on your own custom logic. The provisioning service passes
                          information about the device to the logic, and the logic returns the desired
                          IoT hub as well as the desired initial configuration. We recommend using
                          Azure Functions to host your logic. Known values are: "hashed", "geoLatency",
                          "static", and "custom".
                        "capabilities": {
                            "iotEdge": False  # Default value is False. If set to true,
                              this device is an IoTEdge device. Required.
                        },
                        "createdDateTimeUtc": "2020-02-20 00:00:00",  # Optional. The
                          DateTime this resource was created.
                        "customAllocationDefinition": {
                            "apiVersion": "str",  # The API version of the provisioning
                              service types (such as Enrollment) sent in the custom
                              allocation request. Minimum supported version: "2018-09-01-preview".
                              Required.
                            "webhookUrl": "str"  # The webhook URL used for allocation
                              requests. Required.
                        },
                        "deviceId": "str",  # Optional. Desired IoT Hub device ID (optional).
                        "etag": "str",  # Optional. The entity tag associated with the
                          resource.
                        "initialTwin": {
                            "properties": {
                                "desired": {
                                    "count": 0,  # Optional. Number of properties
                                      in the TwinCollection.
                                    "metadata": {
                                        "lastUpdated": "2020-02-20 00:00:00",
                                          # Optional. Last time the TwinCollection was updated.
                                        "lastUpdatedVersion": 0  # Optional.
                                          This is null for reported properties metadata and is not null
                                          for desired properties metadata.
                                    },
                                    "version": 0  # Optional. Version of the
                                      TwinCollection.
                                }
                            },
                            "tags": {
                                "count": 0,  # Optional. Number of properties in the
                                  TwinCollection.
                                "metadata": {
                                    "lastUpdated": "2020-02-20 00:00:00",  #
                                      Optional. Last time the TwinCollection was updated.
                                    "lastUpdatedVersion": 0  # Optional. This is
                                      null for reported properties metadata and is not null for desired
                                      properties metadata.
                                },
                                "version": 0  # Optional. Version of the
                                  TwinCollection.
                            }
                        },
                        "iotHubHostName": "str",  # Optional. The Iot Hub host name.
                        "iotHubs": [
                            "str"  # Optional. The list of IoT Hub hostnames the
                              device(s) in this resource can be allocated to. Must be a subset of
                              tenant level list of IoT hubs.
                        ],
                        "lastUpdatedDateTimeUtc": "2020-02-20 00:00:00",  # Optional. The
                          DateTime this resource was last updated.
                        "optionalDeviceInformation": {
                            "count": 0,  # Optional. Number of properties in the
                              TwinCollection.
                            "metadata": {
                                "lastUpdated": "2020-02-20 00:00:00",  # Optional.
                                  Last time the TwinCollection was updated.
                                "lastUpdatedVersion": 0  # Optional. This is null for
                                  reported properties metadata and is not null for desired properties
                                  metadata.
                            },
                            "version": 0  # Optional. Version of the TwinCollection.
                        },
                        "provisioningStatus": "enabled",  # Optional. Default value is
                          "enabled". The provisioning status. Known values are: "enabled" and
                          "disabled".
                        "registrationState": {
                            "assignedHub": "str",  # Optional. Assigned Azure IoT Hub.
                            "createdDateTimeUtc": "2020-02-20 00:00:00",  # Optional.
                              Registration create date time (in UTC).
                            "deviceId": "str",  # Optional. Device ID.
                            "errorCode": 0,  # Optional. Error code.
                            "errorMessage": "str",  # Optional. Error message.
                            "etag": "str",  # Optional. The entity tag associated with
                              the resource.
                            "lastUpdatedDateTimeUtc": "2020-02-20 00:00:00",  # Optional.
                              Last updated date time (in UTC).
                            "payload": {},  # Optional. Custom allocation payload
                              returned from the webhook to the device.
                            "registrationId": "str",  # Optional. This id is used to
                              uniquely identify a device registration of an enrollment."nA
                              case-insensitive string (up to 128 characters long) of alphanumeric
                              characters plus certain special characters : . _ -. No special characters
                              allowed at start or end.
                            "status": "str",  # Optional. Enrollment status. Known values
                              are: "unassigned", "assigning", "assigned", "failed", and "disabled".
                            "substatus": "str"  # Optional. Substatus for 'Assigned'
                              devices. Possible values include - 'initialAssignment': Device has been
                              assigned to an IoT hub for the first time, 'deviceDataMigrated': Device
                              has been assigned to a different IoT hub and its device data was migrated
                              from the previously assigned IoT hub. Device data was removed from the
                              previously assigned IoT hub, 'deviceDataReset':  Device has been assigned
                              to a different IoT hub and its device data was populated from the initial
                              state stored in the enrollment. Device data was removed from the
                              previously assigned IoT hub, 'reprovisionedToInitialAssignment': Device
                              has been re-provisioned to a previously assigned IoT hub. Known values
                              are: "initialAssignment", "deviceDataMigrated", "deviceDataReset", and
                              "reprovisionedToInitialAssignment".
                        },
                        "reprovisionPolicy": {
                            "migrateDeviceData": True,  # Default value is True. When set
                              to true (default), the Device Provisioning Service will migrate the
                              device's data (twin, device capabilities, and device ID) from one IoT hub
                              to another during an IoT hub assignment update. If set to false, the
                              Device Provisioning Service will reset the device's data to the initial
                              desired configuration stored in the corresponding enrollment list.
                            "updateHubAssignment": True  # Default value is True. When
                              set to true (default), the Device Provisioning Service will evaluate the
                              device's IoT Hub assignment and update it if necessary for any
                              provisioning requests beyond the first from a given device. If set to
                              false, the device will stay assigned to its current IoT hub.
                        }
                    }
                ]
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop("Content-Type", None)
        )

        content_type = content_type or "application/json"
        _json = None
        _content = None
        if isinstance(query_specification, (IOBase, bytes)):
            _content = query_specification
        else:
            _json = query_specification

        def prepare_request(continuation_token=None):
            if not continuation_token:
                request = build_enrollment_query_request(
                    x_ms_max_item_count=top,
                    content_type=content_type,
                    api_version=self._config.api_version,
                    json=_json,
                    content=_content,
                    headers=_headers,
                    params=_params,
                    **kwargs,
                )
            else:
                request = build_enrollment_query_request(
                    x_ms_max_item_count=top,
                    x_ms_continuation=continuation_token,
                    content_type=content_type,
                    api_version=self._config.api_version,
                    json=_json,
                    content=_content,
                    headers=_headers,
                    params=_params,
                    **kwargs,
                )
            request.url = self._client.format_url(request.url)
            return request

        def get_next(continuation_token: Optional[str] = None):
            request = prepare_request(continuation_token)
            pipeline_response = self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
                request, stream=False, **kwargs
            )
            return pipeline_response

        def _extract_data(pipeline_response):
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(
                    status_code=response.status_code,
                    response=response,
                    error_map=error_map,
                )
                raise HttpResponseError(response=response)
            return _extract_data_default(pipeline_response)

        return ItemPaged(get_next=get_next, extract_data=_extract_data)


class EnrollmentGroupOperations(EnrollmentGroupOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.iot.deviceprovisioning.DeviceProvisioningClient`'s
        :attr:`enrollment_group` attribute.
    """

    @distributed_trace
    def query(  # type: ignore[override]
        self,
        query_specification: Union[JSON, IO],
        *,
        top: Optional[int] = None,
        **kwargs: Any,
    ) -> ItemPaged[JSON]:
        """Query the device enrollment groups.

        Query the device enrollment groups.

        :param query_specification: The query specification. Is either a JSON type or a IO type.
         Required.
        :type query_specification: JSON or IO
        :keyword top: Page size. Default value is None.
        :paramtype top: Optional[int]
        :return: list of JSON object
        :rtype: ~azure.core.paging.ItemPaged[JSON]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                query_specification = {
                    "query": "str"  # Required.
                }

                # response body for status code(s): 200
                response == [
                    {
                        "attestation": {
                            "type": "str",  # Attestation Type. Required. Known values
                              are: "none", "tpm", "x509", and "symmetricKey".
                            "symmetricKey": {
                                "primaryKey": "str",  # Optional. Primary symmetric
                                  key.
                                "secondaryKey": "str"  # Optional. Secondary
                                  symmetric key.
                            },
                            "tpm": {
                                "endorsementKey": "str",  # Required.
                                "storageRootKey": "str"  # Optional. TPM attestation
                                  method.
                            },
                            "x509": {
                                "caReferences": {
                                    "primary": "str",  # Optional. Primary and
                                      secondary CA references.
                                    "secondary": "str"  # Optional. Primary and
                                      secondary CA references.
                                },
                                "clientCertificates": {
                                    "primary": {
                                        "certificate": "str",  # Optional.
                                          Certificate and Certificate info.
                                        "info": {
                                            "issuerName": "str",  #
                                              Required.
                                            "notAfterUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "notBeforeUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "serialNumber": "str",  #
                                              Required.
                                            "sha1Thumbprint": "str",  #
                                              Required.
                                            "sha256Thumbprint": "str",  #
                                              Required.
                                            "subjectName": "str",  #
                                              Required.
                                            "version": 0  # Required.
                                        }
                                    },
                                    "secondary": {
                                        "certificate": "str",  # Optional.
                                          Certificate and Certificate info.
                                        "info": {
                                            "issuerName": "str",  #
                                              Required.
                                            "notAfterUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "notBeforeUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "serialNumber": "str",  #
                                              Required.
                                            "sha1Thumbprint": "str",  #
                                              Required.
                                            "sha256Thumbprint": "str",  #
                                              Required.
                                            "subjectName": "str",  #
                                              Required.
                                            "version": 0  # Required.
                                        }
                                    }
                                },
                                "signingCertificates": {
                                    "primary": {
                                        "certificate": "str",  # Optional.
                                          Certificate and Certificate info.
                                        "info": {
                                            "issuerName": "str",  #
                                              Required.
                                            "notAfterUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "notBeforeUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "serialNumber": "str",  #
                                              Required.
                                            "sha1Thumbprint": "str",  #
                                              Required.
                                            "sha256Thumbprint": "str",  #
                                              Required.
                                            "subjectName": "str",  #
                                              Required.
                                            "version": 0  # Required.
                                        }
                                    },
                                    "secondary": {
                                        "certificate": "str",  # Optional.
                                          Certificate and Certificate info.
                                        "info": {
                                            "issuerName": "str",  #
                                              Required.
                                            "notAfterUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "notBeforeUtc": "2020-02-20
                                              00:00:00",  # Required.
                                            "serialNumber": "str",  #
                                              Required.
                                            "sha1Thumbprint": "str",  #
                                              Required.
                                            "sha256Thumbprint": "str",  #
                                              Required.
                                            "subjectName": "str",  #
                                              Required.
                                            "version": 0  # Required.
                                        }
                                    }
                                }
                            }
                        },
                        "enrollmentGroupId": "str",  # Enrollment Group ID. Required.
                        "allocationPolicy": "str",  # Optional. The allocation policy of this
                          resource. This policy overrides the tenant level allocation policy for this
                          individual enrollment or enrollment group. Possible values include 'hashed':
                          Linked IoT hubs are equally likely to have devices provisioned to them,
                          'geoLatency':  Devices are provisioned to an IoT hub with the lowest latency
                          to the device.If multiple linked IoT hubs would provide the same lowest
                          latency, the provisioning service hashes devices across those hubs, 'static'
                          : Specification of the desired IoT hub in the enrollment list takes priority
                          over the service-level allocation policy, 'custom': Devices are provisioned
                          to an IoT hub based on your own custom logic. The provisioning service passes
                          information about the device to the logic, and the logic returns the desired
                          IoT hub as well as the desired initial configuration. We recommend using
                          Azure Functions to host your logic. Known values are: "hashed", "geoLatency",
                          "static", and "custom".
                        "capabilities": {
                            "iotEdge": False  # Default value is False. If set to true,
                              this device is an IoTEdge device. Required.
                        },
                        "createdDateTimeUtc": "2020-02-20 00:00:00",  # Optional. The
                          DateTime this resource was created.
                        "customAllocationDefinition": {
                            "apiVersion": "str",  # The API version of the provisioning
                              service types (such as Enrollment) sent in the custom
                              allocation request. Minimum supported version: "2018-09-01-preview".
                              Required.
                            "webhookUrl": "str"  # The webhook URL used for allocation
                              requests. Required.
                        },
                        "etag": "str",  # Optional. The entity tag associated with the
                          resource.
                        "initialTwin": {
                            "properties": {
                                "desired": {
                                    "count": 0,  # Optional. Number of properties
                                      in the TwinCollection.
                                    "metadata": {
                                        "lastUpdated": "2020-02-20 00:00:00",
                                          # Optional. Last time the TwinCollection was updated.
                                        "lastUpdatedVersion": 0  # Optional.
                                          This is null for reported properties metadata and is not null
                                          for desired properties metadata.
                                    },
                                    "version": 0  # Optional. Version of the
                                      TwinCollection.
                                }
                            },
                            "tags": {
                                "count": 0,  # Optional. Number of properties in the
                                  TwinCollection.
                                "metadata": {
                                    "lastUpdated": "2020-02-20 00:00:00",  #
                                      Optional. Last time the TwinCollection was updated.
                                    "lastUpdatedVersion": 0  # Optional. This is
                                      null for reported properties metadata and is not null for desired
                                      properties metadata.
                                },
                                "version": 0  # Optional. Version of the
                                  TwinCollection.
                            }
                        },
                        "iotHubHostName": "str",  # Optional. The Iot Hub host name.
                        "iotHubs": [
                            "str"  # Optional. The list of IoT Hub hostnames the
                              device(s) in this resource can be allocated to. Must be a subset of
                              tenant level list of IoT hubs.
                        ],
                        "lastUpdatedDateTimeUtc": "2020-02-20 00:00:00",  # Optional. The
                          DateTime this resource was last updated.
                        "provisioningStatus": "enabled",  # Optional. Default value is
                          "enabled". The provisioning status. Known values are: "enabled" and
                          "disabled".
                        "reprovisionPolicy": {
                            "migrateDeviceData": True,  # Default value is True. When set
                              to true (default), the Device Provisioning Service will migrate the
                              device's data (twin, device capabilities, and device ID) from one IoT hub
                              to another during an IoT hub assignment update. If set to false, the
                              Device Provisioning Service will reset the device's data to the initial
                              desired configuration stored in the corresponding enrollment list.
                            "updateHubAssignment": True  # Default value is True. When
                              set to true (default), the Device Provisioning Service will evaluate the
                              device's IoT Hub assignment and update it if necessary for any
                              provisioning requests beyond the first from a given device. If set to
                              false, the device will stay assigned to its current IoT hub.
                        }
                    }
                ]
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))

        content_type = content_type or "application/json"
        _json = None
        _content = None
        if isinstance(query_specification, (IOBase, bytes)):
            _content = query_specification
        else:
            _json = query_specification

        def prepare_request(continuation_token=None):
            if not continuation_token:
                request = build_enrollment_group_query_request(
                    x_ms_max_item_count=top,
                    content_type=content_type,
                    api_version=self._config.api_version,
                    json=_json,
                    content=_content,
                    headers=_headers,
                    params=_params,
                    **kwargs,
                )
            else:
                request = build_enrollment_group_query_request(
                    x_ms_max_item_count=top,
                    x_ms_continuation=continuation_token,
                    content_type=content_type,
                    api_version=self._config.api_version,
                    json=_json,
                    content=_content,
                    headers=_headers,
                    params=_params,
                    **kwargs,
                )
            request.url = self._client.format_url(request.url)
            return request

        def get_next(continuation_token: Optional[str] = None):
            request = prepare_request(continuation_token)
            pipeline_response = self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
                request, stream=False, **kwargs
            )
            return pipeline_response

        def _extract_data(pipeline_response):
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(
                    status_code=response.status_code,
                    response=response,
                    error_map=error_map,
                )
                raise HttpResponseError(response=response)
            return _extract_data_default(pipeline_response)

        return ItemPaged(get_next=get_next, extract_data=_extract_data)


class DeviceRegistrationStateOperations(DeviceRegistrationStateOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.iot.deviceprovisioning.DeviceProvisioningClient`'s
        :attr:`device_registration_state` attribute.
    """

    @distributed_trace
    def query(  # type: ignore[override]
        self,
        id: str,
        *,
        top: Optional[int] = None,
        **kwargs: Any,
    ) -> ItemPaged[JSON]:
        """Gets the registration state of devices in this enrollmentGroup.

        Gets the registration state of devices in this enrollmentGroup.

        :param id: Enrollment group ID. Required.
        :type id: str
        :keyword top: Page size. Default value is None.
        :paramtype top: Optional[int]
        :return: list of JSON object
        :rtype: ~azure.core.paging.ItemPaged[JSON]
        :raises ~azure.core.exceptions.HttpResponseError

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    {
                        "assignedHub": "str",  # Optional. Assigned Azure IoT Hub.
                        "createdDateTimeUtc": "2020-02-20 00:00:00",  # Optional.
                          Registration create date time (in UTC).
                        "deviceId": "str",  # Optional. Device ID.
                        "errorCode": 0,  # Optional. Error code.
                        "errorMessage": "str",  # Optional. Error message.
                        "etag": "str",  # Optional. The entity tag associated with the
                          resource.
                        "lastUpdatedDateTimeUtc": "2020-02-20 00:00:00",  # Optional. Last
                          updated date time (in UTC).
                        "payload": {},  # Optional. Custom allocation payload returned from
                          the webhook to the device.
                        "registrationId": "str",  # Optional. This id is used to uniquely
                          identify a device registration of an enrollment."nA case-insensitive string
                          (up to 128 characters long) of alphanumeric characters plus certain special
                          characters : . _ -. No special characters allowed at start or end.
                        "status": "str",  # Optional. Enrollment status. Known values are:
                          "unassigned", "assigning", "assigned", "failed", and "disabled".
                        "substatus": "str"  # Optional. Substatus for 'Assigned' devices.
                          Possible values include - 'initialAssignment': Device has been assigned to an
                          IoT hub for the first time, 'deviceDataMigrated': Device has been assigned to
                          a different IoT hub and its device data was migrated from the previously
                          assigned IoT hub. Device data was removed from the previously assigned IoT
                          hub, 'deviceDataReset':  Device has been assigned to a different IoT hub and
                          its device data was populated from the initial state stored in the
                          enrollment. Device data was removed from the previously assigned IoT hub,
                          'reprovisionedToInitialAssignment': Device has been re-provisioned to a
                          previously assigned IoT hub. Known values are: "initialAssignment",
                          "deviceDataMigrated", "deviceDataReset", and
                          "reprovisionedToInitialAssignment".
                    }
                ]
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        def prepare_request(continuation_token=None):
            if not continuation_token:
                request = build_device_registration_state_query_request(
                    id=id,
                    x_ms_max_item_count=top,
                    api_version=self._config.api_version,
                    headers=_headers,
                    params=_params,
                    **kwargs,
                )
            else:
                request = build_device_registration_state_query_request(
                    id=id,
                    x_ms_max_item_count=top,
                    x_ms_continuation=continuation_token,
                    api_version=self._config.api_version,
                    headers=_headers,
                    params=_params,
                    **kwargs,
                )
            request.url = self._client.format_url(request.url)
            return request

        def get_next(continuation_token: Optional[str] = None):
            request = prepare_request(continuation_token)
            pipeline_response = self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
                request, stream=False, **kwargs
            )
            return pipeline_response

        def _extract_data(pipeline_response):
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(
                    status_code=response.status_code,
                    response=response,
                    error_map=error_map,
                )
                raise HttpResponseError(response=response)
            return _extract_data_default(pipeline_response)

        return ItemPaged(get_next=get_next, extract_data=_extract_data)


__all__ = [
    "EnrollmentOperations",
    "EnrollmentGroupOperations",
    "DeviceRegistrationStateOperations",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
