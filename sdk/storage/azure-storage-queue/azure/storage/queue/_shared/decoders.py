import zlib


class GzipDecompressor(object):
    def __init__(self):
        self._obj = zlib.decompressobj(16 + zlib.MAX_WBITS)

    def __getattr__(self, name):
        return getattr(self._obj, name)

    def decompress(self, data):
        return self._obj.decompress(data)


class DeflateDecompressor(object):
    def __init__(self):
        self._obj = zlib.decompressobj()

    def __getattr__(self, name):
        return getattr(self._obj, name)

    def decompress(self, data):
        return self._obj.decompress(data)


class MultiDecompressor(object):
    """
    From RFC7231:
        If one or more encodings have been applied to a representation, the
        sender that applied the encodings MUST generate a Content-Encoding
        header field that lists the content codings in the order in which
        they were applied.
    """

    def __init__(self, modes):
        self._decoders = [get_decompressor(m.strip()) for m in modes.strip(",").split(",")]

    def decompress(self, data):
        for d in reversed(self._decoders):
            data = d.decompress(data)
        return data


def get_decompressor(mode):
    if "," in mode:
        return MultiDecompressor(mode)

    if mode == "gzip":
        return GzipDecompressor()

    return DeflateDecompressor()
