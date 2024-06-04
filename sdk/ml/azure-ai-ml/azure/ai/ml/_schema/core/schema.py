# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import copy
import logging
from pathlib import Path
from typing import Optional

from marshmallow import fields, post_load, pre_load
from pydash import objects

from azure.ai.ml._schema.core.schema_meta import PatchedBaseSchema, PatchedSchemaMeta
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, FILE_PREFIX, PARAMS_OVERRIDE_KEY
from azure.ai.ml.exceptions import MlException

module_logger = logging.getLogger(__name__)


class PathAwareSchema(PatchedBaseSchema, metaclass=PatchedSchemaMeta):
    schema_ignored = fields.Str(data_key="$schema", dump_only=True)

    def __init__(self, *args, **kwargs):
        # this will make context of all PathAwareSchema child class point to one object
        self.context = kwargs.get("context", None)
        if self.context is None or self.context.get(BASE_PATH_CONTEXT_KEY, None) is None:
            msg = "Base path for reading files is required when building PathAwareSchema"
            raise MlException(message=msg, no_personal_data_message=msg)
        # set old base path, note it's an Path object and point to the same object with
        # self.context.get(BASE_PATH_CONTEXT_KEY)
        self.old_base_path = self.context.get(BASE_PATH_CONTEXT_KEY)
        super().__init__(*args, **kwargs)

    @pre_load
    def add_param_overrides(self, data, **kwargs):
        # Removing params override from context so that overriding is done once on the yaml
        # child schema should not override the params.
        params_override = self.context.pop(PARAMS_OVERRIDE_KEY, None)
        if params_override is not None:
            for override in params_override:
                for param, val in override.items():
                    # Check that none of the intermediary levels are string references (azureml/file)
                    param_tokens = param.split(".")
                    test_layer = data
                    for layer in param_tokens:
                        if test_layer is None:
                            continue
                        if isinstance(test_layer, str):
                            msg = f"Cannot use '--set' on properties defined by reference strings: --set {param}"
                            raise MlException(
                                message=msg,
                                no_personal_data_message=msg,
                            )
                        test_layer = test_layer.get(layer, None)
                    objects.set_(data, param, val)
        return data

    @pre_load
    # pylint: disable-next=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
    def trim_dump_only(self, data, **kwargs):
        """Marshmallow raises if dump_only fields are present in the schema. This is not desirable for our use case,
        where read-only properties can be present in the yaml, and should simply be ignored, while we should raise in.

        the case an unknown field is present - to prevent typos.
        """
        if isinstance(data, str) or data is None:
            return data
        for key, value in self.fields.items():  # pylint: disable=no-member
            if value.dump_only:
                schema_key = value.data_key or key
                if data.get(schema_key, None) is not None:
                    data.pop(schema_key)
        return data


class YamlFileSchema(PathAwareSchema):
    """Base class that allows derived classes to be built from paths to separate yaml files in place of inline yaml
    definitions.

    This will be transparent to any parent schema containing a nested schema of the derived class, it will not need a
    union type for the schema, a YamlFile string will be resolved by the pre_load method into a dictionary. On loading
    the child yaml, update the base path to use for loading sub-child files.
    """

    def __init__(self, *args, **kwargs):
        self._previous_base_path = None
        super().__init__(*args, **kwargs)

    @classmethod
    def _resolve_path(cls, data, base_path) -> Optional[Path]:
        if isinstance(data, str) and data.startswith(FILE_PREFIX):
            # Use directly if absolute path
            path = Path(data[len(FILE_PREFIX) :])
            if not path.is_absolute():
                path = Path(base_path) / path
                path.resolve()
            return path
        return None

    @pre_load
    def load_from_file(self, data, **kwargs):
        path = self._resolve_path(data, Path(self.context[BASE_PATH_CONTEXT_KEY]))
        if path is not None:
            self._previous_base_path = Path(self.context[BASE_PATH_CONTEXT_KEY])
            # Push update
            # deepcopy self.context[BASE_PATH_CONTEXT_KEY] to update old base path
            self.old_base_path = copy.deepcopy(self.context[BASE_PATH_CONTEXT_KEY])
            self.context[BASE_PATH_CONTEXT_KEY] = path.parent

            data = load_yaml(path)
            return data
        return data

    # Schemas are read depth-first, so push/pop to update current path
    @post_load
    def reset_base_path_post_load(self, data, **kwargs):
        if self._previous_base_path is not None:
            # pop state
            self.context[BASE_PATH_CONTEXT_KEY] = self._previous_base_path
        return data
