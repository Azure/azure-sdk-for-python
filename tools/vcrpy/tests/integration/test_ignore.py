from six.moves.urllib.request import urlopen
import socket
from contextlib import contextmanager
import vcr


@contextmanager
def overridden_dns(overrides):
    """
    Monkeypatch socket.getaddrinfo() to override DNS lookups (name will resolve
    to address)
    """
    real_getaddrinfo = socket.getaddrinfo

    def fake_getaddrinfo(*args, **kwargs):
        if args[0] in overrides:
            address = overrides[args[0]]
            return [(2, 1, 6, "", (address, args[1]))]
        return real_getaddrinfo(*args, **kwargs)

    socket.getaddrinfo = fake_getaddrinfo
    yield
    socket.getaddrinfo = real_getaddrinfo


def test_ignore_localhost(tmpdir, httpbin):
    with overridden_dns({"httpbin.org": "127.0.0.1"}):
        cass_file = str(tmpdir.join("filter_qs.yaml"))
        with vcr.use_cassette(cass_file, ignore_localhost=True) as cass:
            urlopen("http://localhost:{}/".format(httpbin.port))
            assert len(cass) == 0
            urlopen("http://httpbin.org:{}/".format(httpbin.port))
            assert len(cass) == 1


def test_ignore_httpbin(tmpdir, httpbin):
    with overridden_dns({"httpbin.org": "127.0.0.1"}):
        cass_file = str(tmpdir.join("filter_qs.yaml"))
        with vcr.use_cassette(cass_file, ignore_hosts=["httpbin.org"]) as cass:
            urlopen("http://httpbin.org:{}/".format(httpbin.port))
            assert len(cass) == 0
            urlopen("http://localhost:{}/".format(httpbin.port))
            assert len(cass) == 1


def test_ignore_localhost_and_httpbin(tmpdir, httpbin):
    with overridden_dns({"httpbin.org": "127.0.0.1"}):
        cass_file = str(tmpdir.join("filter_qs.yaml"))
        with vcr.use_cassette(cass_file, ignore_hosts=["httpbin.org"], ignore_localhost=True) as cass:
            urlopen("http://httpbin.org:{}".format(httpbin.port))
            urlopen("http://localhost:{}".format(httpbin.port))
            assert len(cass) == 0


def test_ignore_localhost_twice(tmpdir, httpbin):
    with overridden_dns({"httpbin.org": "127.0.0.1"}):
        cass_file = str(tmpdir.join("filter_qs.yaml"))
        with vcr.use_cassette(cass_file, ignore_localhost=True) as cass:
            urlopen("http://localhost:{}".format(httpbin.port))
            assert len(cass) == 0
            urlopen("http://httpbin.org:{}".format(httpbin.port))
            assert len(cass) == 1
        with vcr.use_cassette(cass_file, ignore_localhost=True) as cass:
            assert len(cass) == 1
            urlopen("http://localhost:{}".format(httpbin.port))
            urlopen("http://httpbin.org:{}".format(httpbin.port))
            assert len(cass) == 1
