# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.core.tracing.decorator import distributed_trace

# This code violates delete-operation-wrong-return-type

class MyClient():
    @distributed_trace
    def delete_some_function(self, **kwargs) -> str:
        client = kwargs.get("some_client")
        client.delete()
        # Do something with the key
        return self
