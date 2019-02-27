# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class CreateTasksErrorException(Exception):
    """ Aggregate Exception containing details for any failures from a task add operation.

    :param str message: Error message describing exit reason
    :param [~TaskAddParameter] pending_task_list: List of tasks remaining to be submitted.
    :param [~TaskAddResult] failure_tasks: List of tasks which failed to add
    :param [~Exception] errors: List of unknown errors forcing early termination
    """
    def __init__(self, message, pending_task_list=None, failure_tasks=None, errors=None):
        self.message = message
        self.pending_tasks = list(pending_task_list)
        self.failure_tasks = list(failure_tasks)
        self.errors = list(errors)
