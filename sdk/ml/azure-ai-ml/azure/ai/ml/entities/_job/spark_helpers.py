# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
import re
from typing import Any

from azure.ai.ml.constants import InputOutputModes
from azure.ai.ml.constants._component import ComponentJobConstants
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.pipeline._io import NodeInput, NodeOutput
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


def _validate_spark_configurations(obj: Any) -> None:
    # skip validation when component of node is from remote
    if hasattr(obj, "component") and isinstance(obj.component, str):
        return
    if obj.dynamic_allocation_enabled in ["True", "true", True]:
        if (
            obj.driver_cores is None
            or obj.driver_memory is None
            or obj.executor_cores is None
            or obj.executor_memory is None
        ):
            msg = (
                "spark.driver.cores, spark.driver.memory, spark.executor.cores and spark.executor.memory are "
                "mandatory fields."
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        if obj.dynamic_allocation_min_executors is None or obj.dynamic_allocation_max_executors is None:
            msg = (
                "spark.dynamicAllocation.minExecutors and spark.dynamicAllocation.maxExecutors are required "
                "when dynamic allocation is enabled."
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        if not (
            obj.dynamic_allocation_min_executors > 0
            and obj.dynamic_allocation_min_executors <= obj.dynamic_allocation_max_executors
        ):
            msg = (
                "Dynamic min executors should be bigger than 0 and min executors should be equal or less than "
                "max executors."
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        if obj.executor_instances and (
            obj.executor_instances > obj.dynamic_allocation_max_executors
            or obj.executor_instances < obj.dynamic_allocation_min_executors
        ):
            msg = (
                "Executor instances must be a valid non-negative integer and must be between "
                "spark.dynamicAllocation.minExecutors and spark.dynamicAllocation.maxExecutors"
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
    else:
        if (
            obj.driver_cores is None
            or obj.driver_memory is None
            or obj.executor_cores is None
            or obj.executor_memory is None
            or obj.executor_instances is None
        ):
            msg = (
                "spark.driver.cores, spark.driver.memory, spark.executor.cores, spark.executor.memory and "
                "spark.executor.instances are mandatory fields."
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        if obj.dynamic_allocation_min_executors is not None or obj.dynamic_allocation_max_executors is not None:
            msg = "Should not specify min or max executors when dynamic allocation is disabled."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )


def _validate_compute_or_resources(compute: Any, resources: Any) -> None:
    # if resources is set, then ensure it is valid before
    # checking mutual exclusiveness against compute existence
    if compute is None and resources is None:
        msg = "One of either compute or resources must be specified for Spark job"
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.SPARK_JOB,
            error_category=ErrorCategory.USER_ERROR,
        )
    if compute and resources:
        msg = "Only one of either compute or resources may be specified for Spark job"
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.SPARK_JOB,
            error_category=ErrorCategory.USER_ERROR,
        )


# Only "direct" mode is supported for spark job inputs and outputs
# pylint: disable=no-else-raise, too-many-boolean-expressions
def _validate_input_output_mode(inputs: Any, outputs: Any) -> None:
    for input_name, input_value in inputs.items():
        if isinstance(input_value, Input) and input_value.mode != InputOutputModes.DIRECT:
            # For standalone job input
            msg = "Input '{}' is using '{}' mode, only '{}' is supported for Spark job"
            raise ValidationException(
                message=msg.format(input_name, input_value.mode, InputOutputModes.DIRECT),
                no_personal_data_message=msg.format("[input_name]", "[input_value.mode]", "direct"),
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        elif (
            isinstance(input_value, NodeInput)
            and (
                isinstance(input_value._data, Input)
                and not (
                    isinstance(input_value._data.path, str)
                    and bool(re.search(ComponentJobConstants.INPUT_PATTERN, input_value._data.path))
                )
                and input_value._data.mode != InputOutputModes.DIRECT
            )
            and (isinstance(input_value._meta, Input) and input_value._meta.mode != InputOutputModes.DIRECT)
        ):
            # For node input in pipeline job, client side can only validate node input which isn't bound to pipeline
            # input or node output.
            # 1. If node input is bound to pipeline input, we can't get pipeline level input mode in node level
            # validate. Even if we can judge through component input mode (_meta), we should note that pipeline level
            # input mode has higher priority than component level. so component input can be set "Mount", but it can
            # run successfully when pipeline input is "Direct".
            # 2. If node input is bound to last node output, input mode should be decoupled with output mode, so we
            # always get None mode in node level. In this case, if we define correct "Direct" mode in component yaml,
            # component level mode will take effect and run successfully. Otherwise, it need to set mode in node level
            # like input1: path: ${{parent.jobs.sample_word.outputs.output1}} mode: direct.
            msg = "Input '{}' is using '{}' mode, only '{}' is supported for Spark job"
            raise ValidationException(
                message=msg.format(
                    input_name, input_value._data.mode or input_value._meta.mode, InputOutputModes.DIRECT
                ),
                no_personal_data_message=msg.format("[input_name]", "[input_value.mode]", "direct"),
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )

    for output_name, output_value in outputs.items():
        if (
            isinstance(output_value, Output)
            and output_name != "default"
            and output_value.mode != InputOutputModes.DIRECT
        ):
            # For standalone job output
            msg = "Output '{}' is using '{}' mode, only '{}' is supported for Spark job"
            raise ValidationException(
                message=msg.format(output_name, output_value.mode, InputOutputModes.DIRECT),
                no_personal_data_message=msg.format("[output_name]", "[output_value.mode]", "direct"),
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        elif (
            isinstance(output_value, NodeOutput)
            and output_name != "default"
            and (
                isinstance(output_value._data, Output)
                and not (
                    isinstance(output_value._data.path, str)
                    and bool(re.search(ComponentJobConstants.OUTPUT_PATTERN, output_value._data.path))
                )
                and output_value._data.mode != InputOutputModes.DIRECT
            )
            and (isinstance(output_value._meta, Output) and output_value._meta.mode != InputOutputModes.DIRECT)
        ):
            # For node output in pipeline job, client side can only validate node output which isn't bound to pipeline
            # output.
            # 1. If node output is bound to pipeline output, we can't get pipeline level output mode in node level
            # validate. Even if we can judge through component output mode (_meta), we should note that pipeline level
            # output mode has higher priority than component level. so component output can be set "upload", but it
            # can run successfully when pipeline output is "Direct".
            msg = "Output '{}' is using '{}' mode, only '{}' is supported for Spark job"
            raise ValidationException(
                message=msg.format(
                    output_name, output_value._data.mode or output_value._meta.mode, InputOutputModes.DIRECT
                ),
                no_personal_data_message=msg.format("[output_name]", "[output_value.mode]", "direct"),
                target=ErrorTarget.SPARK_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
