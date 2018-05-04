﻿#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

__author__ = 'Microsoft Corp. <ptvshelp@microsoft.com>'
__version__ = '1.1.10'


class AzureException(Exception):
    pass


class AzureHttpError(AzureException):
    def __init__(self, message, status_code):
        super(AzureHttpError, self).__init__(message)
        self.status_code = status_code

    def __new__(cls, message, status_code, *args, **kwargs):
        if cls is AzureHttpError:
            if status_code == 404:
                cls = AzureMissingResourceHttpError
            elif status_code == 409:
                cls = AzureConflictHttpError
        return AzureException.__new__(cls, message, status_code, *args, **kwargs)


class AzureConflictHttpError(AzureHttpError):
    def __init__(self, message, status_code):
        super(AzureConflictHttpError, self).__init__(message, status_code)


class AzureMissingResourceHttpError(AzureHttpError):
    def __init__(self, message, status_code):
        super(AzureMissingResourceHttpError, self).__init__(message, status_code)
