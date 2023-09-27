# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
import datetime
from typing import Any, Callable, Dict, Iterable, List, Optional, TypeVar
from .. import models as _models
from ._operations import (
    BatchClientOperationsMixin as BatchClientOperationsMixinGenerated,
)

__all__: List[str] = []  # Add all objects you want publicly available to users at this package level

class BatchClientOperationsMixin(BatchClientOperationsMixinGenerated):
    """Customize generated code"""

    def get_node_file(
        self,
        pool_id: str,
        node_id: str,
        file_path: str,
        *,
        time_out: Optional[int] = None,
        ocp_date: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        ocp_range: Optional[str] = None,
        **kwargs: Any
    ) -> bytes:
        """Returns the content of the specified Compute Node file.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node from which you want to delete the file. Required.
        :type node_id: str
        :param file_path: The path to the file or directory that you want to delete. Required.
        :type file_path: str
        :keyword time_out: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out: int
        :keyword ocp_date: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocp_date: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword ocp_range: The byte range to be retrieved. The default is to retrieve the entire file.
         The
         format is bytes=startRange-endRange. Default value is None.
        :paramtype ocp_range: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: bytes
        :rtype: bytes
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        args = [pool_id, node_id, file_path]
        kwargs.update(
            {
                "time_out": time_out,
                "ocp_date": ocp_date,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
                "ocp_range": ocp_range,
            }
        )
        kwargs["stream"] = True
        return super().get_node_file(*args, **kwargs)

    def get_node_file_properties(
        self,
        pool_id: str,
        node_id: str,
        file_path: str,
        *,
        time_out: Optional[int] = None,
        ocp_date: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> HttpResponse:
        """Gets the properties of the specified Compute Node file.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node from which you want to delete the file. Required.
        :type node_id: str
        :param file_path: The path to the file or directory that you want to delete. Required.
        :type file_path: str
        :keyword time_out: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out: int
        :keyword ocp_date: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocp_date: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: HttpResponse
        :rtype: HttpResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        args = [pool_id, node_id, file_path]
        kwargs.update(
            {
                "time_out": time_out,
                "ocp_date": ocp_date,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
            }
        )

        kwargs["cls"] = lambda pipeline_response, json_response, headers: (
            pipeline_response,
            json_response,
            headers,
        )
        get_response = super().get_node_file_properties(*args, **kwargs)

        return get_response[0].http_response

    def get_task_file_properties(
        self,
        job_id: str,
        task_id: str,
        file_path: str,
        *,
        time_out: Optional[int] = None,
        ocp_date: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> HttpResponse:
        """Gets the properties of the specified Task file.

        :param job_id: The ID of the Job that contains the Task. Required.
        :type job_id: str
        :param task_id: The ID of the Task whose file you want to retrieve. Required.
        :type task_id: str
        :param file_path: The path to the Task file that you want to get the content of. Required.
        :type file_path: str
        :keyword time_out: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out: int
        :keyword ocp_date: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocp_date: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: HttpResponse
        :rtype: HttpResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        args = [job_id, task_id, file_path]
        kwargs.update(
            {
                "time_out": time_out,
                "ocp_date": ocp_date,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
            }
        )

        kwargs["cls"] = lambda pipeline_response, json_response, headers: (
            pipeline_response,
            json_response,
            headers,
        )
        get_response = super().get_task_file_properties(*args, **kwargs)

        return get_response[0].http_response

    def get_node_remote_desktop_file(
        self,
        pool_id: str,
        node_id: str,
        *,
        time_out: Optional[int] = None,
        ocp_date: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> bytes:
        """Gets the Remote Desktop Protocol file for the specified Compute Node.

        Before you can access a Compute Node by using the RDP file, you must create a
        user Account on the Compute Node. This API can only be invoked on Pools created
        with a cloud service configuration. For Pools created with a virtual machine
        configuration, see the GetRemoteLoginSettings API.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node for which you want to get the Remote Desktop
         Protocol file. Required.
        :type node_id: str
        :keyword time_out: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out: int
        :keyword ocp_date: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocp_date: ~datetime.datetime
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: bytes
        :rtype: bytes
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        args = [pool_id, node_id]
        kwargs.update({"time_out": time_out, "ocp_date": ocp_date})
        kwargs["stream"] = True
        return super().get_node_remote_desktop_file(*args, **kwargs)

    def get_task_file(
        self,
        job_id: str,
        task_id: str,
        file_path: str,
        *,
        time_out: Optional[int] = None,
        ocp_date: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        ocp_range: Optional[str] = None,
        **kwargs: Any
    ) -> bytes:
        """Returns the content of the specified Task file.

        :param job_id: The ID of the Job that contains the Task. Required.
        :type job_id: str
        :param task_id: The ID of the Task whose file you want to retrieve. Required.
        :type task_id: str
        :param file_path: The path to the Task file that you want to get the content of. Required.
        :type file_path: str
        :keyword time_out: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out: int
        :keyword ocp_date: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocp_date: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword ocp_range: The byte range to be retrieved. The default is to retrieve the entire file.
         The
         format is bytes=startRange-endRange. Default value is None.
        :paramtype ocp_range: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: bytes
        :rtype: bytes
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        args = [job_id, task_id, file_path]
        kwargs.update(
            {
                "time_out": time_out,
                "ocp_date": ocp_date,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
                "ocp_range": ocp_range,
            }
        )
        kwargs["stream"] = True
        return super().get_task_file(*args, **kwargs)



def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
