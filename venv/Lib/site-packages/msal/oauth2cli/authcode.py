# Note: This docstring is also used by this script's command line help.
"""A one-stop helper for desktop app to acquire an authorization code.

It starts a web server to listen redirect_uri, waiting for auth code.
It optionally opens a browser window to guide a human user to manually login.
After obtaining an auth code, the web server will automatically shut down.
"""

import argparse
import webbrowser
import logging

try:  # Python 3
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs, urlencode
except ImportError:  # Fall back to Python 2
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urlparse import urlparse, parse_qs
    from urllib import urlencode

from .oauth2 import Client


logger = logging.getLogger(__name__)

def obtain_auth_code(listen_port, auth_uri=None):
    """This function will start a web server listening on http://localhost:port
    and then you need to open a browser on this device and visit your auth_uri.
    When interaction finishes, this function will return the auth code,
    and then shut down the local web server.

    :param listen_port:
        The local web server will listen at http://localhost:<listen_port>
        Unless the authorization server supports dynamic port,
        you need to use the same port when you register with your app.
    :param auth_uri: If provided, this function will try to open a local browser.
    :return: Hang indefinitely, until it receives and then return the auth code.
    """
    exit_hint = "Visit http://localhost:{p}?code=exit to abort".format(p=listen_port)
    logger.warning(exit_hint)
    if auth_uri:
        page = "http://localhost:{p}?{q}".format(p=listen_port, q=urlencode({
            "text": "Open this link to sign in. You may use incognito window",
            "link": auth_uri,
            "exit_hint": exit_hint,
            }))
        browse(page)
    server = HTTPServer(("", int(listen_port)), AuthCodeReceiver)
    try:
        server.authcode = None
        while not server.authcode:
            # Derived from
            # https://docs.python.org/2/library/basehttpserver.html#more-examples
            server.handle_request()
        return server.authcode
    finally:
        server.server_close()

def browse(auth_uri):
    controller = webbrowser.get()  # Get a default controller
    # Some Linux Distro does not setup default browser properly,
    # so we try to explicitly use some popular browser, if we found any.
    for browser in ["chrome", "firefox", "safari", "windows-default"]:
        try:
            controller = webbrowser.get(browser)
            break
        except webbrowser.Error:
            pass  # This browser is not installed. Try next one.
    logger.info("Please open a browser on THIS device to visit: %s" % auth_uri)
    controller.open(auth_uri)

class AuthCodeReceiver(BaseHTTPRequestHandler):
    def do_GET(self):
        # For flexibility, we choose to not check self.path matching redirect_uri
        #assert self.path.startswith('/THE_PATH_REGISTERED_BY_THE_APP')
        qs = parse_qs(urlparse(self.path).query)
        if qs.get('code'):  # Then store it into the server instance
            ac = self.server.authcode = qs['code'][0]
            self._send_full_response('Authcode:\n{}'.format(ac))
            # NOTE: Don't do self.server.shutdown() here. It'll halt the server.
        elif qs.get('text') and qs.get('link'):  # Then display a landing page
            self._send_full_response(
                '<a href={link}>{text}</a><hr/>{exit_hint}'.format(
                link=qs['link'][0], text=qs['text'][0],
                exit_hint=qs.get("exit_hint", [''])[0],
                ))
        else:
            self._send_full_response("This web service serves your redirect_uri")

    def _send_full_response(self, body, is_ok=True):
        self.send_response(200 if is_ok else 400)
        content_type = 'text/html' if body.startswith('<') else 'text/plain'
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    p = parser = argparse.ArgumentParser(
        description=__doc__ + "The auth code received will be shown at stdout.")
    p.add_argument('endpoint',
        help="The auth endpoint for your app. For example: "
            "https://login.microsoftonline.com/your_tenant/oauth2/authorize")
    p.add_argument('client_id', help="The client_id of your application")
    p.add_argument('redirect_port', type=int, help="The port in redirect_uri")
    args = parser.parse_args()
    client = Client(args.client_id, authorization_endpoint=args.endpoint)
    auth_uri = client.build_auth_request_uri("code")
    print(obtain_auth_code(args.redirect_port, auth_uri))

