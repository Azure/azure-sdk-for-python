# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core import MatchConditions
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError

from ._generated import SearchServiceClient as _SearchServiceClient
from ._generated.models import Skillset
from ._utils import get_access_conditions
from .._headers_mixin import HeadersMixin
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from ._generated.models import Skill
    from typing import Any, List, Sequence, Union
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

    def __enter__(self):
        # type: () -> SearchSkillsetsClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        return self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.SearchSkillsetsClient` session.

        """
        return self._client.close()

    @distributed_trace
    def get_skillsets(self, **kwargs):
        # type: (**Any) -> List[Skillset]
        """List the Skillsets in an Azure Search service.

        :return: List of Skillsets
        :rtype: list[dict]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_skillset_operations.py
                :start-after: [START get_skillsets]
                :end-before: [END get_skillsets]
                :language: python
                :dedent: 4
                :caption: List Skillsets

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.skillsets.list(**kwargs)
        return result.skillsets

    @distributed_trace
    def get_skillset(self, name, **kwargs):
        # type: (str, **Any) -> Skillset
        """Retrieve a named Skillset in an Azure Search service

        :param name: The name of the Skillset to get
        :type name: str
        :return: The retrieved Skillset
        :rtype: dict
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_skillset_operations.py
                :start-after: [START get_skillset]
                :end-before: [END get_skillset]
                :language: python
                :dedent: 4
                :caption: Get a Skillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        return self._client.skillsets.get(name, **kwargs)

    @distributed_trace
    def delete_skillset(self, skillset, **kwargs):
        # type: (Union[str, Skillset], **Any) -> None
        """Delete a named Skillset in an Azure Search service. To use access conditions,
        the Skillset model must be provided instead of the name. It is enough to provide
        the name of the skillset to delete unconditionally

        :param name: The Skillset to delete
        :type name: str or ~search.models.Skillset
        :keyword match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_skillset_operations.py
                :start-after: [START delete_skillset]
                :end-before: [END delete_skillset]
                :language: python
                :dedent: 4
                :caption: Delete a Skillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            skillset,
            kwargs.pop('match_condition', MatchConditions.Unconditionally)
        )
        try:
            name = skillset.name
        except AttributeError:
            name = skillset
        self._client.skillsets.delete(name, access_condition=access_condition, error_map=error_map, **kwargs)

    @distributed_trace
    def create_skillset(self, name, skills, description, **kwargs):
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

            .. literalinclude:: ../samples/sample_skillset_operations.py
                :start-after: [START create_skillset]
                :end-before: [END create_skillset]
                :language: python
                :dedent: 4
                :caption: Create a Skillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))

        skillset = Skillset(name=name, skills=list(skills), description=description)

        return self._client.skillsets.create(skillset, **kwargs)

    @distributed_trace
    def create_or_update_skillset(self, name, **kwargs):
        # type: (str, **Any) -> Skillset
        """Create a new Skillset in an Azure Search service, or update an
        existing one. The skillset param must be provided to perform the
        operation with access conditions.

        :param name: The name of the Skillset to create or update
        :type name: str
        :keyword skills: A list of Skill objects to include in the Skillset
        :type skills: List[Skill]
        :keyword description: A description for the Skillset
        :type description: Optional[str]
        :keyword skillset: A Skillset to create or update.
        :type skillset: :class:`~azure.search.documents.Skillset`
        :keyword match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions
        :return: The created or updated Skillset
        :rtype: dict

        If a `skillset` is passed in, any optional `skills`, or
        `description` parameter values will override it.

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError
        }
        access_condition = None

        if "skillset" in kwargs:
            skillset = kwargs.pop("skillset")
            error_map, access_condition = get_access_conditions(
                skillset,
                kwargs.pop('match_condition', MatchConditions.Unconditionally)
            )
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

        return self._client.skillsets.create_or_update(
            skillset_name=name,
            skillset=skillset,
            access_condition=access_condition,
            error_map=error_map,
            **kwargs
        )
