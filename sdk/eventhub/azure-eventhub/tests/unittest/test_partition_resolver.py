# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import ast

from azure.eventhub._buffered_producer._partition_resolver import generate_hash_code


class TestPartitionResolver:
    def test_partition_key(self):
        with open("partition-key-hashes.txt", "r") as file:
            content = file.read()
            json_arr = ast.literal_eval(content)
            for obj in json_arr:
                key = obj['Key']
                target_hash = int(obj['Hash'])
                generated_hash = int(generate_hash_code(key))
                assert target_hash == generated_hash

