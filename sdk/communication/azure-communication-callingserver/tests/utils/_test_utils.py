# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid
from azure.communication.identity import CommunicationIdentityClient
from devtools_testutils import is_live
from ._test_constants import AZURE_TENANT_ID

class TestUtils:
    def get_new_user_id(connection_str):
        if is_live():
            identity_client = CommunicationIdentityClient.from_connection_string(connection_str)
            user = identity_client.create_user()
            return user.properties['id']

        return "8:acs:" + AZURE_TENANT_ID + "_" + str(uuid.uuid4())

    def get_group_id(test_name):
        # If tests are running in live mode, we want them to all
        # have unique groupId's so they do not conflict with other
        # recording tests running in live mode.
        if is_live():
            return str(uuid.uuid4())

        # For recording tests we need to make sure the groupId
        # matches the recorded groupId, or the call will fail.
        return str(uuid.uuid3(uuid.NAMESPACE_OID, test_name))