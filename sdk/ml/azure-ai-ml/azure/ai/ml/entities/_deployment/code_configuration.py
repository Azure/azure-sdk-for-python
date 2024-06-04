# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
from typing import Optional, Union

from azure.ai.ml._restclient.v2022_05_01.models import CodeConfiguration as RestCodeConfiguration
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._mixins import DictMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

module_logger = logging.getLogger(__name__)


class CodeConfiguration(DictMixin):
    """Code configuration for a scoring job.

    :param code: The code directory containing the scoring script. The code can be an Code object, an ARM resource ID
        of an existing code asset, a local path, or "http:", "https:", or "azureml:" url pointing to a remote location.
    :type code: Optional[Union[~azure.ai.ml.entities.Code, str]]
    :param scoring_script: The scoring script file path relative to the code directory.
    :type scoring_script: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START code_configuration]
            :end-before: [END code_configuration]
            :language: python
            :dedent: 8
            :caption: Creating a CodeConfiguration for a BatchDeployment.
    """

    def __init__(
        self,
        code: Optional[Union[str, os.PathLike]] = None,
        scoring_script: Optional[Union[str, os.PathLike]] = None,
    ) -> None:
        self.code: Optional[Union[str, os.PathLike]] = code
        self._scoring_script: Optional[Union[str, os.PathLike]] = scoring_script

    @property
    def scoring_script(self) -> Optional[Union[str, os.PathLike]]:
        """The scoring script file path relative to the code directory.

        :rtype: str
        """
        return self._scoring_script

    def _to_rest_code_configuration(self) -> RestCodeConfiguration:
        return RestCodeConfiguration(code_id=self.code, scoring_script=self.scoring_script)

    def _validate(self) -> None:
        if self.code and not self.scoring_script:
            msg = "scoring script can't be empty"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.CODE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

    @staticmethod
    def _from_rest_code_configuration(code_configuration: RestCodeConfiguration) -> Optional["CodeConfiguration"]:
        if code_configuration:
            return CodeConfiguration(
                code=code_configuration.code_id,
                scoring_script=code_configuration.scoring_script,
            )
        return None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CodeConfiguration):
            return NotImplemented
        if not other:
            return False
        # only compare mutable fields
        return (
            self.scoring_script == other.scoring_script
            and (
                isinstance(self.code, Code)
                and isinstance(other.code, Code)
                or isinstance(self.code, str)
                and isinstance(other.code, str)
            )
            and self.code == other.code
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
