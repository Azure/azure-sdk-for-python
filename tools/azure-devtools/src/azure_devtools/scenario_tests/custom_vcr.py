# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import copy
import os

from vcr.serialize import serialize, deserialize


ATTRIBUTES_TO_COMPARE = ["body", "headers", "host", "method", "path", "protocol", "query", "scheme", "uri", "url"]


def trim_duplicates(cassette_dict):
    # Dict[str] -> Dict[str]
    cassette_copy = copy.deepcopy(cassette_dict)
    requests = cassette_dict['requests']
    responses = cassette_dict['responses']
    pairs_to_keep = []
    for i in range(1, len(requests)):
        if not same_requests(requests[i-1], requests[i]):
            pairs_to_keep.append(i)

    ret = {
        "requests": [],
        "responses": []
    }

    for p in pairs_to_keep:
        ret['requests'].append(requests[p])
        ret['responses'].append(responses[p])

    return ret


def same_requests(request1, request2):
    # (vcr.Request, vcr.Request) -> bool
    for attr in ATTRIBUTES_TO_COMPARE:
        if getattr(request1, attr) != getattr(request2, attr):
            return False

    return True


class CustomPersister(object):
    @classmethod
    def load_cassette(cls, cassette_path, serializer):
        try:
            with open(cassette_path) as f:
                cassette_content = f.read()
        except OSError:
            raise ValueError("Cassette not found.")
        cassette = deserialize(cassette_content, serializer)
        return cassette

    @staticmethod
    def save_cassette(cassette_path, cassette_dict, serializer):
        cassette_dict = trim_duplicates(cassette_dict)
        data = serialize(cassette_dict, serializer)
        dirname, filename = os.path.split(cassette_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(cassette_path, "w") as f:
            f.write(data)