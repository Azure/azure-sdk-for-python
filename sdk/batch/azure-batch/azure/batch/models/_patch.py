# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
from typing import List, Any, Optional

from azure.core.exceptions import HttpResponseError

from ._models import BatchPoolReplaceContent as BatchPoolReplaceContentGenerated
from .._model_base import rest_field

__all__: List[str] = [
    "CreateTasksError",
    "BatchFileProperties",
]  # Add all objects you want publicly available to users at this package level

class CreateTasksError(HttpResponseError):
    """Aggregate Exception containing details for any failures from a task add operation.

    :param str message: Error message describing exit reason
    :param [~TaskAddParameter] pending_tasks: List of tasks remaining to be submitted.
    :param [~TaskAddResult] failure_tasks: List of tasks which failed to add
    :param [~Exception] errors: List of unknown errors forcing early termination
    """

    def __init__(self, pending_tasks=[], failure_tasks=[], errors=[]):
        self.pending_tasks = pending_tasks
        self.failure_tasks = failure_tasks
        self.errors = errors
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

class BatchFileProperties:

    """Information about a file or directory on a Compute Node with additional properties.

    :ivar url: The URL of the file.
    :vartype url: str
    :ivar is_directory: Whether the object represents a directory.
    :vartype is_directory: bool
    :ivar creation_time: The file creation time. The creation time is not returned for files on
    Linux Compute Nodes.
    :vartype creation_time: ~datetime.datetime
    :ivar last_modified: The time at which the file was last modified. Required.
    :vartype last_modified: ~datetime.datetime
    :ivar content_length: The length of the file. Required.
    :vartype content_length: int
    :ivar content_type: The content type of the file.
    :vartype content_type: str
    :ivar file_mode: The file mode attribute in octal format. The file mode is returned only for
     files on Linux Compute Nodes.
    :vartype file_mode: str
    """

    url: Optional[str] 
    """The URL of the file."""
    is_directory: Optional[bool]
    """Whether the object represents a directory."""
    creation_time: Optional[datetime.datetime]
    """The file creation time. The creation time is not returned for files on Linux Compute Nodes."""
    last_modified: datetime.datetime
    """The time at which the file was last modified. Required."""
    content_length: int
    """The length of the file. Required."""
    content_type: Optional[str]
    """The content type of the file."""
    file_mode: Optional[str]
    """The file mode attribute in octal format. The file mode is returned only for files on Linux
     Compute Nodes."""

    def __init__(
        self,
        *,
        url: Optional[str] = None,
        is_directory: Optional[bool] = None,
        last_modified: datetime.datetime,
        content_length: int,
        creation_time: Optional[datetime.datetime] = None,
        content_type: Optional[str] = None,
        file_mode: Optional[str] = None,
    ) -> None:
        self.url = url
        self.is_directory = is_directory
        self.creation_time = creation_time
        self.last_modified = last_modified
        self.content_length = content_length
        self.content_type = content_type
        self.file_mode = file_mode

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
