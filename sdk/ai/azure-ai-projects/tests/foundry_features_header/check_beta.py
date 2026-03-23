import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')
import inspect
from azure.ai.projects import AIProjectClient
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpTransport

FAKE_ENDPOINT = "https://fake-account.services.ai.azure.com/api/projects/fake-project"

class FakeCredential:
    def get_token(self, *args, **kwargs):
        return AccessToken("fake-token", 9_999_999_999)

class CapturingTransport(HttpTransport):
    def send(self, request, **kwargs):
        raise Exception("captured")
    def open(self): pass
    def close(self): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass

client = AIProjectClient(endpoint=FAKE_ENDPOINT, credential=FakeCredential(), transport=CapturingTransport())

print("Type of client.beta:", type(client.beta))
print("Dir of client.beta:", [x for x in dir(client.beta) if not x.startswith('_')])
print()
for sc_name in sorted(dir(client.beta)):
    if sc_name.startswith('_'):
        continue
    sc = getattr(client.beta, sc_name)
    print(f"sc_name={sc_name}, callable={callable(sc)}, type={type(sc)}")
    if not callable(sc):
        print(f"  Sub-client type: {type(sc)}")
        print(f"  Dir: {[x for x in dir(sc) if not x.startswith('_')]}")
        for m_name in sorted(dir(sc)):
            if m_name.startswith('_'):
                continue
            method = getattr(sc, m_name)
            print(f"    {m_name}: ismethod={inspect.ismethod(method)}, isfunction={inspect.isfunction(method)}, iscoroutinefunction={inspect.iscoroutinefunction(method)}, callable={callable(method)}, type={type(method)}")
