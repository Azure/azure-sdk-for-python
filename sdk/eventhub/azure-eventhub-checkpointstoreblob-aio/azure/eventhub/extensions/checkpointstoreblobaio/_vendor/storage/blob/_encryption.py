# pylint: disable=too-many-lines
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


import warnings

class StorageEncryptionMixin(object):
    def _configure_encryption(self, kwargs):
        self.require_encryption = False
        self.encryption_version = "1.0"
        self.key_encryption_key = None
        self.key_resolver_function = None
        if self.key_encryption_key and self.encryption_version == '1.0':
            warnings.warn("This client has been configured to use encryption with version 1.0. " +
                          "Version 1.0 is deprecated and no longer considered secure. It is highly " +
                          "recommended that you switch to using version 2.0. The version can be " +
                          "specified using the 'encryption_version' keyword.")
