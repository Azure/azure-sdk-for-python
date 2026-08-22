# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timezone

from azure.storage.blob import BlobClient, BlobSasPermissions, generate_blob_sas

ACCOUNT_NAME = "account"
ACCOUNT_KEY = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
CONTAINER_NAME = "container"
EXPIRY = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _generate_sas(blob_name, **kwargs):
    string_to_sign = []
    token = generate_blob_sas(
        account_name=ACCOUNT_NAME,
        container_name=CONTAINER_NAME,
        blob_name=blob_name,
        account_key=ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=EXPIRY,
        sts_hook=string_to_sign.append,
        **kwargs,
    )
    # The canonicalized resource is the fourth line of the string to sign,
    # after the signed permissions, start and expiry.
    canonicalized_resource = string_to_sign[0].split("\n")[3]
    return token, canonicalized_resource


class TestBlobSharedAccessSignature:

    def test_generate_blob_sas_canonicalizes_backslash_in_blob_name(self):
        token, canonicalized_resource = _generate_sas("dir\\file")

        # The service treats a backslash in a blob name as a forward slash when
        # validating the signature, so the signed resource must match.
        assert canonicalized_resource == "/blob/account/container/dir/file"
        assert "sr=b&" in token

        # The signature is identical to the one for the equivalent forward slash name.
        expected_token, _ = _generate_sas("dir/file")
        assert token == expected_token

        # The blob name used in the request URL is left untouched.
        client = BlobClient("https://account.blob.core.windows.net", CONTAINER_NAME, "dir\\file", credential=token)
        assert "/container/dir%5Cfile?" in client.url

    def test_generate_blob_sas_leaves_directory_name_untouched(self):
        token, canonicalized_resource = _generate_sas("dir\\sub", is_directory=True)

        assert canonicalized_resource == "/blob/account/container/dir\\sub"
        assert "sr=d&" in token
