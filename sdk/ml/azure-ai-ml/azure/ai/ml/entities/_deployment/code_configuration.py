# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2021_10_01.models import CodeConfiguration as RestCodeConfiguration
from azure.ai.ml.entities._assets import Code

module_logger = logging.getLogger(__name__)


class CodeConfiguration:
    """CodeConfiguration.

    :param code: Code entity, defaults to None
    :type code: Union[Code, str, None], optional
    :param scoring_script: defaults to None
    :type scoring_script: str, optional
    """

    def __init__(
        self,
        code: str = None,
        scoring_script: str = None,
    ):
        self.code = code
        self._scoring_script = scoring_script

    @property
    def scoring_script(self) -> str:
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
            )

    @staticmethod
    def _from_rest_code_configuration(code_configuration: RestCodeConfiguration):
        if code_configuration:
            return CodeConfiguration(
                code=code_configuration.code_id,
                scoring_script=code_configuration.scoring_script,
            )

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
