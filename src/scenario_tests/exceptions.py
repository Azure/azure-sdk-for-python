# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class CliTestError(Exception):
    def __init__(self, error_message):
        message = 'An error caused by the CLI test harness failed the test: {}'
        super(CliTestError, self).__init__(message.format(error_message))


class CliExecutionError(Exception):
    def __init__(self, exception):
        self.exception = exception
        message = 'The CLI throws exception {} during execution and fails the command.'
        super(CliExecutionError, self).__init__(message.format(exception.__class__.__name__,
                                                               exception))


class JMESPathCheckAssertionError(AssertionError):
    def __init__(self, query, expected, actual, json_data):
        message = "Query '{}' doesn't yield expected value '{}', instead the actual value " \
                  "is '{}'. Data: \n{}\n".format(query, expected, actual, json_data)
        super(JMESPathCheckAssertionError, self).__init__(message)
