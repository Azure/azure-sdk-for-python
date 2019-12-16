# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class AzureTestError(Exception):
    def __init__(self, error_message):
        message = 'An error caused by the Azure test harness failed the test: {}'
        super(AzureTestError, self).__init__(message.format(error_message))

class NameInUseError(Exception):
    def __init__(self, vault_name):
        error_message = "A vault with the name {} already exists".format(vault_name)
        super(NameInUseError, self).__init__(error_message)

class ReservedResourceNameError(Exception):
    def __init__(self, rg_name):
        error_message = "The resource name {} or a part of the name is trademarked / reserved".format(rg_name)
        super(ReservedResourceNameError, self).__init__(error_message)