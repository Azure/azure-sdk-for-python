def bytes_to_long(bytes):
    assert len(bytes) == 8
    return sum((b << (k * 8) for k, b in enumerate(bytes)))


def murmur64(data, seed=0):

    m = 0xc6a4a7935bd1e995
    r = 47

    MASK = 2 ** 64 - 1

    try:
        data_as_bytes = bytearray(data)
    except TypeError:
        data_as_bytes = bytearray(data, 'utf-8')

    h = seed ^ ((m * len(data_as_bytes)) & MASK)

    offset = int(len(data_as_bytes)/8)*8
    for ll in range(0, offset, 8):
        k = bytes_to_long(data_as_bytes[ll:ll + 8])
        k = (k * m) & MASK
        k = k ^ ((k >> r) & MASK)
        k = (k * m) & MASK
        h = (h ^ k)
        h = (h * m) & MASK

    l = len(data_as_bytes) & 7

    if l >= 7:
        h = (h ^ (data_as_bytes[offset+6] << 48))

    if l >= 6:
        h = (h ^ (data_as_bytes[offset+5] << 40))

    if l >= 5:
        h = (h ^ (data_as_bytes[offset+4] << 32))

    if l >= 4:
        h = (h ^ (data_as_bytes[offset+3] << 24))

    if l >= 3:
        h = (h ^ (data_as_bytes[offset+2] << 16))

    if l >= 2:
        h = (h ^ (data_as_bytes[offset+1] << 8))

    if l >= 1:
        h = (h ^ data_as_bytes[offset])
        h = (h * m) & MASK

    h = h ^ ((h >> r) & MASK)
    h = (h * m) & MASK
    h = h ^ ((h >> r) & MASK)

    # Cosmos implementation - reverse the final result
    h = int(str(h)[::-1])

    return h
