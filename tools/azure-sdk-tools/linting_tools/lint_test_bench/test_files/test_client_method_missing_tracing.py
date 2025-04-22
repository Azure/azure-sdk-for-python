# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import List
from azure.core.tracing.decorator_async import distributed_trace_async
# This code violates client-method-has-tracing-decorator
class Some2Client():

    @distributed_trace_async
    def get_thing(self, **kwargs) -> List[str]:
        return []
