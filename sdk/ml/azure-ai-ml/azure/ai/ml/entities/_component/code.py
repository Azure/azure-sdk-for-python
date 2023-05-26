# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from abc import abstractmethod
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

from azure.ai.ml._utils._arm_id_utils import is_ARM_id_for_resource, is_registry_id_for_resource
from azure.ai.ml._utils._asset_utils import IgnoreFile, get_ignore_file
from azure.ai.ml._utils.utils import is_private_preview_enabled
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._validation import MutableValidationResult, _ValidationResultBuilder


class ComponentIgnoreFile(IgnoreFile):
    _COMPONENT_CODE_IGNORES = ["__pycache__"]

    def __init__(
        self,
        directory_path: Union[str, Path],
        *,
        additional_includes_file_name: Optional[str] = None,
        skip_ignore_file: bool = False,
        extra_ignore_list: Optional[List[IgnoreFile]] = None,
    ):
        self._base_path = Path(directory_path)
        self._extra_ignore_list: List[IgnoreFile] = extra_ignore_list or []
        # only the additional include file in root directory is ignored
        # additional include files in subdirectories are not processed so keep them
        self._additional_includes_file_name = additional_includes_file_name
        # note: the parameter changes to directory path in this class, rather than file path
        file_path = None if skip_ignore_file else get_ignore_file(directory_path).path
        super(ComponentIgnoreFile, self).__init__(file_path=file_path)

    def exists(self) -> bool:
        """Override to always return True as we do have default ignores."""
        return True

    @property
    def base_path(self) -> Path:
        # for component ignore file, the base path can be different from file.parent
        return self._base_path

    def rebase(self, directory_path: Union[str, Path]) -> "ComponentIgnoreFile":
        """Rebase the ignore file to a new directory."""
        self._base_path = directory_path
        return self

    def is_file_excluded(self, file_path: Union[str, Path]) -> bool:
        """Override to add custom ignores for internal component."""
        if self._additional_includes_file_name and self._get_rel_path(file_path) == self._additional_includes_file_name:
            return True
        for ignore_file in self._extra_ignore_list:
            if ignore_file.is_file_excluded(file_path):
                return True
        return super(ComponentIgnoreFile, self).is_file_excluded(file_path)

    def merge(self, other_path: Path) -> "ComponentIgnoreFile":
        """Merge ignore list from another ComponentIgnoreFile object."""
        if other_path.is_file():
            return self
        return ComponentIgnoreFile(other_path, extra_ignore_list=self._extra_ignore_list + [self])

    def _get_ignore_list(self) -> List[str]:
        """Override to add custom ignores."""
        if not super(ComponentIgnoreFile, self).exists():
            return self._COMPONENT_CODE_IGNORES
        return super(ComponentIgnoreFile, self)._get_ignore_list() + self._COMPONENT_CODE_IGNORES


class CodeType(Enum):
    """Code type."""

    LOCAL = "local"
    NONE = "none"
    GIT = "git"
    ARM_ID = "arm_id"
    UNKNOWN = "unknown"


class ComponentCodeMixin:
    @abstractmethod
    def _get_base_path_for_code(self) -> Path:
        """Get base path for additional includes."""

    @abstractmethod
    def _get_origin_code_value(self) -> Union[str, os.PathLike, None]:
        """Get origin code path.
        Origin code path is either an absolute path or a relative path to base path.
        Additional includes are only supported for component types with code attribute. Origin code path will be copied
        to a temp folder along with additional includes to form a new code content.
        """

    def _get_code_type(self) -> CodeType:
        origin_code_value = self._get_origin_code_value()
        if origin_code_value is None:
            return CodeType.NONE
        if not isinstance(origin_code_value, str):
            # note that:
            # 1. Code & CodeOperation are not public for now
            # 2. AnonymousCodeSchema is not within CodeField
            # 3. Code will be returned as an arm id as an attribute of a component when getting a component from remote
            # So origin_code_value should never be a Code object, or an exception will be raised
            # in validation stage.
            return CodeType.UNKNOWN
        if is_ARM_id_for_resource(origin_code_value, AzureMLResourceType.CODE) or is_registry_id_for_resource(
            origin_code_value
        ):
            return CodeType.ARM_ID
        if origin_code_value.startswith("git+"):
            return CodeType.GIT
        return CodeType.LOCAL

    def _validate_code(self) -> MutableValidationResult:
        validation_result = _ValidationResultBuilder.success()
        # If private features are enable and component has code value of type str we need to check
        # that it is a valid git path case. Otherwise, we should throw a ValidationError
        # saying that the code value is not valid
        # pylint: disable=no-member
        if self._get_code_type() == CodeType.GIT and not is_private_preview_enabled():
            validation_result.append_error(
                message="Not a valid code value: git paths are not supported.",
            )
        return validation_result

    def _with_local_code(self) -> bool:
        """Whether the component has local code.

        Leave this method to avoid expose _CodeType.
        """
        return self._get_code_type() == CodeType.LOCAL

    @contextmanager
    def _build_code(self) -> Optional[Code]:
        """Create a Code object if necessary based on origin code value and yield it.

        If built code is the same as its origin value, do nothing and yield None.
        Otherwise, yield a Code object pointing to the code.
        """
        origin_code_value = self._get_origin_code_value()
        code_type = self._get_code_type()

        if code_type == CodeType.GIT:
            # git also need to be resolved into arm id
            yield Code(path=origin_code_value)
        elif code_type == CodeType.LOCAL:
            yield Code(
                base_path=self._get_base_path_for_code(),
                path=origin_code_value,
                ignore_file=ComponentIgnoreFile(origin_code_value),
            )
        else:
            # arm id, None and unknown need no extra resolution
            yield None
