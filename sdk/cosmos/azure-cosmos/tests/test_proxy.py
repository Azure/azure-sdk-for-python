# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import platform
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import pytest
from azure.core.exceptions import ServiceRequestError

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import test_config


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


@pytest.mark.cosmosEmulator
class TestProxy(unittest.TestCase):
    """Proxy Tests.
    """
    host = 'http://localhost:8081'
    masterKey = test_config.TestConfig.masterKey
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

    # Needs further debugging
    @pytest.mark.skip
    def test_success_with_correct_proxy(self):
        if platform.system() == 'Darwin':
            self.skipTest("TODO: Connection error raised on OSX")
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
