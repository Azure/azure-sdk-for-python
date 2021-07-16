# .. _persister_example:

import os
from ..serialize import serialize, deserialize


class FilesystemPersister(object):
    @classmethod
    def load_cassette(cls, cassette_path, serializer):
        try:
            with open(cassette_path) as f:
                cassette_content = f.read()
        except IOError:
            raise ValueError("Cassette not found.")
        cassette = deserialize(cassette_content, serializer)
        return cassette

    @staticmethod
    def save_cassette(cassette_path, cassette_dict, serializer):
        data = serialize(cassette_dict, serializer)
        dirname, filename = os.path.split(cassette_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(cassette_path, "w") as f:
            f.write(data)
