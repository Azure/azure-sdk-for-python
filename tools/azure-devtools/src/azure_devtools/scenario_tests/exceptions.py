# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class AzureTestError(Exception):
    def __init__(self, error_message):
        message = 'An error caused by the Azure test harness failed the test: {}'
        super(AzureTestError, self).__init__(message.format(error_message))
