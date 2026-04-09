"""Serve the browser client on a local HTTP port.

Usage::

    python serve_browser_client.py
    python serve_browser_client.py --port 3000
"""
import argparse
import http.server
import os
import functools


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve browser client locally")
    parser.add_argument("--port", type=int, default=8080, help="Port to serve on (default: 8080)")
    args = parser.parse_args()

    directory = os.path.dirname(os.path.abspath(__file__))
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)

    with http.server.HTTPServer(("", args.port), handler) as httpd:
        print(f"Serving browser client at http://localhost:{args.port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
