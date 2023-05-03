# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import pytest
import platform
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import test_config
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from azure.core.exceptions import ServiceRequestError

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.usefixtures("teardown")
class CustomRequestHandler(BaseHTTPRequestHandler):
    database_name = None

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _send_payload(self):
        self._set_headers()
        payload = "{\"id\":\"" + self.database_name + "\", \"_self\":\"self_link\"}"
        self.wfile.write(bytes(payload, "utf-8"))

    def do_GET(self):
        self._send_payload()

    def do_POST(self):
        self._send_payload()


class Server(Thread):
    def __init__(self, database_name, PORT):
        Thread.__init__(self)
        server_address = ('', PORT)
        CustomRequestHandler.database_name = database_name
        self.httpd = HTTPServer(server_address, CustomRequestHandler)

    def run(self):
        self.httpd.serve_forever()

    def shutdown(self):
        self.httpd.shutdown()


class ProxyTests(unittest.TestCase):
    """Proxy Tests.
    """
    host = 'http://localhost:8081'
    masterKey = test_config._test_config.masterKey
    testDbName = 'sample database'
    serverPort = 8089

    @classmethod
    def setUpClass(cls):
        global server
        global connection_policy
        server = Server(cls.testDbName, cls.serverPort)
        server.start()
        connection_policy = documents.ConnectionPolicy()
        connection_policy.ProxyConfiguration = documents.ProxyConfiguration()
        connection_policy.ProxyConfiguration.Host = 'http://127.0.0.1'

    @classmethod
    def tearDownClass(cls):
        server.shutdown()

    def test_success_with_correct_proxy(self):
        if platform.system() == 'Darwin':
            pytest.skip("TODO: Connection error raised on OSX")
        connection_policy.ProxyConfiguration.Port = self.serverPort
        client = cosmos_client.CosmosClient(self.host, self.masterKey, consistency_level="Session",
                                            connection_policy=connection_policy)
        created_db = client.create_database_if_not_exists(self.testDbName)
        self.assertEqual(created_db.id, self.testDbName, msg="Database id is incorrect")

    def test_failure_with_wrong_proxy(self):
        connection_policy.ProxyConfiguration.Port = self.serverPort + 1
        try:
            # client does a getDatabaseAccount on initialization, which fails
            cosmos_client.CosmosClient(self.host, {'masterKey': self.masterKey}, connection_policy=connection_policy)
            self.fail("Client instantiation is not expected")
        except Exception as e:
            self.assertTrue(type(e) is ServiceRequestError, msg="Error is not a ServiceRequestError")


if __name__ == "__main__":
    unittest.main()
