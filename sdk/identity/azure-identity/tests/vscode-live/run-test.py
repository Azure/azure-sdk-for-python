# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.identity import VSCodeCredential

def test_live():
    credential = VSCodeCredential()
    token=credential.get_token('https://vault.azure.net/.default')
    print(token)

if __name__ == "__main__":
    test_live()
