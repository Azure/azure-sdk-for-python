# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.identity import VSCodeCredential

def test_live():
    credential = VSCodeCredential()
    str=credential.get_token('https://vault.azure.net/.default')
    print(str)

if __name__ == "__main__":
    test_live()
