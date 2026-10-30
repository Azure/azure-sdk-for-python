# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Offline smoke tests for the installed extension wheel."""

import unittest
from importlib.metadata import version

from azure.storage.extensions import transfer
from azure.storage.extensions.transfer import _native


class TestExtensionWheel(unittest.TestCase):
    def test_native_module_available(self):
        self.assertTrue(transfer.is_available())
        self.assertEqual(transfer.__version__, version("azure-storage-extensions-transfer"))
        self.assertIs(transfer.NativeTransferError, _native.NativeTransferError)
        self.assertTrue(issubclass(transfer.NativeTransferError, Exception))
        self.assertTrue(callable(transfer.upload_blob))
        self.assertTrue(callable(transfer.download_blob))
        self.assertTrue(callable(_native.upload_blob))
        self.assertTrue(callable(_native.download_blob))
        self.assertIsInstance(_native.NativeDownloadStream, type)


if __name__ == "__main__":
    unittest.main(verbosity=2)
