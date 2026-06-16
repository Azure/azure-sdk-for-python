# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

def compute(data: bytes, crc: int, /) -> int:
    """Compute Storage CRC64 over given data with given initial CRC64 value.

    :param data: The bytes data to compute the CRC64 over.
    :param crc: The initial CRC64 value.
    :returns: The computed CRC64 value.
    """
    ...

def concat(
    initial_crc_ab: int,
    initial_crc_a: int,
    final_crc_a: int,
    size_a: int,
    initial_crc_b: int,
    final_crc_b: int,
    size_b: int,
    /,
) -> int:
    """Concatenate two Storage CRC64s together.

    :param initial_crc_ab: The initial CRC64 of the combined data.
    :param initial_crc_a: The initial CRC64 of the first data segment.
    :param final_crc_a: The final CRC64 of the first data segment.
    :param size_a: The size of the first data segment in bytes.
    :param initial_crc_b: The initial CRC64 of the second data segment.
    :param final_crc_b: The final CRC64 of the second data segment.
    :param size_b: The size of the second data segment in bytes.
    :returns: The concatenated CRC64 value.
    """
    ...
