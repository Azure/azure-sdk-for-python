# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import array
import base64
import hashlib
import secrets

from cryptography.hazmat.primitives.serialization import Encoding


class Utils:
    @staticmethod
    def is_little_endian():
        a = array.array("H", [1]).tobytes()
        # little endian: b'\x01\x00'
        # big endian: b'\x00\x01'
        return a[0] == 1

    @staticmethod
    def convert_to_uint16(b: bytearray):
        ret = [0 for _ in range(len(b) // 2)]
        for i in range(0, len(b), 2):
            byte_order = "little" if Utils.is_little_endian() else "big"
            ret[i // 2] = int.from_bytes(bytearray([b[i], b[i + 1]]), byteorder=byte_order, signed=False)
        return ret

    @staticmethod
    def get_random(cb):
        ret = bytearray()
        for _ in range(cb):
            ret.append(secrets.randbits(8))
        return ret

    @staticmethod
    def get_SHA256_thumbprint(cert):
        public_bytes = cert.public_bytes(Encoding.DER)
        return hashlib.sha256(public_bytes).digest()

    @staticmethod
    def security_domain_b64_url_encode_for_x5c(s):
        return base64.b64encode(s).decode("ascii")

    @staticmethod
    def security_domain_b64_url_encode(s):
        return base64.b64encode(s).decode("ascii").strip("=").replace("+", "-").replace("/", "_")


if __name__ == "__main__":
    print(Utils.convert_to_uint16(bytearray([40, 30, 20, 10])))
