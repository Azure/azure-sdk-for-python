# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
import typing
from ._models import BatchPoolReplaceContent as BatchPoolReplaceContentGenerated

__all__: List[str] = [
    "BatchPoolReplaceContent",
    "CreateTasksErrorException"
]  # Add all objects you want publicly available to users at this package level

class BatchPoolReplaceContent(BatchPoolReplaceContentGenerated):

    def as_dict(self, *, exclude_readonly: bool = False) -> typing.Dict[str, typing.Any]:
        result = super().as_dict(exclude_readonly=exclude_readonly)
        result["certificateReferences"] = []
        return result

    #     """Return a dict that can be JSONify using json.dump.

    #     :keyword bool exclude_readonly: Whether to remove the readonly properties.
    #     :returns: A dict JSON compatible object
    #     :rtype: dict
    #     """

    #     result = {}
    #     result["certificateReferences"] = []
    #     if exclude_readonly:
    #         readonly_props = [p._rest_name for p in self._attr_to_rest_field.values() if _is_readonly(p)]
    #     for k, v in self.items():
    #         if exclude_readonly and k in readonly_props:  # pyright: ignore
    #             continue
    #         is_multipart_file_input = False
    #         try:
    #             is_multipart_file_input = next(
    #                 rf for rf in self._attr_to_rest_field.values() if rf._rest_name == k
    #             )._is_multipart_file_input
    #         except StopIteration:
    #             pass
    #         result[k] = v if is_multipart_file_input else Model._as_dict_value(v, exclude_readonly=exclude_readonly)
    #     return result
    

class CreateTasksErrorException(Exception):
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
        super(CreateTasksErrorException, self).__init__(self.message)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
