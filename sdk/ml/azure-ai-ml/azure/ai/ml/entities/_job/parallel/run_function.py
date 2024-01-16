# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Any, Optional, Union

from azure.ai.ml.constants import ParallelTaskType
from azure.ai.ml.entities._assets.environment import Environment

from .parallel_task import ParallelTask


class RunFunction(ParallelTask):
    """Run Function.

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
    :type args: str
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
        self,
        *,
        code: Optional[str] = None,
        entry_script: Optional[str] = None,
        program_arguments: Optional[str] = None,
        model: Optional[str] = None,
        append_row_to: Optional[str] = None,
        environment: Optional[Union[Environment, str]] = None,
        **kwargs: Any,
    ):
        super().__init__(
            code=code,
            entry_script=entry_script,
            program_arguments=program_arguments,
            model=model,
            append_row_to=append_row_to,
            environment=environment,
            type=ParallelTaskType.RUN_FUNCTION,
        )
