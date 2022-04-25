# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING
from uuid import uuid4
from urllib.parse import urlparse
from email.utils import parsedate_to_datetime, format_datetime

from azure.core.tracing.decorator import distributed_trace

from ._shared.utils import parse_connection_str, get_authentication_policy, get_current_utc_time
from ._shared.user_credential import CommunicationTokenCredential
from ._generated import AzureCommunicationJobRouterService
from ._generated.models import (
    ClassificationPolicy
)
from ._version import SDK_MONIKER
from ._utils import _to_imf_date

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union
    from datetime import datetime
    from azure.core.paging import ItemPaged


class RouterClient(object):  # pylint: disable=client-accepts-api-version-keyword
    """A client to interact with the AzureCommunicationService JobRouter service.

    This client provides operations to create and update jobs, policies and workers.

    :param str endpoint:
        The endpoint of the Azure Communication resource.
    :param CommunicationTokenCredential credential:
        The credentials with which to authenticate
    """

    def __init__(
            self,
            endpoint,  # type: str
            credential,  # type: CommunicationTokenCredential
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        if not credential:
            raise ValueError("credential can not be None")

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint
        self._authentication_policy = get_authentication_policy(endpoint, credential)
        self._client = AzureCommunicationJobRouterService(
            self._endpoint,
            authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(cls, conn_str,  # type: str
                               **kwargs  # type: Any
                               ):  # type: (...) -> RouterClient
        """Create RouterClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of RouterClient.
        :rtype: ~azure.communication.RouterClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

#region ClassificationPolicy

    @distributed_trace
    def create_classification_policy(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> ClassificationPolicy
        """ Creates a new classification policy

        :keyword str name: Friendly name of this policy.

        :keyword str fallback_queue_id: The fallback queue to select if the queue selector doesn't find a match.

        :keyword List[~azure.communication.jobrouter.QueueSelectorAttachment] queue_selectors: The queue selectors to resolve a queue for a given job.

        :keyword ~azure.communication.jobrouter.RouterRule prioritization_rule: The rule to determine a priority score for a given job.

        :keyword List[~azure.communication.jobrouter.WorkerSelectorAttachment] worker_selectors: The worker label selectors to attach to a given job.

        :keyword Union[str, datetime] repeatability_request_id: As described in https://docs.oasis-open.org/odata/repeatable-requests/v1.0/cs01/repeatable-requests-v1.0-cs01.html. If not provided, one will be generated.

        :keyword str repeatability_first_sent: As described in
         https://docs.oasis-open.org/odata/repeatable-requests/v1.0/cs01/repeatable-requests-v1.0-cs01.html.
         Default value is None.
        """
        if not id:
            raise ValueError("id cannot be None.")

        repeatability_request_id = kwargs.pop('repeatability_request_id', None)
        if repeatability_request_id is None:
            repeatability_request_id = str(uuid4())

        repeatability_first_sent = kwargs.pop('repeatability_first_sent')
        if repeatability_first_sent is None:
            repeatability_first_sent = format_datetime(datetime.utcnow(), True)
        else:
            repeatability_first_sent = _to_imf_date(repeatability_first_sent)

        classification_policy = ClassificationPolicy(
            name = kwargs.get("name", None),
            fallback_queue_id = kwargs.get("fallback_queue_id", None),
            queue_selectors = kwargs.get("queue_selectors", None),
            prioritization_rule = kwargs.get("prioritization_rule", None),
            worker_selectors = kwargs.get("worker_selectors", None))

        return self._client.job_router.create_classification_policy(
            classification_policy,
            repeatability_request_id = repeatability_request_id,
            repeatability_first_sent = repeatability_first_sent,
            **kwargs)

    @distributed_trace
    def update_classification_policy(
            self,
            id,  # type: str
            classification_policy,  # type: ClassificationPolicy
            **kwargs  # type: Any
    ):
        # type: (...) -> ClassificationPolicy
        """Updates a classification policy

        :param str id: The id of classification policy.
        :param ~azure.communication.jobrouter.ClassificationPolicy classification_policy: Updated classification policy
        :return ClassificationPolicy
        :rtype ~azure.communication.jobrouter.ClassificationPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not id:
            raise ValueError("id cannot be None.")

        return self._client.job_router.update_classification_policy(
            id,
            classification_policy = classification_policy,
            **kwargs)

    @distributed_trace
    def get_classification_policy(
            self,
            id,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> ClassificationPolicy
        """Retrieves an existing classification policy by Id.

        :param str id: The id of classification policy.
        :return ClassificationPolicy
        :rtype ~azure.communication.jobrouter.ClassificationPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not id:
            raise ValueError("id cannot be None.")

        return self._client.job_router.get_classification_policy(
            id,
            **kwargs)

    @distributed_trace
    def list_classification_policies(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[ClassificationPolicy]
        """Retrieves existing classification policies.

        :keyword int results_per_page: The maximum number of results to be returned per page.
        :return: An iterator like instance of ClassificationPolicy
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.jobrouter.ClassificationPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        results_per_page = kwargs.pop("results_per_page", None)

        return self._client.job_router.list_classification_policies(
            maxpagesize = results_per_page,
            **kwargs)

    def delete_classification_policy(
            self,
            id,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete a classification policy by Id.

        :param str id: The id of classification policy.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if not id:
            raise ValueError("id cannot be None.")

        return self._client.job_router.delete_classification_policy(
            id = id,
            **kwargs)

#endregion ClassificationPolicy

    def close(self):
        # type: () -> None
        self._client.close()

    def __enter__(self):
        # type: () -> RouterClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
