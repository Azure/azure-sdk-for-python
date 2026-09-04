from datetime import datetime, timedelta

from azure.storage.blob import BlobSasPermissions, generate_blob_sas


def test_generate_blob_sas_normalizes_backslashes_in_canonical_resource():
    string_to_sign = []

    generate_blob_sas(
        account_name="account",
        container_name="container",
        blob_name="dir\\file",
        account_key="a2V5",
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1),
        sts_hook=string_to_sign.append,
    )

    assert "/blob/account/container/dir/file\n" in string_to_sign[0]
