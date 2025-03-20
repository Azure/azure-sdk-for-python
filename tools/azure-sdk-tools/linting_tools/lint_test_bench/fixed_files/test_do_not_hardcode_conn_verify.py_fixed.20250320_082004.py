# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class FunctionKeywordArgumentsErrors:
    def create(self, x, connection_verify):
        return x + 1 if connection_verify else x

    def run(self):
        client = self.create(x=0, connection_verify=self.get_connection_verify())
        return client

    def get_connection_verify(self):
        # Placeholder for actual implementation to get connection verification setting
        return False
