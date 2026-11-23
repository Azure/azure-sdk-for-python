# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Offline smoke tests for the installed extension wheel."""

import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import version
from threading import Thread

from azure.storage.extensions import transfer
from azure.storage.extensions.transfer import _native


class TestExtensionWheel(unittest.TestCase):
    def test_native_module_available(self):
        self.assertTrue(transfer.is_available())
        self.assertEqual(transfer.__version__, version("azure-storage-extensionstransfer"))
        self.assertIs(transfer.NativeTransferError, _native.NativeTransferError)
        self.assertTrue(issubclass(transfer.NativeTransferError, Exception))
        self.assertTrue(callable(transfer.upload_blob))
        self.assertTrue(callable(transfer.download_blob))
        self.assertTrue(callable(_native.upload_blob))
        self.assertTrue(callable(_native.download_blob))
        self.assertIsInstance(_native.NativeDownloadStream, type)

    def test_download_partitions_are_available_as_read_only_buffers(self):
        payload = bytes(range(256)) * 100

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                start, end = self.headers["Range"].removeprefix("bytes=").split("-")
                start, end = int(start), min(int(end) + 1, len(payload))
                self.send_response(206)
                self.send_header("ETag", '"stable"')
                self.send_header("Content-Length", str(end - start))
                self.send_header("Content-Range", f"bytes {start}-{end - 1}/{len(payload)}")
                self.end_headers()
                self.wfile.write(payload[start:end])

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        stream = transfer.download_blob(
            f"http://127.0.0.1:{server.server_port}/container/blob", max_concurrency=2, max_chunk_size=7000
        )
        views = []
        while True:
            buffer = stream.next_buffer()
            if buffer is None:
                break
            views.append(memoryview(buffer))  # Views stay valid after later partitions are requested.
        self.assertGreater(len(views), 1)
        self.assertTrue(all(view.readonly and view.format == "B" for view in views))
        self.assertEqual(b"".join(views), payload)
        with self.assertRaises(TypeError):
            views[0][0] = 0


if __name__ == "__main__":
    unittest.main(verbosity=2)
