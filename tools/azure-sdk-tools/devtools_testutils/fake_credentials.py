from azure.core.credentials import AccessToken

STORAGE_ACCOUNT_FAKE_KEY = "NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg=="
MGMT_HDINSIGHT_FAKE_KEY = "qFmud5LfxcCxWUvWcGMhKDp0v0KuBRLsO/AIddX734W7lzdInsVMsB5ILVoOrF+0fCfk/IYYy5SJ9Q+2v4aihQ=="


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)
        self.get_token_count = 0

    def get_token(self, *args):
        self.get_token_count += 1
        return self.token
