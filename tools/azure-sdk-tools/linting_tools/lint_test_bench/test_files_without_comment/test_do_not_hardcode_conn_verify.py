# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

class FunctionKeywordArgumentsErrors:
    def create(self, x, connection_verify):
        if connection_verify:
            return x+1
        return x

    def run(self):
        client = self.create(connection_verify=False, x=0)
        return client
