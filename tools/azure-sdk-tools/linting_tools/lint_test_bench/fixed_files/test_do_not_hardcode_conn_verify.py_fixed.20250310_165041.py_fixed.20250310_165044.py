# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# This code violates do-not-harcode-connection-verify

class FunctionKeywordArgumentsErrors:
    def create(self, x, connection_verify):
        if connection_verify:
            return x+1
        return x

    def run(self):
        # Removed hardcoded value for `connection_verify` to comply with guidelines.
        connection_verify = self.get_connection_verify_setting()  # This should be parameterized or configured
        client = self.create(connection_verify=connection_verify, x=0)
        return client

    def get_connection_verify_setting(self):
        # Placeholder method to demonstrate fetching a configuration setting.
        # Implementation should fetch from a configuration file or environment variable.
        return False
