# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore ests
"""
Local test server for token binding proxy testing.

This server simulates a token proxy that can:
1. Accept HTTPS requests with custom SNI and CA certificates
2. Route requests to downstream services
3. Handle various error scenarios for testing
4. Support certificate rotation scenarios
"""

import argparse
import ipaddress
import json
import logging
import os
import ssl
import tempfile
import threading
import time
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import uuid

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class TokenProxyHandler(BaseHTTPRequestHandler):
    """HTTP request handler that simulates a token proxy."""

    def log_message(self, format, *args):
        """Override to use proper logging instead of stderr."""
        logging.info(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        """Handle GET requests."""
        self._handle_request()

    def do_POST(self):
        """Handle POST requests."""
        self._handle_request()

    def do_PUT(self):
        """Handle PUT requests."""
        self._handle_request()

    def do_DELETE(self):
        """Handle DELETE requests."""
        self._handle_request()

    def do_PATCH(self):
        """Handle PATCH requests."""
        self._handle_request()

    def _handle_request(self):
        """Common request handling logic."""
        path = self.path
        headers = dict(self.headers)

        # Read request body if present
        content_length = int(headers.get("content-length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        logging.info(f"Received {self.command} {path}")
        logging.info(f"Headers: {headers}")

        # Simulate different responses based on path
        if path == "/health":
            self._send_health_response()
        elif path.endswith("/oauth2/v2.0/token"):
            self._send_token_response(body)
        elif path == "/error/500":
            self._send_error_response(500, "Internal Server Error")
        elif path == "/error/ssl":
            # Simulate SSL error by closing connection
            self.wfile.close()
            return
        else:
            self._send_proxy_response(path, body, headers)

    def _send_health_response(self):
        """Send a health check response."""
        response = {"status": "healthy", "timestamp": time.time(), "server": "token-proxy-test-server"}
        self._send_json_response(response)

    def _send_token_response(self, body):
        """Send a mock OAuth token response."""
        # Parse the request body to extract grant type, etc.
        try:
            if body:
                body_str = body.decode("utf-8")
                logging.info(f"Token request body: {body_str}")
        except Exception as e:
            logging.warning(f"Could not decode request body: {e}")

        # Mock token response
        response = {
            "access_token": f"mock_token_{uuid.uuid4().hex[:16]}",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "https://graph.microsoft.com/.default",
        }
        self._send_json_response(response)

    def _send_proxy_response(self, path, body, headers):
        """Send a generic proxy response."""
        response = {
            "proxied_path": path,
            "method": self.command,
            "headers_received": dict(headers),
            "body_length": len(body),
            "proxy_server": "token-proxy-test-server",
        }
        self._send_json_response(response)

    def _send_json_response(self, data, status_code=200):
        """Send a JSON response."""
        response_json = json.dumps(data, indent=2)

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_json)))
        self.end_headers()

        self.wfile.write(response_json.encode("utf-8"))

    def _send_error_response(self, status_code, message):
        """Send an error response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(message)))
        self.end_headers()

        self.wfile.write(message.encode("utf-8"))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server for handling multiple concurrent requests."""

    allow_reuse_address = True
    daemon_threads = True


class TokenProxyTestServer:
    """Test server that can be configured with SSL/TLS and custom certificates."""

    def __init__(self, host="localhost", port=0, use_ssl=True):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.server = None
        self.server_thread = None
        self.cert_file = None
        self.key_file = None
        self.ca_file = None
        self._temp_files = []

    def generate_test_certificates(self):
        """Generate self-signed certificates for testing."""

        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Create certificate
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Test"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Test"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Proxy Server"),
                x509.NameAttribute(NameOID.COMMON_NAME, self.host),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
            .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName(self.host),
                        x509.DNSName("localhost"),
                        x509.DNSName("1234.ests.aks"),
                        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                    ]
                ),
                critical=False,
            )
            .sign(private_key, hashes.SHA256())
        )

        # Write certificate to temp file
        cert_fd, self.cert_file = tempfile.mkstemp(suffix=".pem", prefix="test_cert_")
        with os.fdopen(cert_fd, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        self._temp_files.append(self.cert_file)

        # Write private key to temp file
        key_fd, self.key_file = tempfile.mkstemp(suffix=".pem", prefix="test_key_")
        with os.fdopen(key_fd, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
        self._temp_files.append(self.key_file)

        # Use the same cert as CA for simplicity
        self.ca_file = self.cert_file

        logging.info(f"Generated test certificate: {self.cert_file}")
        logging.info(f"Generated test key: {self.key_file}")

    def start(self):
        """Start the test server."""
        if self.use_ssl:
            self.generate_test_certificates()

        # Create server
        self.server = ThreadedHTTPServer((self.host, self.port), TokenProxyHandler)

        if self.use_ssl:
            # Configure SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            if self.cert_file and self.key_file:
                context.load_cert_chain(self.cert_file, self.key_file)

            self.server.socket = context.wrap_socket(self.server.socket, server_side=True)

        # Update port if it was 0 (auto-assigned)
        self.port = self.server.server_address[1]

        # Start server in background thread
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

        scheme = "https" if self.use_ssl else "http"
        logging.info(f"Test server started at {scheme}://{self.host}:{self.port}")

        return f"{scheme}://{self.host}:{self.port}"

    def stop(self):
        """Stop the test server and clean up."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()

        if self.server_thread:
            self.server_thread.join(timeout=5)

        # Clean up temporary files
        for temp_file in self._temp_files:
            try:
                os.unlink(temp_file)
            except OSError:
                pass
        self._temp_files.clear()  # Clear the list after cleanup

        logging.info("Test server stopped and cleaned up")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    @property
    def base_url(self):
        """Get the base URL of the server."""
        scheme = "https" if self.use_ssl else "http"
        return f"{scheme}://{self.host}:{self.port}"


def main():
    """Run the test server standalone."""
    parser = argparse.ArgumentParser(description="Token Proxy Test Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8443, help="Port to bind to")
    parser.add_argument("--no-ssl", action="store_true", help="Disable SSL/TLS")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    # Start server
    with TokenProxyTestServer(host=args.host, port=args.port, use_ssl=not args.no_ssl) as server:
        print(f"Server running at {server.base_url}")
        print("Available endpoints:")
        print(f"  {server.base_url}/health - Health check")
        print(f"  {server.base_url}/oauth2/v2.0/token - Mock OAuth token endpoint")
        print(f"  {server.base_url}/error/500 - Simulate server error")
        print(f"  {server.base_url}/error/ssl - Simulate SSL error")
        print(f"  {server.base_url}/<any-path> - Generic proxy response")
        print("\nPress Ctrl+C to stop")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    main()
