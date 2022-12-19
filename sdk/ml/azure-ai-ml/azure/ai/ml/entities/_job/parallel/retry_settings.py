# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from os import PathLike
from pathlib import Path
from typing import Dict, Optional, Union

from azure.ai.ml._schema.component.retry_settings import RetrySettingsSchema
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin
from azure.ai.ml.entities._util import load_from_dict


class RetrySettings(RestTranslatableMixin, DictMixin):
    """Parallel RetrySettings.

    :param timeout: Timeout in seconds for each invocation of the run() method.
        (optional) This value could be set through PipelineParameter.
    :type timeout: int
    :param max_retries: The number of maximum tries for a failed or timeout mini batch.
        The range is [1, int.max]. This value could be set through PipelineParameter.
        A mini batch with dequeue count greater than this won't be processed again and will be deleted directly.
    :type max_retries: int
    """

    def __init__(
        self,
        *,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        **kwargs,  # pylint: disable=unused-argument
    ):
        self.timeout = timeout
        self.max_retries = max_retries

    def _to_dict(self) -> Dict:
        return RetrySettingsSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)  # pylint: disable=no-member

    @classmethod
    def _load(
        cls,
        path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> "RetrySettings":
        params_override = params_override or []
        data = load_yaml(path)
        return RetrySettings._load_from_dict(data=data, path=path, params_override=params_override)

    @classmethod
    def _load_from_dict(
        cls,
        data: dict,
        path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "RetrySettings":
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(path).parent if path else Path.cwd(),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return load_from_dict(RetrySettingsSchema, data, context, **kwargs)

    @classmethod
    def _from_dict(cls, dct: dict):
        """Convert a dict to an Input object."""
        obj = cls(**dict(dct.items()))
        return obj

    def _to_rest_object(self):
        return self._to_dict()

    @classmethod
    def _from_rest_object(cls, obj):
        return cls._from_dict(obj)
