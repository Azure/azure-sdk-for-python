# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential


def resolve_data_path() -> None:
    credential = DefaultAzureCredential()
    ml_client = MLClient.from_config(credential=credential)

    # [START resolve_data_path]
    # Metadata-only resolution does not access storage or retrieve datastore secrets.
    blob = ml_client.data.resolve_path(
        "azureml://datastores/my_blob_store/paths/data/Titanic.csv",
        follow_mltable=False,
    )
    print(blob.uri)

    # For an MLTable, the root URI identifies the definition. Its sources identify the data.
    table = ml_client.data.resolve_path("azureml://datastores/workspaceblobstore/paths/data/table-definition/")
    for source in table.sources:
        print(source.uri, source.path_type)
    print(table.transformations)  # Preserve version_as_of and other read semantics.
    # [END resolve_data_path]

    # Returned URLs are locations, not access grants. Authenticate separately when reading.
    credential.close()


if __name__ == "__main__":
    resolve_data_path()
