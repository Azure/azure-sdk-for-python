import dns.resolver

class TestDnsPython():

    def test(self):
        test = dns.resolver.resolve
        assert test is not None