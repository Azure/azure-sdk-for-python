# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Pure Cosmos property-path tokenization, shared by the wrappers."""
from typing import List


def parse_paths(paths: List[str]) -> List[str]:
    """Tokenize Cosmos paths, preserving quoted separators and escaped quotes."""
    tokens: List[str] = []
    for path in paths:
        current_index = 0
        while current_index < len(path):
            if path[current_index] != "/":
                raise ValueError(f"Invalid path character at index {current_index}")
            current_index += 1
            if current_index == len(path):
                break
            if path[current_index] in ('"', "'"):
                quote = path[current_index]
                new_index = current_index + 1
                while True:
                    new_index = path.find(quote, new_index)
                    if new_index == -1:
                        raise ValueError(f"Invalid path character at index {current_index}")
                    if path[new_index - 1] != "\\":
                        break
                    new_index += 1
                tokens.append(path[current_index + 1:new_index])
                current_index = new_index + 1
            else:
                new_index = path.find("/", current_index)
                if new_index == -1:
                    token = path[current_index:]
                    current_index = len(path)
                else:
                    token = path[current_index:new_index]
                    current_index = new_index
                tokens.append(token.strip())
    return tokens
