# pylint: disable=line-too-long,useless-suppression
# cSpell:ignore operationid, phdr, cosesign, strea, Bignums
import math
import pytest

from azure.codetransparency.cbor import (
    CBORDecoder,
    CBOREncoder,
)

from _shared.testcase import CodeTransparencyClientTestBase


class TestCBOREncoderCoseSign1(CodeTransparencyClientTestBase):
    """Test cases for COSE_Sign1 encoding that verify round-trip with decoder."""

    def test_encode_decode_cose_sign1_roundtrip(self):
        """Test that encoding and decoding COSE_Sign1 produces consistent results."""
        # Create test data similar to what the decoder tests expect
        protected_headers = {
            1: -38,  # alg: PS384
            3: "application/spdx+json+cose-hash-v",  # content type
        }
        unprotected_headers = {}
        payload = b"test payload data"
        signature = b"test signature bytes"

        encoder = CBOREncoder()
        encoded = encoder.encode_cose_sign1(
            protected_headers=protected_headers,
            unprotected_headers=unprotected_headers,
            payload=payload,
            signature=signature,
            include_tag=True,
        )

        # Decode and verify
        decoder = CBORDecoder(encoded)
        decoded = decoder.decode_cose_sign1()

        assert decoded["protected_headers"][1] == -38
        assert decoded["protected_headers"][3] == "application/spdx+json+cose-hash-v"
        assert decoded["payload"] == payload
        assert decoded["signature"] == signature

    def test_encode_decode_alg_header(self):
        """Test encoding alg header value -38 (PS384)."""
        value = -38
        encoded = CBOREncoder.encode_value(value)
        decoded = CBORDecoder(encoded).decode()
        assert decoded == value

    def test_encode_decode_content_type_header(self):
        """Test encoding content type header string."""
        value = "application/spdx+json+cose-hash-v"
        encoded = CBOREncoder.encode_value(value)
        decoded = CBORDecoder(encoded).decode()
        assert decoded == value

    def test_encode_decode_x5t_header(self):
        """Test encoding x5t header array with algorithm and thumbprint."""
        thumbprint = bytes.fromhex(
            "c73d66092edfd7148d290d173bf0d07c4cf6b2116b32b0aef55b7cbec4cca9f4"
        )
        x5t = [-16, thumbprint]  # alg and thumbprint
        encoded = CBOREncoder.encode_value(x5t)
        decoded = CBORDecoder(encoded).decode()
        assert decoded[0] == -16
        assert decoded[1] == thumbprint

    def test_encode_decode_cwt_claims(self):
        """Test encoding CWT Claims with iss, sub, iat, and svn."""
        cwt_claims = {
            1: "did:x509:0:sha256:HnwZ4lezuxq_GVcl_Sk7YWW170qAD0DZBLXilXet0jg::eku:1.3.6.1.4.1.311.10.3.13",  # iss
            2: "test.submission-1",  # sub
            6: {"tag": 1, "value": 1741023399},  # iat (tagged epoch time)
            "svn": 2,  # svn
        }
        encoded = CBOREncoder.encode_value(cwt_claims)
        decoded = CBORDecoder(encoded).decode()

        assert (
            decoded[1]
            == "did:x509:0:sha256:HnwZ4lezuxq_GVcl_Sk7YWW170qAD0DZBLXilXet0jg::eku:1.3.6.1.4.1.311.10.3.13"
        )
        assert decoded[2] == "test.submission-1"
        assert decoded[6]["tag"] == 1
        assert decoded[6]["value"] == 1741023399
        assert decoded["svn"] == 2

    def test_encode_decode_payload_list(self):
        """Test encoding payload as list with algorithm, hash, and URL."""
        payload_data = [
            -43,
            bytes.fromhex(
                "c2a01949d2ccf9c434d6c272bb5282f129a38e8fa170b36bf3ec1d4ab577cc82231f8e9fe928a7f651b9ef9ae9323eac"
            ),
            "https://download.content-here.net",
        ]
        encoded = CBOREncoder.encode_value(payload_data)
        decoded = CBORDecoder(encoded).decode()

        assert decoded[0] == -43
        assert decoded[1] == bytes.fromhex(
            "c2a01949d2ccf9c434d6c272bb5282f129a38e8fa170b36bf3ec1d4ab577cc82231f8e9fe928a7f651b9ef9ae9323eac"
        )
        assert decoded[2] == "https://download.content-here.net"

    def test_encode_decode_protected_headers_map(self):
        """Test encoding complete protected headers map."""
        thumbprint = bytes.fromhex(
            "c73d66092edfd7148d290d173bf0d07c4cf6b2116b32b0aef55b7cbec4cca9f4"
        )
        protected_headers = {
            1: -38,  # alg
            3: "application/spdx+json+cose-hash-v",  # content type
            34: [-16, thumbprint],  # x5t
        }
        encoded = CBOREncoder.encode_value(protected_headers)
        decoded = CBORDecoder(encoded).decode()

        assert decoded[1] == -38
        assert decoded[3] == "application/spdx+json+cose-hash-v"
        assert decoded[34][0] == -16
        assert decoded[34][1] == thumbprint

    def test_encode_cose_sign1_without_tag(self):
        """Test encoding COSE_Sign1 without the tag 18."""
        encoder = CBOREncoder()
        encoded = encoder.encode_cose_sign1(
            protected_headers={1: -7},
            unprotected_headers={},
            payload=b"payload",
            signature=b"sig",
            include_tag=False,
        )

        # Should decode as a plain array, not a tagged structure
        decoder = CBORDecoder(encoded)
        decoded = decoder.decode()
        assert isinstance(decoded, list)
        assert len(decoded) == 4

    def test_encode_decode_tag_18(self):
        """Test encoding and decoding tag 18 (COSE_Sign1 tag)."""
        tagged_value = {"tag": 18, "value": [b"", {}, b"payload", b"sig"]}
        encoded = CBOREncoder.encode_value(tagged_value)
        decoded = CBORDecoder(encoded).decode()

        assert decoded["tag"] == 18
        assert decoded["value"] == [b"", {}, b"payload", b"sig"]


class TestCBOREncoderRFC8949AppendixA(CodeTransparencyClientTestBase):
    """Test cases based on RFC 8949 Appendix A examples.

    These tests verify that the CBOREncoder correctly encodes values
    and that the encoded bytes can be decoded back to the original value.
    """

    # =========================================================================
    # Unsigned Integers (Major Type 0)
    # =========================================================================

    def test_unsigned_integer_0(self):
        """RFC 8949 Appendix A: 0 -> 0x00"""
        encoded = CBOREncoder.encode_value(0)
        assert encoded == bytes.fromhex("00")
        assert CBORDecoder(encoded).decode() == 0

    def test_unsigned_integer_1(self):
        """RFC 8949 Appendix A: 1 -> 0x01"""
        encoded = CBOREncoder.encode_value(1)
        assert encoded == bytes.fromhex("01")
        assert CBORDecoder(encoded).decode() == 1

    def test_unsigned_integer_10(self):
        """RFC 8949 Appendix A: 10 -> 0x0a"""
        encoded = CBOREncoder.encode_value(10)
        assert encoded == bytes.fromhex("0a")
        assert CBORDecoder(encoded).decode() == 10

    def test_unsigned_integer_23(self):
        """RFC 8949 Appendix A: 23 -> 0x17"""
        encoded = CBOREncoder.encode_value(23)
        assert encoded == bytes.fromhex("17")
        assert CBORDecoder(encoded).decode() == 23

    def test_unsigned_integer_24(self):
        """RFC 8949 Appendix A: 24 -> 0x1818"""
        encoded = CBOREncoder.encode_value(24)
        assert encoded == bytes.fromhex("1818")
        assert CBORDecoder(encoded).decode() == 24

    def test_unsigned_integer_25(self):
        """RFC 8949 Appendix A: 25 -> 0x1819"""
        encoded = CBOREncoder.encode_value(25)
        assert encoded == bytes.fromhex("1819")
        assert CBORDecoder(encoded).decode() == 25

    def test_unsigned_integer_100(self):
        """RFC 8949 Appendix A: 100 -> 0x1864"""
        encoded = CBOREncoder.encode_value(100)
        assert encoded == bytes.fromhex("1864")
        assert CBORDecoder(encoded).decode() == 100

    def test_unsigned_integer_1000(self):
        """RFC 8949 Appendix A: 1000 -> 0x1903e8"""
        encoded = CBOREncoder.encode_value(1000)
        assert encoded == bytes.fromhex("1903e8")
        assert CBORDecoder(encoded).decode() == 1000

    def test_unsigned_integer_1000000(self):
        """RFC 8949 Appendix A: 1000000 -> 0x1a000f4240"""
        encoded = CBOREncoder.encode_value(1000000)
        assert encoded == bytes.fromhex("1a000f4240")
        assert CBORDecoder(encoded).decode() == 1000000

    def test_unsigned_integer_1000000000000(self):
        """RFC 8949 Appendix A: 1000000000000 -> 0x1b000000e8d4a51000"""
        encoded = CBOREncoder.encode_value(1000000000000)
        assert encoded == bytes.fromhex("1b000000e8d4a51000")
        assert CBORDecoder(encoded).decode() == 1000000000000

    def test_unsigned_integer_max_uint64(self):
        """RFC 8949 Appendix A: 18446744073709551615 -> 0x1bffffffffffffffff"""
        encoded = CBOREncoder.encode_value(18446744073709551615)
        assert encoded == bytes.fromhex("1bffffffffffffffff")
        assert CBORDecoder(encoded).decode() == 18446744073709551615

    # =========================================================================
    # Negative Integers (Major Type 1)
    # =========================================================================

    def test_negative_integer_minus_1(self):
        """RFC 8949 Appendix A: -1 -> 0x20"""
        encoded = CBOREncoder.encode_value(-1)
        assert encoded == bytes.fromhex("20")
        assert CBORDecoder(encoded).decode() == -1

    def test_negative_integer_minus_10(self):
        """RFC 8949 Appendix A: -10 -> 0x29"""
        encoded = CBOREncoder.encode_value(-10)
        assert encoded == bytes.fromhex("29")
        assert CBORDecoder(encoded).decode() == -10

    def test_negative_integer_minus_100(self):
        """RFC 8949 Appendix A: -100 -> 0x3863"""
        encoded = CBOREncoder.encode_value(-100)
        assert encoded == bytes.fromhex("3863")
        assert CBORDecoder(encoded).decode() == -100

    def test_negative_integer_minus_1000(self):
        """RFC 8949 Appendix A: -1000 -> 0x3903e7"""
        encoded = CBOREncoder.encode_value(-1000)
        assert encoded == bytes.fromhex("3903e7")
        assert CBORDecoder(encoded).decode() == -1000

    def test_negative_integer_minus_max_uint64_minus_1(self):
        """RFC 8949 Appendix A: -18446744073709551616 -> 0x3bffffffffffffffff"""
        encoded = CBOREncoder.encode_value(-18446744073709551616)
        assert encoded == bytes.fromhex("3bffffffffffffffff")
        assert CBORDecoder(encoded).decode() == -18446744073709551616

    # =========================================================================
    # Floating-Point Numbers (Major Type 7)
    # =========================================================================

    def test_float_0_0(self):
        """RFC 8949 Appendix A: 0.0 -> half precision"""
        encoded = CBOREncoder.encode_value(0.0)
        # Should encode as half-precision 0xf90000
        assert encoded == bytes.fromhex("f90000")
        assert CBORDecoder(encoded).decode() == 0.0

    def test_float_1_0(self):
        """RFC 8949 Appendix A: 1.0 -> half precision"""
        encoded = CBOREncoder.encode_value(1.0)
        # Should encode as half-precision 0xf93c00
        assert encoded == bytes.fromhex("f93c00")
        assert CBORDecoder(encoded).decode() == 1.0

    def test_float_1_5(self):
        """RFC 8949 Appendix A: 1.5 -> half precision"""
        encoded = CBOREncoder.encode_value(1.5)
        # Should encode as half-precision 0xf93e00
        assert encoded == bytes.fromhex("f93e00")
        assert CBORDecoder(encoded).decode() == 1.5

    def test_float_65504_0(self):
        """RFC 8949 Appendix A: 65504.0 -> half precision (max finite half)"""
        encoded = CBOREncoder.encode_value(65504.0)
        # Should encode as half-precision 0xf97bff
        assert encoded == bytes.fromhex("f97bff")
        assert CBORDecoder(encoded).decode() == 65504.0

    def test_float_100000_0(self):
        """RFC 8949 Appendix A: 100000.0 -> single precision"""
        encoded = CBOREncoder.encode_value(100000.0)
        # Should encode as single-precision 0xfa47c35000
        assert encoded == bytes.fromhex("fa47c35000")
        assert CBORDecoder(encoded).decode() == 100000.0

    def test_float_1_1_roundtrip(self):
        """Test 1.1 round-trip (requires double precision)."""
        encoded = CBOREncoder.encode_value(1.1)
        decoded = CBORDecoder(encoded).decode()
        assert abs(decoded - 1.1) < 1e-15

    def test_float_minus_4_0(self):
        """RFC 8949 Appendix A: -4.0 -> half precision"""
        encoded = CBOREncoder.encode_value(-4.0)
        # Should encode as half-precision 0xf9c400
        assert encoded == bytes.fromhex("f9c400")
        assert CBORDecoder(encoded).decode() == -4.0

    def test_float_infinity(self):
        """RFC 8949 Appendix A: Infinity -> half precision"""
        encoded = CBOREncoder.encode_value(float("inf"))
        # Should encode as half-precision infinity 0xf97c00
        assert encoded == bytes.fromhex("f97c00")
        assert CBORDecoder(encoded).decode() == float("inf")

    def test_float_minus_infinity(self):
        """RFC 8949 Appendix A: -Infinity -> half precision"""
        encoded = CBOREncoder.encode_value(float("-inf"))
        # Should encode as half-precision -infinity 0xf9fc00
        assert encoded == bytes.fromhex("f9fc00")
        assert CBORDecoder(encoded).decode() == float("-inf")

    def test_float_nan(self):
        """RFC 8949 Appendix A: NaN -> half precision"""
        encoded = CBOREncoder.encode_value(float("nan"))
        # Should encode as half-precision NaN 0xf97e00
        assert encoded == bytes.fromhex("f97e00")
        assert math.isnan(CBORDecoder(encoded).decode())

    def test_float_roundtrip_various(self):
        """Test various float values round-trip correctly."""
        test_values = [0.5, 2.0, -0.5, 256.0, 0.00006103515625]
        for value in test_values:
            encoded = CBOREncoder.encode_value(value)
            decoded = CBORDecoder(encoded).decode()
            assert decoded == value, f"Round-trip failed for {value}"

    # =========================================================================
    # Simple Values (Major Type 7)
    # =========================================================================

    def test_simple_false(self):
        """RFC 8949 Appendix A: false -> 0xf4"""
        encoded = CBOREncoder.encode_value(False)
        assert encoded == bytes.fromhex("f4")
        assert CBORDecoder(encoded).decode() is False

    def test_simple_true(self):
        """RFC 8949 Appendix A: true -> 0xf5"""
        encoded = CBOREncoder.encode_value(True)
        assert encoded == bytes.fromhex("f5")
        assert CBORDecoder(encoded).decode() is True

    def test_simple_null(self):
        """RFC 8949 Appendix A: null -> 0xf6"""
        encoded = CBOREncoder.encode_value(None)
        assert encoded == bytes.fromhex("f6")
        assert CBORDecoder(encoded).decode() is None

    def test_simple_undefined(self):
        """RFC 8949 Appendix A: undefined -> 0xf7"""
        encoded = CBOREncoder.encode_value({"undefined": True})
        assert encoded == bytes.fromhex("f7")
        assert CBORDecoder(encoded).decode() == {"undefined": True}

    def test_simple_16(self):
        """RFC 8949 Appendix A: simple(16) -> 0xf0"""
        encoded = CBOREncoder.encode_value({"simple": 16})
        assert encoded == bytes.fromhex("f0")
        assert CBORDecoder(encoded).decode() == {"simple": 16}

    def test_simple_255(self):
        """RFC 8949 Appendix A: simple(255) -> 0xf8ff"""
        encoded = CBOREncoder.encode_value({"simple": 255})
        assert encoded == bytes.fromhex("f8ff")
        assert CBORDecoder(encoded).decode() == {"simple": 255}

    # =========================================================================
    # Byte Strings (Major Type 2)
    # =========================================================================

    def test_byte_string_empty(self):
        """RFC 8949 Appendix A: h'' -> 0x40"""
        encoded = CBOREncoder.encode_value(b"")
        assert encoded == bytes.fromhex("40")
        assert CBORDecoder(encoded).decode() == b""

    def test_byte_string_4_bytes(self):
        """RFC 8949 Appendix A: h'01020304' -> 0x4401020304"""
        encoded = CBOREncoder.encode_value(bytes.fromhex("01020304"))
        assert encoded == bytes.fromhex("4401020304")
        assert CBORDecoder(encoded).decode() == bytes.fromhex("01020304")

    def test_byte_string_long(self):
        """Test encoding longer byte strings."""
        data = bytes(range(256))
        encoded = CBOREncoder.encode_value(data)
        decoded = CBORDecoder(encoded).decode()
        assert decoded == data

    # =========================================================================
    # Text Strings (Major Type 3)
    # =========================================================================

    def test_text_string_empty(self):
        """RFC 8949 Appendix A: "" -> 0x60"""
        encoded = CBOREncoder.encode_value("")
        assert encoded == bytes.fromhex("60")
        assert CBORDecoder(encoded).decode() == ""

    def test_text_string_a(self):
        """RFC 8949 Appendix A: "a" -> 0x6161"""
        encoded = CBOREncoder.encode_value("a")
        assert encoded == bytes.fromhex("6161")
        assert CBORDecoder(encoded).decode() == "a"

    def test_text_string_IETF(self):
        """RFC 8949 Appendix A: "IETF" -> 0x6449455446"""
        encoded = CBOREncoder.encode_value("IETF")
        assert encoded == bytes.fromhex("6449455446")
        assert CBORDecoder(encoded).decode() == "IETF"

    def test_text_string_escaped_chars(self):
        r"""RFC 8949 Appendix A: "\"\\" -> 0x62225c"""
        encoded = CBOREncoder.encode_value('"\\')
        assert encoded == bytes.fromhex("62225c")
        assert CBORDecoder(encoded).decode() == '"\\'

    def test_text_string_unicode_u00fc(self):
        """RFC 8949 Appendix A: "ü" (U+00FC) -> 0x62c3bc"""
        encoded = CBOREncoder.encode_value("\u00fc")
        assert encoded == bytes.fromhex("62c3bc")
        assert CBORDecoder(encoded).decode() == "\u00fc"

    def test_text_string_unicode_u6c34(self):
        """RFC 8949 Appendix A: "水" (U+6C34) -> 0x63e6b0b4"""
        encoded = CBOREncoder.encode_value("\u6c34")
        assert encoded == bytes.fromhex("63e6b0b4")
        assert CBORDecoder(encoded).decode() == "\u6c34"

    def test_text_string_unicode_u10151(self):
        """RFC 8949 Appendix A: "𐅑" (U+10151) -> 0x64f0908591"""
        encoded = CBOREncoder.encode_value("\U00010151")
        assert encoded == bytes.fromhex("64f0908591")
        assert CBORDecoder(encoded).decode() == "\U00010151"

    # =========================================================================
    # Arrays (Major Type 4)
    # =========================================================================

    def test_array_empty(self):
        """RFC 8949 Appendix A: [] -> 0x80"""
        encoded = CBOREncoder.encode_value([])
        assert encoded == bytes.fromhex("80")
        assert CBORDecoder(encoded).decode() == []

    def test_array_1_2_3(self):
        """RFC 8949 Appendix A: [1, 2, 3] -> 0x83010203"""
        encoded = CBOREncoder.encode_value([1, 2, 3])
        assert encoded == bytes.fromhex("83010203")
        assert CBORDecoder(encoded).decode() == [1, 2, 3]

    def test_array_nested(self):
        """RFC 8949 Appendix A: [1, [2, 3], [4, 5]] -> 0x8301820203820405"""
        encoded = CBOREncoder.encode_value([1, [2, 3], [4, 5]])
        assert encoded == bytes.fromhex("8301820203820405")
        assert CBORDecoder(encoded).decode() == [1, [2, 3], [4, 5]]

    def test_array_25_elements(self):
        """RFC 8949 Appendix A: [1..25] -> 0x98190102...181819"""
        value = list(range(1, 26))
        encoded = CBOREncoder.encode_value(value)
        assert encoded == bytes.fromhex(
            "98190102030405060708090a0b0c0d0e0f101112131415161718181819"
        )
        assert CBORDecoder(encoded).decode() == value

    def test_tuple_encoding(self):
        """Test that tuples are encoded as arrays."""
        encoded = CBOREncoder.encode_value((1, 2, 3))
        assert encoded == bytes.fromhex("83010203")
        assert CBORDecoder(encoded).decode() == [1, 2, 3]

    # =========================================================================
    # Maps (Major Type 5)
    # =========================================================================

    def test_map_empty(self):
        """RFC 8949 Appendix A: {} -> 0xa0"""
        encoded = CBOREncoder.encode_value({})
        assert encoded == bytes.fromhex("a0")
        assert CBORDecoder(encoded).decode() == {}

    def test_map_1_2_3_4(self):
        """RFC 8949 Appendix A: {1: 2, 3: 4} -> 0xa201020304"""
        encoded = CBOREncoder.encode_value({1: 2, 3: 4})
        assert encoded == bytes.fromhex("a201020304")
        assert CBORDecoder(encoded).decode() == {1: 2, 3: 4}

    def test_map_with_strings_and_arrays(self):
        """RFC 8949 Appendix A: {"a": 1, "b": [2, 3]} -> 0xa26161016162820203"""
        encoded = CBOREncoder.encode_value({"a": 1, "b": [2, 3]})
        assert encoded == bytes.fromhex("a26161016162820203")
        assert CBORDecoder(encoded).decode() == {"a": 1, "b": [2, 3]}

    def test_array_with_map(self):
        """RFC 8949 Appendix A: ["a", {"b": "c"}] -> 0x826161a161626163"""
        encoded = CBOREncoder.encode_value(["a", {"b": "c"}])
        assert encoded == bytes.fromhex("826161a161626163")
        assert CBORDecoder(encoded).decode() == ["a", {"b": "c"}]

    def test_map_5_pairs(self):
        """RFC 8949 Appendix A: {"a": "A", "b": "B", "c": "C", "d": "D", "e": "E"}"""
        value = {"a": "A", "b": "B", "c": "C", "d": "D", "e": "E"}
        encoded = CBOREncoder.encode_value(value)
        assert encoded == bytes.fromhex("a56161614161626142616361436164614461656145")
        assert CBORDecoder(encoded).decode() == value

    # =========================================================================
    # Tags (Major Type 6)
    # =========================================================================

    def test_tag_0_datetime_string(self):
        """RFC 8949 Appendix A: 0("2013-03-21T20:04:00Z") -> 0xc074..."""
        value = {"tag": 0, "value": "2013-03-21T20:04:00Z"}
        encoded = CBOREncoder.encode_value(value)
        assert encoded == bytes.fromhex("c074323031332d30332d32315432303a30343a30305a")
        decoded = CBORDecoder(encoded).decode()
        assert decoded == value

    def test_tag_1_epoch_time(self):
        """RFC 8949 Appendix A: 1(1363896240) -> 0xc11a514b67b0"""
        value = {"tag": 1, "value": 1363896240}
        encoded = CBOREncoder.encode_value(value)
        assert encoded == bytes.fromhex("c11a514b67b0")
        decoded = CBORDecoder(encoded).decode()
        assert decoded == value

    def test_tag_23_base16_hint(self):
        """RFC 8949 Appendix A: 23(h'01020304') -> 0xd74401020304"""
        value = {"tag": 23, "value": bytes.fromhex("01020304")}
        encoded = CBOREncoder.encode_value(value)
        assert encoded == bytes.fromhex("d74401020304")
        decoded = CBORDecoder(encoded).decode()
        assert decoded == value

    def test_tag_24_encoded_cbor(self):
        """RFC 8949 Appendix A: 24(h'6449455446') -> 0xd818456449455446"""
        value = {"tag": 24, "value": bytes.fromhex("6449455446")}
        encoded = CBOREncoder.encode_value(value)
        assert encoded == bytes.fromhex("d818456449455446")
        decoded = CBORDecoder(encoded).decode()
        assert decoded == value

    def test_tag_32_uri(self):
        """RFC 8949 Appendix A: 32("http://www.example.com") -> 0xd82076..."""
        value = {"tag": 32, "value": "http://www.example.com"}
        encoded = CBOREncoder.encode_value(value)
        assert encoded == bytes.fromhex(
            "d82076687474703a2f2f7777772e6578616d706c652e636f6d"
        )
        decoded = CBORDecoder(encoded).decode()
        assert decoded == value

    # =========================================================================
    # Indefinite-Length Items
    # =========================================================================

    def test_indefinite_byte_string(self):
        """Test encoding indefinite-length byte string."""
        encoder = CBOREncoder()
        encoded = encoder.encode_indefinite_bytes(
            [bytes.fromhex("0102"), bytes.fromhex("030405")]
        )
        assert encoded == bytes.fromhex("5f42010243030405ff")
        decoded = CBORDecoder(encoded).decode()
        assert decoded == bytes.fromhex("0102030405")

    def test_indefinite_text_string(self):
        """Test encoding indefinite-length text string."""
        encoder = CBOREncoder()
        encoded = encoder.encode_indefinite_string(["strea", "ming"])
        assert encoded == bytes.fromhex("7f657374726561646d696e67ff")
        decoded = CBORDecoder(encoded).decode()
        assert decoded == "streaming"

    def test_indefinite_array_empty(self):
        """Test encoding empty indefinite-length array."""
        encoder = CBOREncoder()
        encoded = encoder.encode_indefinite_array([])
        assert encoded == bytes.fromhex("9fff")
        decoded = CBORDecoder(encoded).decode()
        assert decoded == []

    def test_indefinite_array(self):
        """Test encoding indefinite-length array."""
        encoder = CBOREncoder()
        encoded = encoder.encode_indefinite_array([1, 2, 3])
        # Verify it decodes correctly
        decoded = CBORDecoder(encoded).decode()
        assert decoded == [1, 2, 3]

    def test_indefinite_map(self):
        """Test encoding indefinite-length map."""
        encoder = CBOREncoder()
        encoded = encoder.encode_indefinite_map({"Fun": True, "Amt": -2})
        # Verify it decodes correctly
        decoded = CBORDecoder(encoded).decode()
        assert decoded == {"Fun": True, "Amt": -2}


class TestCBOREncoderBignums(CodeTransparencyClientTestBase):
    """Test cases for bignum encoding (RFC 8949 Appendix A)."""

    def test_bignum_positive_tag(self):
        """Test encoding positive bignum with tag 2."""
        value = {"tag": 2, "value": bytes.fromhex("010000000000000000")}
        encoded = CBOREncoder.encode_value(value)
        assert encoded == bytes.fromhex("c249010000000000000000")
        decoded = CBORDecoder(encoded).decode()
        assert decoded["tag"] == 2
        assert decoded["value"] == bytes.fromhex("010000000000000000")

    def test_bignum_negative_tag(self):
        """Test encoding negative bignum with tag 3."""
        value = {"tag": 3, "value": bytes.fromhex("010000000000000000")}
        encoded = CBOREncoder.encode_value(value)
        assert encoded == bytes.fromhex("c349010000000000000000")
        decoded = CBORDecoder(encoded).decode()
        assert decoded["tag"] == 3
        assert decoded["value"] == bytes.fromhex("010000000000000000")


class TestCBOREncoderEdgeCases(CodeTransparencyClientTestBase):
    """Edge case tests for CBOREncoder."""

    def test_encode_integer_too_large(self):
        """Test that encoding integers larger than uint64 raises ValueError."""
        with pytest.raises(ValueError, match="Integer too large to encode"):
            CBOREncoder.encode_value(2**64)

    def test_encode_negative_integer_too_large(self):
        """Test encoding very large negative integers."""
        # -2^64 - 1 should fail
        with pytest.raises(ValueError, match="Integer too large to encode"):
            CBOREncoder.encode_value(-(2**64) - 1)

    def test_encode_unsupported_type(self):
        """Test that encoding unsupported types raises ValueError."""
        with pytest.raises(ValueError, match="Cannot encode type"):
            CBOREncoder.encode_value(object())

    def test_encode_negative_tag(self):
        """Test that encoding negative tag numbers raises ValueError."""
        with pytest.raises(ValueError, match="Tag number must be non-negative"):
            CBOREncoder.encode_value({"tag": -1, "value": "test"})

    def test_encode_simple_value_out_of_range(self):
        """Test that simple values outside 0-255 raise ValueError."""
        encoder = CBOREncoder()
        with pytest.raises(ValueError, match="Simple value must be 0-255"):
            encoder._encode_simple(256)
        with pytest.raises(ValueError, match="Simple value must be 0-255"):
            encoder._encode_simple(-1)

    def test_roundtrip_complex_nested_structure(self):
        """Test round-trip of a complex nested structure."""
        value = {
            "integers": [0, 1, -1, 255, 256, 65535, 65536, -100],
            "floats": [0.0, 1.0, -1.5, float("inf")],
            "strings": ["", "hello", "\u6c34", "test\nwith\nnewlines"],
            "bytes": [b"", b"\x00\x01\x02", bytes(range(100))],
            "bools": [True, False],
            "null": None,
            "nested": {"a": {"b": {"c": [1, 2, 3]}}},
            "tagged": {"tag": 1, "value": 1234567890},
        }
        encoded = CBOREncoder.encode_value(value)
        decoded = CBORDecoder(encoded).decode()
        assert decoded == value

    def test_static_method(self):
        """Test the static encode_value method."""
        encoded = CBOREncoder.encode_value(42)
        assert encoded == bytes.fromhex("182a")
        assert CBORDecoder(encoded).decode() == 42

    def test_instance_reuse(self):
        """Test that encoder instance can be reused."""
        encoder = CBOREncoder()
        encoded1 = encoder.encode({"a": 1})
        encoded2 = encoder.encode({"b": 2})
        assert CBORDecoder(encoded1).decode() == {"a": 1}
        assert CBORDecoder(encoded2).decode() == {"b": 2}
