# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union

# from azure.ai.ml.entities._deployment.code_configuration import CodeConfiguration
from azure.ai.ml._schema.component.parallel_task import ComponentParallelTaskSchema
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._assets.environment import Environment
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class ParallelTask(RestTranslatableMixin, DictMixin):
    """Parallel task.

    :param type: The type of the parallel task.
        Possible values are 'run_function'and 'model'.
    :type type: str
    :param code: A local or remote path pointing at source code.
    :type code: str
    :param entry_script: User script which will be run in parallel on multiple nodes. This is
        specified as a local file path.
        The entry_script should contain two functions:
        ``init()``: this function should be used for any costly or common preparation for subsequent inferences,
        e.g., deserializing and loading the model into a global object.
        ``run(mini_batch)``: The method to be parallelized. Each invocation will have one mini-batch.
        'mini_batch': Batch inference will invoke run method and pass either a list or a Pandas DataFrame as an
        argument to the method. Each entry in min_batch will be a filepath if input is a FileDataset,
        a Pandas DataFrame if input is a TabularDataset.
        run() method should return a Pandas DataFrame or an array.
        For append_row output_action, these returned elements are appended into the common output file.
        For summary_only, the contents of the elements are ignored. For all output actions,
        each returned output element indicates one successful inference of input element in the input mini-batch.
        Each parallel worker process will call `init` once and then loop over `run` function until all mini-batches
        are processed.
    :type entry_script: str
    :param program_arguments: The arguments of the parallel task.
    :type program_arguments: str
    :param model: The model of the parallel task.
    :type model: str
    :param append_row_to: All values output by run() method invocations will be aggregated into
        one unique file which is created in the output location.
        if it is not set, 'summary_only' would invoked,  which means user script is expected to store the output itself.
    :type append_row_to: str
    :param environment: Environment that training job will run in.
    :type environment: Union[Environment, str]
    """

    def __init__(
        self,  # pylint: disable=unused-argument
        *,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
        code: Optional[str] = None,
        entry_script: Optional[str] = None,
        program_arguments: Optional[str] = None,
        model: Optional[str] = None,
        append_row_to: Optional[str] = None,
        environment: Optional[Union[Environment, str]] = None,
        **kwargs: Any,
    ):
        self.type = type
        self.code = code
        self.entry_script = entry_script
        self.program_arguments = program_arguments
        self.model = model
        self.append_row_to = append_row_to
        self.environment: Any = environment

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = ComponentParallelTaskSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    @classmethod
    def _load(
        cls,  # pylint: disable=unused-argument
        path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "ParallelTask":
        params_override = params_override or []
        data = load_yaml(path)
        return ParallelTask._load_from_dict(data=data, path=path, params_override=params_override)

    @classmethod
    def _load_from_dict(
        cls,
        data: dict,
        path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "ParallelTask":
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(path).parent if path else Path.cwd(),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        res: ParallelTask = load_from_dict(ComponentParallelTaskSchema, data, context, **kwargs)
        return res

    @classmethod
    def _from_dict(cls, dct: dict) -> "ParallelTask":
        obj = cls(**dict(dct.items()))
        return obj

    def _validate(self) -> None:
        if self.type is None:
            msg = "'type' is required for ParallelTask {}."
            raise ValidationException(
                message=msg.format(self.type),
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg.format(""),
                error_category=ErrorCategory.USER_ERROR,
            )
