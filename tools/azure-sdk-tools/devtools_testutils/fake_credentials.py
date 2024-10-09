from azure.core.credentials import AccessToken

# General-use placeholder values
SANITIZED = "Sanitized"

# General-use fake credentials
FAKE_ACCESS_TOKEN = (
    "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJlbWFpbCI6IkJvYkBjb250b3NvLmNvbSIsImdpdmVuX25hbWUiOiJCb2I"
    "iLCJpc3MiOiJodHRwOi8vRGVmYXVsdC5Jc3N1ZXIuY29tIiwiYXVkIjoiaHR0cDovL0RlZmF1bHQuQXVkaWVuY2UuY29tIiwiaWF0IjoiMTYwNz"
    "k3ODY4MyIsIm5iZiI6IjE2MDc5Nzg2ODMiLCJleHAiOiIxNjA3OTc4OTgzIn0."
)
FAKE_ID = "00000000-0000-0000-0000-000000000000"
FAKE_LOGIN_PASSWORD = "F4ke_L0gin_P4ss"

# Service-specific fake credentials
BATCH_TEST_PASSWORD = "kt#_gahr!@aGERDXA"
MGMT_HDINSIGHT_FAKE_KEY = "qFmud5LfxcCxWUvWcGMhKDp0v0KuBRLsO/AIddX734W7lzdInsVMsB5ILVoOrF+0fCfk/IYYy5SJ9Q+2v4aihQ=="
SERVICEBUS_FAKE_SAS = (
    "SharedAccessSignature sr=https%3A%2F%2Ffoo.servicebus.windows.net&sig=dummyValue%3D&se=168726" "7490&skn=dummyKey"
)
STORAGE_ACCOUNT_FAKE_KEY = "NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg=="


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.

    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)
        self.get_token_count = 0

    def get_token(self, *args, **kwargs):
        self.get_token_count += 1
        return self.token
