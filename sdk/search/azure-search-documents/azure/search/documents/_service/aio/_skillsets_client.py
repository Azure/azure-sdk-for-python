# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core.tracing.decorator_async import distributed_trace_async

from .._generated.aio import SearchServiceClient as _SearchServiceClient
from .._generated.models import Skillset
from ..._headers_mixin import HeadersMixin
from ..._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from .._generated.models import Skill
    from typing import Any, List, Sequence
    from azure.core.credentials import AzureKeyCredential


class SearchSkillsetsClient(HeadersMixin):
    """A client to interact with Azure search service Skillsets.

    This class is not normally instantiated directly, instead use
    `get_skillsets_client()` from a `SearchServiceClient`

    """

    _ODATA_ACCEPT = "application/json;odata.metadata=minimal"  # type: str

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, AzureKeyCredential, **Any) -> None

        self._endpoint = endpoint  # type: str
        self._credential = credential  # type: AzureKeyCredential
        self._client = _SearchServiceClient(
            endpoint=endpoint, sdk_moniker=SDK_MONIKER, **kwargs
        )  # type: _SearchServiceClient

    async def __aenter__(self):
        # type: () -> SearchSkillsetsClient
        await self._client.__aenter__()  # pylint:disable=no-member
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        return await self._client.__aexit__(*args)  # pylint:disable=no-member

    async def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.DataSourcesClient` session.

        """
        return await self._client.close()

    @distributed_trace_async
    async def get_skillsets(self, **kwargs):
        # type: (**Any) -> List[Skillset]
        """List the Skillsets in an Azure Search service.

        :return: List of Skillsets
        :rtype: list[dict]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_skillset_operations_async.py
                :start-after: [START get_skillsets]
                :end-before: [END get_skillsets]
                :language: python
                :dedent: 4
                :caption: List Skillsets

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.skillsets.list(**kwargs)
        return result.skillsets

    @distributed_trace_async
    async def get_skillset(self, name, **kwargs):
        # type: (str, **Any) -> Skillset
        """Retrieve a named Skillset in an Azure Search service

        :param name: The name of the Skillset to get
        :type name: str
        :return: The retrieved Skillset
        :rtype: dict
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_skillset_operations_async.py
                :start-after: [START get_skillset]
                :end-before: [END get_skillset]
                :language: python
                :dedent: 4
                :caption: Get a Skillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        return await self._client.skillsets.get(name, **kwargs)

    @distributed_trace_async
    async def delete_skillset(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Delete a named Skillset in an Azure Search service

        :param name: The name of the Skillset to delete
        :type name: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_skillset_operations_async.py
                :start-after: [START delete_skillset]
                :end-before: [END delete_skillset]
                :language: python
                :dedent: 4
                :caption: Delete a Skillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        await self._client.skillsets.delete(name, **kwargs)

    @distributed_trace_async
    async def create_skillset(self, name, skills, description, **kwargs):
        # type: (str, Sequence[Skill], str, **Any) -> Skillset
        """Create a new Skillset in an Azure Search service

        :param name: The name of the Skillset to create
        :type name: str
        :param skills: A list of Skill objects to include in the Skillset
        :type skills: List[Skill]]
        :param description: A description for the Skillset
        :type description: Optional[str]
        :return: The created Skillset
        :rtype: dict

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_skillset_operations_async.py
                :start-after: [START create_skillset]
                :end-before: [END create_skillset]
                :language: python
                :dedent: 4
                :caption: Create a Skillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))

        skillset = Skillset(name=name, skills=list(skills), description=description)

        return await self._client.skillsets.create(skillset, **kwargs)

    @distributed_trace_async
    async def create_or_update_skillset(self, name, **kwargs):
        # type: (str, **Any) -> Skillset
        """Create a new Skillset in an Azure Search service, or update an
        existing one.

        :param name: The name of the Skillset to create or update
        :type name: str
        :param skills: A list of Skill objects to include in the Skillset
        :type skills: List[Skill]
        :param description: A description for the Skillset
        :type description: Optional[str]
        :param skillset: A Skillset to create or update.
        :type skillset: :class:`~azure.search.documents.Skillset`
        :return: The created or updated Skillset
        :rtype: dict

        If a `skillset` is passed in, any optional `skills`, or
        `description` parameter values will override it.


        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))

        if "skillset" in kwargs:
            skillset = kwargs.pop("skillset")
            skillset = Skillset.deserialize(skillset.serialize())
            skillset.name = name
            for param in ("description", "skills"):
                if param in kwargs:
                    setattr(skillset, param, kwargs.pop(param))
        else:

            skillset = Skillset(
                name=name,
                description=kwargs.pop("description", None),
                skills=kwargs.pop("skills", None),
            )

        return await self._client.skillsets.create_or_update(name, skillset, **kwargs)
