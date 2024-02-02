# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pickle
from azure.identity import DefaultAzureCredential

def test_pickle_dac():
    cred = DefaultAzureCredential()
    with open('data.pkl', 'wb') as outfile:
        pickle.dump(cred, outfile)
    with open('data.pkl', 'rb') as infile:
        data_loaded = pickle.load(infile)
