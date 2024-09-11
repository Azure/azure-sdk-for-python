# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any

from azure.core.exceptions import HttpResponseError

from ._models import BatchPoolReplaceContent as BatchPoolReplaceContentGenerated
from .._model_base import rest_field

__all__: List[str] = [
    "BatchPoolReplaceContent",
    "CreateTasksError",
]  # Add all objects you want publicly available to users at this package level

class BatchPoolReplaceContent(BatchPoolReplaceContentGenerated):
    certificate_references: List[str] = rest_field(name="certificateReferences")

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)
        self.certificate_references = []


class CreateTasksError(HttpResponseError):
    """Aggregate Exception containing details for any failures from a task add operation.

    :param str message: Error message describing exit reason
    :param [~TaskAddParameter] pending_tasks: List of tasks remaining to be submitted.
    :param [~TaskAddResult] failure_tasks: List of tasks which failed to add
    :param [~Exception] errors: List of unknown errors forcing early termination
    """

    def __init__(self, pending_tasks=None, failure_tasks=None, errors=None):
        self.pending_tasks = list(pending_tasks)
        self.failure_tasks = list(failure_tasks)
        self.errors = list(errors)
        if failure_tasks and errors:
            self.message = (
                "Multiple errors encountered. Check the `failure_tasks` and "
                "`errors` properties for additional details."
            )
        elif errors:
            if len(errors) > 1:
                self.message = (
                    "Multiple errors occurred when submitting add_collection "
                    "requests. Check the `errors` property for the inner "
                    "exceptions."
                )
            else:
                self.message = str(errors[0])
        elif failure_tasks:
            if len(failure_tasks) > 1:
                self.message = (
                    "Multiple client side errors occurred when adding the "
                    "tasks. Check the `failure_tasks` property for details on"
                    " these tasks."
                )
            else:
                result = failure_tasks[0]
                self.message = "Task with id `%s` failed due to client error - %s::%s" % (
                    result.task_id,
                    result.error.code,
                    result.error.message,
                )
        super(CreateTasksError, self).__init__(self.message)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
