# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import List, Union

from marshmallow import Schema

from ..._schema import PathAwareSchema
from .._schema.component import NodeType
from ..entities.node import InternalBaseNode


class Scope(InternalBaseNode):
    """Node of scope components in pipeline with specific run settings."""

    def __init__(self, **kwargs):
        kwargs.pop("type", None)
        super(Scope, self).__init__(type=NodeType.SCOPE, **kwargs)
        self._init = True
        self._adla_account_name = kwargs.pop("adla_account_name", None)
        self._scope_param = kwargs.pop("scope_param", None)
        self._custom_job_name_suffix = kwargs.pop("custom_job_name_suffix", None)
        self._priority = kwargs.pop("priority", None)
        self._auto_token = kwargs.pop("auto_token", None)
        self._tokens = kwargs.pop("tokens", None)
        self._vcp = kwargs.pop("vcp", None)
        self._init = False

    @property
    def adla_account_name(self) -> str:
        """The ADLA account name to use for the scope job.

        :return: ADLA account name
        :rtype: str
        """
        return self._adla_account_name

    @adla_account_name.setter
    def adla_account_name(self, value: str):
        self._adla_account_name = value

    @property
    def scope_param(self) -> str:
        """nebula command used when submit the scope job.

        :return: The nebula command
        :rtype: str
        """
        return self._scope_param

    @scope_param.setter
    def scope_param(self, value: str):
        self._scope_param = value

    @property
    def custom_job_name_suffix(self) -> str:
        """Optional string to append to scope job name.

        :return: The custom suffix
        :rtype: str
        """
        return self._custom_job_name_suffix

    @custom_job_name_suffix.setter
    def custom_job_name_suffix(self, value: str):
        self._custom_job_name_suffix = value

    @property
    def priority(self) -> int:
        """scope job priority.

        If set priority in scope_param, will override this setting.

        :return: The job priority
        :rtype: int
        """
        return self._priority

    @priority.setter
    def priority(self, value: int):
        self._priority = value

    @property
    def auto_token(self) -> int:
        """A predictor for estimating the peak resource usage of scope job.

        :return: auto token
        :rtype: int
        """
        return self._auto_token

    @auto_token.setter
    def auto_token(self, value: int):
        self._auto_token = value

    @property
    def tokens(self) -> int:
        """Standard token allocation.

        :return: The token allocation
        :rtype: int
        """
        return self._tokens

    @tokens.setter
    def tokens(self, value: int):
        self._tokens = value

    @property
    def vcp(self) -> float:
        """Standard VC percent allocation; should be a float between 0 and 1.

        :return: The VC allocation
        :rtype: float
        """
        return self._vcp

    @vcp.setter
    def vcp(self, value: float):
        self._vcp = value

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["custom_job_name_suffix", "scope_param", "adla_account_name", "priority", "auto_token", "tokens", "vcp"]

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from .._schema.node import ScopeSchema

        return ScopeSchema(context=context)
