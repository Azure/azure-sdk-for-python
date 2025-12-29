# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class AzureTestError(Exception):
    def __init__(self, error_message):
        message = f"An error caused by the Azure test harness failed the test: {error_message}"
        super(AzureTestError, self).__init__(message)


class ReservedResourceNameError(Exception):
    def __init__(self, rg_name):
        message = f"The resource name {rg_name} or a part of the name is trademarked / reserved"
        super(ReservedResourceNameError, self).__init__(message)
