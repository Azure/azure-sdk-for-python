# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# This code violates do-not-harcode-connection-verify

import os

class FunctionKeywordArgumentsErrors:
    def create(self, x, connection_verify):
        if connection_verify:
            return x+1
        return x

    def run(self):
        connection_verify = os.getenv("CONNECTION_VERIFY", "False") == "True"
        client = self.create(connection_verify=connection_verify, x=0)
        return client
