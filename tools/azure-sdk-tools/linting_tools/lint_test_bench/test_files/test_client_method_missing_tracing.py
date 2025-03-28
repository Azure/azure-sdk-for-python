# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import List
# This code violates client-method-missing-tracing-decoration
class Some2Client():
    def get_thing(self) -> List[str]:
        return []