# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Any, Generator, List, Optional, Union

from azure.ai.ml._utils._arm_id_utils import is_ARM_id_for_resource, is_registry_id_for_resource
from azure.ai.ml._utils._asset_utils import IgnoreFile, get_ignore_file
from azure.ai.ml._utils.utils import is_private_preview_enabled
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AzureMLResourceType
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._validation import MutableValidationResult


class ComponentIgnoreFile(IgnoreFile):
    _COMPONENT_CODE_IGNORES = ["__pycache__"]
    """Component-specific ignore file used for ignoring files in a component directory.

    :param directory_path: The directory path for the ignore file.
    :type directory_path: Union[str, Path]
    :param additional_includes_file_name: Name of the additional includes file in the root directory to be ignored.
    :type additional_includes_file_name: str
    :param skip_ignore_file: Whether to skip the ignore file, defaults to False.
    :type skip_ignore_file: bool
    :param extra_ignore_list: List of additional ignore files to be considered during file exclusion.
    :type extra_ignore_list: List[~azure.ai.ml._utils._asset_utils.IgnoreFile]
    :raises ValueError: If additional include file is not found.
    :return: The ComponentIgnoreFile object.
    :rtype: ComponentIgnoreFile
    """

    def __init__(
        self,
        directory_path: Union[str, Path],
        *,
        additional_includes_file_name: Optional[str] = None,
        skip_ignore_file: bool = False,
        extra_ignore_list: Optional[List[IgnoreFile]] = None,
    ):
        self._base_path: Union[str, Path] = Path(directory_path)
        self._extra_ignore_list: List[IgnoreFile] = extra_ignore_list or []
        # only the additional include file in root directory is ignored
        # additional include files in subdirectories are not processed so keep them
        self._additional_includes_file_name = additional_includes_file_name
        # note: the parameter changes to directory path in this class, rather than file path
        file_path = None if skip_ignore_file else get_ignore_file(directory_path).path
        super(ComponentIgnoreFile, self).__init__(file_path=file_path)

    def exists(self) -> bool:
        """Check if the ignore file exists.

        :return: True
        :rtype: bool
        """
        return True

    @property
    def base_path(self) -> Union[str, Path]:
        """Get the base path of the ignore file.

        :return: The base path.
        :rtype: Path
        """
        # for component ignore file, the base path can be different from file.parent
        return self._base_path

    def rebase(self, directory_path: Union[str, Path]) -> "ComponentIgnoreFile":
        """Rebase the ignore file to a new directory.

        :param directory_path: The new directory path.
        :type directory_path: Union[str, Path]
        :return: The rebased ComponentIgnoreFile object.
        :rtype: ComponentIgnoreFile
        """
        self._base_path = directory_path
        return self

    def is_file_excluded(self, file_path: Union[str, Path]) -> bool:
        """Check if a file should be excluded based on the ignore file rules.

        :param file_path: The file path.
        :type file_path: Union[str, Path]
        :return: True if the file should be excluded, False otherwise.
        :rtype: bool
        """
        if self._additional_includes_file_name and self._get_rel_path(file_path) == self._additional_includes_file_name:
            return True
        for ignore_file in self._extra_ignore_list:
            if ignore_file.is_file_excluded(file_path):
                return True
        res: bool = super(ComponentIgnoreFile, self).is_file_excluded(file_path)
        return res

    def merge(self, other_path: Path) -> "ComponentIgnoreFile":
        """Merge the ignore list from another ComponentIgnoreFile object.

        :param other_path: The path of the other ignore file.
        :type other_path: Path
        :return: The merged ComponentIgnoreFile object.
        :rtype: ComponentIgnoreFile
        """
        if other_path.is_file():
            return self
        return ComponentIgnoreFile(other_path, extra_ignore_list=self._extra_ignore_list + [self])

    def _get_ignore_list(self) -> List[str]:
        """Retrieves the list of ignores from ignore file

        Override to add custom ignores.

        :return: The ignore rules
        :rtype: List[str]
        """
        if not super(ComponentIgnoreFile, self).exists():
            return self._COMPONENT_CODE_IGNORES
        res: list = super(ComponentIgnoreFile, self)._get_ignore_list() + self._COMPONENT_CODE_IGNORES
        return res


class CodeType(Enum):
    """Code type."""

    LOCAL = "local"
    NONE = "none"
    GIT = "git"
    ARM_ID = "arm_id"
    UNKNOWN = "unknown"


def _get_code_type(origin_code_value: Optional[str]) -> CodeType:
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


class ComponentCodeMixin:
    """Mixin class for components with local files as part of the component. Those local files will be uploaded to
    blob storage and further referenced as a code asset in arm id. In below docstring, we will refer to those local
    files as "code".

    The major interface of this mixin is self._customized_code_validate and self._build_code.
    self._customized_code_validate will return a validation result indicating whether the code is valid.
    self._build_code will return a temp Code object for server-side code asset creation.
    """

    def _get_base_path_for_code(self) -> Path:
        """Get base path for additional includes.

        :return: The base path
        :rtype: Path
        """
        if hasattr(self, BASE_PATH_CONTEXT_KEY):
            return Path(getattr(self, BASE_PATH_CONTEXT_KEY))
        raise NotImplementedError(
            "Component must have a base_path attribute to use ComponentCodeMixin. "
            "Please set base_path in __init__ or override _get_base_path_for_code."
        )

    @classmethod
    def _get_code_field_name(cls) -> str:
        """Get the field name for code.

        Will be used to get origin code value by default and will be used as field name of validation diagnostics.

        :return: Code field name
        :rtype: str
        """
        return "code"

    def _get_origin_code_value(self) -> Union[str, os.PathLike, None]:
        """Get origin code value.
        Origin code value is either an absolute path or a relative path to base path if it's a local path.
        Additional includes are only supported for component types with code attribute. Origin code path will be copied
        to a temp folder along with additional includes to form a new code content.
        """
        return getattr(self, self._get_code_field_name(), None)

    def _fill_back_code_value(self, value: str) -> None:
        """Fill resolved code value back to the component.

        :param value: resolved code value
        :type value: str
        :return: no return
        :rtype: None
        """
        return setattr(self, self._get_code_field_name(), value)

    def _get_origin_code_in_str(self) -> Optional[str]:
        """Get origin code value in str to simplify following logic."""
        origin_code_value = self._get_origin_code_value()
        if origin_code_value is None:
            return None
        if isinstance(origin_code_value, Path):
            return origin_code_value.as_posix()
        return str(origin_code_value)

    def _append_diagnostics_and_check_if_origin_code_reliable_for_local_path_validation(
        self, base_validation_result: Optional[MutableValidationResult] = None
    ) -> bool:
        """Append diagnostics from customized validation logic to the base validation result and check if origin code
        value is valid for path validation.

        For customized validation logic, this method shouldn't cover the validation logic duplicated with schema
        validation, like local code existence check.
        For the check, as "code" includes file dependencies of a component, other fields may depend on those files.
        However, the origin code value may not be reliable for validation of those fields. For example:
        1. origin code value can be a remote git path or an arm id of a code asset.
        2. some file operations may be done during build_code, which makes final code content different from what we can
        get from origin code value.
        So, we use this function to check if origin code value is reliable for further local path validation.

        :param base_validation_result: base validation result to append diagnostics to.
        :type base_validation_result: MutableValidationResult
        :return: whether origin code value is reliable for further local path validation.
        :rtype: bool
        """
        # If private features are enable and component has code value of type str we need to check
        # that it is a valid git path case. Otherwise, we should throw a ValidationError
        # saying that the code value is not valid
        code_type = _get_code_type(self._get_origin_code_in_str())
        if code_type == CodeType.GIT and not is_private_preview_enabled():
            if base_validation_result is not None:
                base_validation_result.append_error(
                    message="Not a valid code value: git paths are not supported.",
                    yaml_path=self._get_code_field_name(),
                )
        return code_type == CodeType.LOCAL

    @contextmanager
    def _build_code(self) -> Generator:
        """Create a Code object if necessary based on origin code value and yield it.

        :return: If built code is the same as its origin value, do nothing and yield None.
           Otherwise, yield a Code object pointing to the code.
        :rtype: Iterable[Optional[Code]]
        """
        origin_code_value = self._get_origin_code_in_str()
        code_type = _get_code_type(origin_code_value)

        if code_type == CodeType.GIT:
            # git also need to be resolved into arm id
            yield Code(path=origin_code_value)
        elif code_type in [CodeType.LOCAL, CodeType.NONE]:
            code: Any
            with self._try_build_local_code() as code:  # pylint:disable=contextmanager-generator-missing-cleanup
                yield code
        else:
            # arm id, None and unknown need no extra resolution
            yield None

    @contextmanager
    def _try_build_local_code(self) -> Generator:
        """Extract the logic of _build_code for local code for further override.

        :return: The Code object if could be constructed, None otherwise
        :rtype: Iterable[Optional[Code]]
        """
        origin_code_value = self._get_origin_code_in_str()
        if origin_code_value is None:
            yield None
        else:
            base_path = self._get_base_path_for_code()
            absolute_path: Union[str, Path] = (
                origin_code_value if os.path.isabs(origin_code_value) else base_path / origin_code_value
            )

            yield Code(
                base_path=base_path,
                path=origin_code_value,
                ignore_file=ComponentIgnoreFile(absolute_path),
            )

    def _with_local_code(self) -> bool:
        # TODO: remove this method after we have a better way to do this judge in cache_utils
        origin_code_value = self._get_origin_code_in_str()
        code_type = _get_code_type(origin_code_value)
        return code_type == CodeType.LOCAL
