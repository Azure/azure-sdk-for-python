# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# This code violates do-not-harcode-connection-verify


class FunctionKeywordArgumentsErrors:
    def create(self, x, connection_verify=None):
        if connection_verify is not None and connection_verify:
            return x + 1
        return x

    def run(self):
        # Use a variable for connection_verify to avoid hardcoding
        connection_verify_value = False
        client = self.create(x=0, connection_verify=connection_verify_value)
        return client
