# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Keep Event Hubs pyAMQP unsigned encoders aligned with Service Bus guards."""

import pytest

from azure.eventhub._pyamqp._encode import encode_uint, encode_ulong


@pytest.mark.parametrize("encoder", [encode_uint, encode_ulong])
@pytest.mark.parametrize("value", [-1, -255, -256])
def test_unsigned_encoders_reject_negative_values(encoder, value):
    with pytest.raises(ValueError, match="invalid"):
        encoder(bytearray(), value)
