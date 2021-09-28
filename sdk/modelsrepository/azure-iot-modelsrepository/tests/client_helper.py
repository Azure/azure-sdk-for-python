# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import json
from enum import Enum
from azure.iot.modelsrepository import (
    ModelsRepositoryClient,
    DEFAULT_LOCATION
)

class ClientType(Enum):
    """
    Model repository properties
    """
    local = "local"
    remote = "remote"

# Testing Constants
# Remote Repository with metadata
REMOTE_REPO_METADATA = DEFAULT_LOCATION
# Remote Repository without metadata
REMOTE_REPO_NO_METADATA = "https://raw.githubusercontent.com/Azure/iot-plugandplay-models/main/"
# Local Repository
test_dir = os.path.dirname(os.path.abspath(__file__))
LOCAL_REPOSITORY = os.path.join(test_dir, "local_repository")
METADATA_PATH = os.path.join(LOCAL_REPOSITORY, "metadata.json")

# TODO code for adding/removing metadata file
def add_local_repo_metadata():
    """ Adds a metadata file to the local repository """
    metadata_properties = {
        "commitId": "abcd1234",
        "pubishDateUTC": "0000000",
        "sourceRepo": LOCAL_REPOSITORY,
        "totalModelCount": 25,
        "features": {
            "expanded": True,
            "index": False,
        },
    }
    with open(METADATA_PATH, "w") as f:
        f.write(json.dumps(metadata_properties))


def delete_local_repo_metadata():
    """ Deletes a metadata file to the local repository """
    if os.path.exists(METADATA_PATH):
        os.remove(METADATA_PATH)


################################
# Client Fixture Mixin Classes #
################################


class RemoteRepositoryMixin(object):
    def setUp(self, metadata=True):
        self.metadata = metadata
        repo = REMOTE_REPO_METADATA if metadata else REMOTE_REPO_NO_METADATA

        self.client = ModelsRepositoryClient(repository_location=repo)
        self.client_type = ClientType.remote.value
        super(RemoteRepositoryMixin, self).setUp()

    def tearDown(self):
        self.client.close()
        super(RemoteRepositoryMixin, self).tearDown()


class LocalRepositoryMixin(object):
    def setUp(self, metadata=True):
        self.metadata = metadata
        if metadata:
            add_local_repo_metadata()

        self.client = ModelsRepositoryClient(repository_location=LOCAL_REPOSITORY)
        self.client_type = ClientType.local.value
        super(LocalRepositoryMixin, self).setUp()

    def tearDown(self):
        if self.metadata:
            delete_local_repo_metadata()
        self.client.close()
        super(LocalRepositoryMixin, self).tearDown()
