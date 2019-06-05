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
        if failure_tasks and errors:
            self.message =  "Multiple errors encountered. " \
                            "Check the `failure_tasks` and `errors` properties for additional details"
        if errors:
            if len(errors) > 1:
                self.message = "The SDK encountered an internal error. " \
                               "Check the `errors` property for the inner exceptions"
            else:
                self.message = errors[0].message
        if failure_tasks:
            if len(failure_tasks) > 1:
                self.message = "Multiple client side errors occured when submitting the request. " \
                               "Check the `failure_tasks` property for details on these tasks."
            else:
                result = failure_tasks[0]
                self.message = "Task with id `%s` failed due to client error - %s::%s" % \
                               result.task_id,\
                               result.error.code,\
                               result.error.message
        self.pending_tasks = list(pending_task_list)
        self.failure_tasks = list(failure_tasks)
        self.errors = list(errors)
