# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pickle
from azure.identity.aio import DefaultAzureCredential


def test_pickle_dac():
    cred = DefaultAzureCredential()
    with open("data_aio.pkl", "wb") as outfile:
        pickle.dump(cred, outfile)
    with open("data_aio.pkl", "rb") as infile:
        data_loaded = pickle.load(infile)
