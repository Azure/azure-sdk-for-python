# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pickle
from azure.identity import DefaultAzureCredential, SharedTokenCacheCredential
from azure.identity._internal.msal_credentials import MsalCredential


def test_pickle_dac():
    cred = DefaultAzureCredential()
    with open("data.pkl", "wb") as outfile:
        pickle.dump(cred, outfile)
    with open("data.pkl", "rb") as infile:
        data_loaded = pickle.load(infile)


def test_pickle_shared_token_cache():
    cred = SharedTokenCacheCredential()
    cred._credential._initialize_cache()
    with open("data.pkl", "wb") as outfile:
        pickle.dump(cred, outfile)
    with open("data.pkl", "rb") as infile:
        data_loaded = pickle.load(infile)


def test_pickle_msal_credential():
    cred = MsalCredential(client_id="CLIENT_ID")
    app = cred._get_app()
    with open("data.pkl", "wb") as outfile:
        pickle.dump(cred, outfile)
    with open("data.pkl", "rb") as infile:
        data_loaded = pickle.load(infile)
