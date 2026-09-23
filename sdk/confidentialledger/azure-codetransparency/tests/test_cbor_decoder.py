# pylint: disable=line-too-long,useless-suppression
# cSpell:ignore operationid, phdr, cosesign, strea, Bignums
import math
import pytest

from azure.codetransparency.cbor import (
    CBORDecoder,
)

from _shared.testcase import CodeTransparencyClientTestBase


class TestCBORDecoderCoseSign1(CodeTransparencyClientTestBase):
    def create_valid_cose_sign1(self) -> bytes:
        import base64

        b64_sign1 = "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"
        return base64.b64decode(b64_sign1)

    def test_decode_cbor_cosesign1(self, **kwargs):
        cose_message = self.create_valid_cose_sign1()
        decoder = CBORDecoder(cose_message)
        decoded = decoder.decode_cose_sign1()
        phdr = decoded.get("protected_headers", {})

        # verify that alg header matches PS384
        alg = phdr.get(1, 0)
        assert alg == -38, f"Unexpected header value: {alg}"

        # verify content type header
        content_type = phdr.get(3, "")
        assert (
            content_type == "application/spdx+json+cose-hash-v"
        ), f"Unexpected header value: {content_type}"

        # verify x5t header
        x5t = phdr.get(34, list())
        # alg == -16
        assert x5t[0] == -16, f"Unexpected x5t value: {x5t}"
        # second element is a bytestring of the thumbprint which is c73d66092edfd7148d290d173bf0d07c4cf6b2116b32b0aef55b7cbec4cca9f4
        thumbprint = x5t[1]
        expected_thumbprint = bytes.fromhex(
            "c73d66092edfd7148d290d173bf0d07c4cf6b2116b32b0aef55b7cbec4cca9f4"
        )
        assert (
            thumbprint == expected_thumbprint
        ), f"Unexpected thumbprint value: {thumbprint.hex()}"

        # verify CWT Claims header (15) contains keys: iss (1), sub (2), iat (6), svn ("svn")

        cwt_claims = phdr.get(15, {})
        iss = cwt_claims.get(1, "")
        assert (
            iss
            == "did:x509:0:sha256:HnwZ4lezuxq_GVcl_Sk7YWW170qAD0DZBLXilXet0jg::eku:1.3.6.1.4.1.311.10.3.13"
        ), f"Unexpected iss value: {iss}"

        sub = cwt_claims.get(2, "")
        assert sub == "test.submission-1", f"Unexpected sub value: {sub}"

        iat = cwt_claims.get(6, 0)
        assert iat.get("value") == 1741023399, f"Unexpected iat value: {iat}"

        svn = cwt_claims.get("svn", 0)
        assert svn == 2, f"Unexpected svn value: {svn}"

        # verify payload is bytes and can be decoded as cbor
        payload = decoded.get("payload", b"")
        assert isinstance(payload, bytes), "Payload is not bytes"
        payload_decoder = CBORDecoder(payload)
        payload_decoded = payload_decoder.decode()
        # verify payload is a list with 3 elements -43, c2a01949d2ccf9c434d6c272bb5282f129a38e8fa170b36bf3ec1d4ab577cc82231f8e9fe928a7f651b9ef9ae9323eac, https://download.content-here.net
        assert isinstance(payload_decoded, list), "Payload is not a list"
        assert (
            len(payload_decoded) == 3
        ), f"Unexpected payload length: {len(payload_decoded)}"
        assert (
            payload_decoded[0] == -43
        ), f"Unexpected payload[0] value: {payload_decoded[0]}"
        assert payload_decoded[1] == bytes.fromhex(
            "c2a01949d2ccf9c434d6c272bb5282f129a38e8fa170b36bf3ec1d4ab577cc82231f8e9fe928a7f651b9ef9ae9323eac"
        ), f"Unexpected payload[1] value: {payload_decoded[1].hex()}"
        assert (
            payload_decoded[2] == "https://download.content-here.net"
        ), f"Unexpected payload[2] value: {payload_decoded[2]}"


class TestCBORDecoderRFC8949AppendixA(CodeTransparencyClientTestBase):
    """Test cases based on RFC 8949 Appendix A examples.

    These tests verify that the CBORDecoder correctly decodes all examples
    from the CBOR specification (RFC 8949) Appendix A.
    """

    # =========================================================================
    # Unsigned Integers (Major Type 0)
    # =========================================================================

    def test_unsigned_integer_0(self):
        """RFC 8949 Appendix A: 0 -> 0x00"""
        decoder = CBORDecoder(bytes.fromhex("00"))
        assert decoder.decode() == 0

    def test_unsigned_integer_1(self):
        """RFC 8949 Appendix A: 1 -> 0x01"""
        decoder = CBORDecoder(bytes.fromhex("01"))
        assert decoder.decode() == 1

    def test_unsigned_integer_10(self):
        """RFC 8949 Appendix A: 10 -> 0x0a"""
        decoder = CBORDecoder(bytes.fromhex("0a"))
        assert decoder.decode() == 10

    def test_unsigned_integer_23(self):
        """RFC 8949 Appendix A: 23 -> 0x17"""
        decoder = CBORDecoder(bytes.fromhex("17"))
        assert decoder.decode() == 23

    def test_unsigned_integer_24(self):
        """RFC 8949 Appendix A: 24 -> 0x1818"""
        decoder = CBORDecoder(bytes.fromhex("1818"))
        assert decoder.decode() == 24

    def test_unsigned_integer_25(self):
        """RFC 8949 Appendix A: 25 -> 0x1819"""
        decoder = CBORDecoder(bytes.fromhex("1819"))
        assert decoder.decode() == 25

    def test_unsigned_integer_100(self):
        """RFC 8949 Appendix A: 100 -> 0x1864"""
        decoder = CBORDecoder(bytes.fromhex("1864"))
        assert decoder.decode() == 100

    def test_unsigned_integer_1000(self):
        """RFC 8949 Appendix A: 1000 -> 0x1903e8"""
        decoder = CBORDecoder(bytes.fromhex("1903e8"))
        assert decoder.decode() == 1000

    def test_unsigned_integer_1000000(self):
        """RFC 8949 Appendix A: 1000000 -> 0x1a000f4240"""
        decoder = CBORDecoder(bytes.fromhex("1a000f4240"))
        assert decoder.decode() == 1000000

    def test_unsigned_integer_1000000000000(self):
        """RFC 8949 Appendix A: 1000000000000 -> 0x1b000000e8d4a51000"""
        decoder = CBORDecoder(bytes.fromhex("1b000000e8d4a51000"))
        assert decoder.decode() == 1000000000000

    def test_unsigned_integer_max_uint64(self):
        """RFC 8949 Appendix A: 18446744073709551615 -> 0x1bffffffffffffffff"""
        decoder = CBORDecoder(bytes.fromhex("1bffffffffffffffff"))
        assert decoder.decode() == 18446744073709551615

    # =========================================================================
    # Negative Integers (Major Type 1)
    # =========================================================================

    def test_negative_integer_minus_1(self):
        """RFC 8949 Appendix A: -1 -> 0x20"""
        decoder = CBORDecoder(bytes.fromhex("20"))
        assert decoder.decode() == -1

    def test_negative_integer_minus_10(self):
        """RFC 8949 Appendix A: -10 -> 0x29"""
        decoder = CBORDecoder(bytes.fromhex("29"))
        assert decoder.decode() == -10

    def test_negative_integer_minus_100(self):
        """RFC 8949 Appendix A: -100 -> 0x3863"""
        decoder = CBORDecoder(bytes.fromhex("3863"))
        assert decoder.decode() == -100

    def test_negative_integer_minus_1000(self):
        """RFC 8949 Appendix A: -1000 -> 0x3903e7"""
        decoder = CBORDecoder(bytes.fromhex("3903e7"))
        assert decoder.decode() == -1000

    def test_negative_integer_minus_max_uint64_minus_1(self):
        """RFC 8949 Appendix A: -18446744073709551616 -> 0x3bffffffffffffffff"""
        decoder = CBORDecoder(bytes.fromhex("3bffffffffffffffff"))
        assert decoder.decode() == -18446744073709551616

    # =========================================================================
    # Floating-Point Numbers (Major Type 7)
    # =========================================================================

    def test_float_0_0(self):
        """RFC 8949 Appendix A: 0.0 -> 0xf90000"""
        decoder = CBORDecoder(bytes.fromhex("f90000"))
        assert decoder.decode() == 0.0

    def test_float_minus_0_0(self):
        """RFC 8949 Appendix A: -0.0 -> 0xf98000"""
        decoder = CBORDecoder(bytes.fromhex("f98000"))
        result = decoder.decode()
        assert result == 0.0
        assert math.copysign(1, result) == -1  # Verify it's negative zero

    def test_float_1_0(self):
        """RFC 8949 Appendix A: 1.0 -> 0xf93c00"""
        decoder = CBORDecoder(bytes.fromhex("f93c00"))
        assert decoder.decode() == 1.0

    def test_float_1_1(self):
        """RFC 8949 Appendix A: 1.1 -> 0xfb3ff199999999999a (double)"""
        decoder = CBORDecoder(bytes.fromhex("fb3ff199999999999a"))
        assert abs(decoder.decode() - 1.1) < 1e-15

    def test_float_1_5(self):
        """RFC 8949 Appendix A: 1.5 -> 0xf93e00"""
        decoder = CBORDecoder(bytes.fromhex("f93e00"))
        assert decoder.decode() == 1.5

    def test_float_65504_0(self):
        """RFC 8949 Appendix A: 65504.0 -> 0xf97bff"""
        decoder = CBORDecoder(bytes.fromhex("f97bff"))
        assert decoder.decode() == 65504.0

    def test_float_100000_0(self):
        """RFC 8949 Appendix A: 100000.0 -> 0xfa47c35000 (single)"""
        decoder = CBORDecoder(bytes.fromhex("fa47c35000"))
        assert decoder.decode() == 100000.0

    def test_float_max_single(self):
        """RFC 8949 Appendix A: 3.4028234663852886e+38 -> 0xfa7f7fffff"""
        decoder = CBORDecoder(bytes.fromhex("fa7f7fffff"))
        assert abs(decoder.decode() - 3.4028234663852886e38) < 1e32

    def test_float_1e300(self):
        """RFC 8949 Appendix A: 1.0e+300 -> 0xfb7e37e43c8800759c"""
        decoder = CBORDecoder(bytes.fromhex("fb7e37e43c8800759c"))
        assert abs(decoder.decode() - 1.0e300) < 1e285

    def test_float_smallest_subnormal(self):
        """RFC 8949 Appendix A: 5.960464477539063e-8 -> 0xf90001"""
        decoder = CBORDecoder(bytes.fromhex("f90001"))
        assert abs(decoder.decode() - 5.960464477539063e-8) < 1e-14

    def test_float_smallest_normal_half(self):
        """RFC 8949 Appendix A: 0.00006103515625 -> 0xf90400"""
        decoder = CBORDecoder(bytes.fromhex("f90400"))
        assert decoder.decode() == 0.00006103515625

    def test_float_minus_4_0(self):
        """RFC 8949 Appendix A: -4.0 -> 0xf9c400"""
        decoder = CBORDecoder(bytes.fromhex("f9c400"))
        assert decoder.decode() == -4.0

    def test_float_minus_4_1(self):
        """RFC 8949 Appendix A: -4.1 -> 0xfbc010666666666666"""
        decoder = CBORDecoder(bytes.fromhex("fbc010666666666666"))
        assert abs(decoder.decode() - (-4.1)) < 1e-15

    def test_float_infinity_half(self):
        """RFC 8949 Appendix A: Infinity (half) -> 0xf97c00"""
        decoder = CBORDecoder(bytes.fromhex("f97c00"))
        assert decoder.decode() == float("inf")

    def test_float_nan_half(self):
        """RFC 8949 Appendix A: NaN (half) -> 0xf97e00"""
        decoder = CBORDecoder(bytes.fromhex("f97e00"))
        assert math.isnan(decoder.decode())

    def test_float_minus_infinity_half(self):
        """RFC 8949 Appendix A: -Infinity (half) -> 0xf9fc00"""
        decoder = CBORDecoder(bytes.fromhex("f9fc00"))
        assert decoder.decode() == float("-inf")

    def test_float_infinity_single(self):
        """RFC 8949 Appendix A: Infinity (single) -> 0xfa7f800000"""
        decoder = CBORDecoder(bytes.fromhex("fa7f800000"))
        assert decoder.decode() == float("inf")

    def test_float_nan_single(self):
        """RFC 8949 Appendix A: NaN (single) -> 0xfa7fc00000"""
        decoder = CBORDecoder(bytes.fromhex("fa7fc00000"))
        assert math.isnan(decoder.decode())

    def test_float_minus_infinity_single(self):
        """RFC 8949 Appendix A: -Infinity (single) -> 0xfaff800000"""
        decoder = CBORDecoder(bytes.fromhex("faff800000"))
        assert decoder.decode() == float("-inf")

    def test_float_infinity_double(self):
        """RFC 8949 Appendix A: Infinity (double) -> 0xfb7ff0000000000000"""
        decoder = CBORDecoder(bytes.fromhex("fb7ff0000000000000"))
        assert decoder.decode() == float("inf")

    def test_float_nan_double(self):
        """RFC 8949 Appendix A: NaN (double) -> 0xfb7ff8000000000000"""
        decoder = CBORDecoder(bytes.fromhex("fb7ff8000000000000"))
        assert math.isnan(decoder.decode())

    def test_float_minus_infinity_double(self):
        """RFC 8949 Appendix A: -Infinity (double) -> 0xfbfff0000000000000"""
        decoder = CBORDecoder(bytes.fromhex("fbfff0000000000000"))
        assert decoder.decode() == float("-inf")

    # =========================================================================
    # Simple Values (Major Type 7)
    # =========================================================================

    def test_simple_false(self):
        """RFC 8949 Appendix A: false -> 0xf4"""
        decoder = CBORDecoder(bytes.fromhex("f4"))
        assert decoder.decode() is False

    def test_simple_true(self):
        """RFC 8949 Appendix A: true -> 0xf5"""
        decoder = CBORDecoder(bytes.fromhex("f5"))
        assert decoder.decode() is True

    def test_simple_null(self):
        """RFC 8949 Appendix A: null -> 0xf6"""
        decoder = CBORDecoder(bytes.fromhex("f6"))
        assert decoder.decode() is None

    def test_simple_undefined(self):
        """RFC 8949 Appendix A: undefined -> 0xf7"""
        decoder = CBORDecoder(bytes.fromhex("f7"))
        result = decoder.decode()
        assert result == {"undefined": True}

    def test_simple_16(self):
        """RFC 8949 Appendix A: simple(16) -> 0xf0"""
        decoder = CBORDecoder(bytes.fromhex("f0"))
        result = decoder.decode()
        assert result == {"simple": 16}

    def test_simple_255(self):
        """RFC 8949 Appendix A: simple(255) -> 0xf8ff"""
        decoder = CBORDecoder(bytes.fromhex("f8ff"))
        result = decoder.decode()
        assert result == {"simple": 255}

    # =========================================================================
    # Byte Strings (Major Type 2)
    # =========================================================================

    def test_byte_string_empty(self):
        """RFC 8949 Appendix A: h'' -> 0x40"""
        decoder = CBORDecoder(bytes.fromhex("40"))
        assert decoder.decode() == b""

    def test_byte_string_4_bytes(self):
        """RFC 8949 Appendix A: h'01020304' -> 0x4401020304"""
        decoder = CBORDecoder(bytes.fromhex("4401020304"))
        assert decoder.decode() == bytes.fromhex("01020304")

    # =========================================================================
    # Text Strings (Major Type 3)
    # =========================================================================

    def test_text_string_empty(self):
        """RFC 8949 Appendix A: "" -> 0x60"""
        decoder = CBORDecoder(bytes.fromhex("60"))
        assert decoder.decode() == ""

    def test_text_string_a(self):
        """RFC 8949 Appendix A: "a" -> 0x6161"""
        decoder = CBORDecoder(bytes.fromhex("6161"))
        assert decoder.decode() == "a"

    def test_text_string_IETF(self):
        """RFC 8949 Appendix A: "IETF" -> 0x6449455446"""
        decoder = CBORDecoder(bytes.fromhex("6449455446"))
        assert decoder.decode() == "IETF"

    def test_text_string_escaped_chars(self):
        r"""RFC 8949 Appendix A: "\"\\" -> 0x62225c"""
        decoder = CBORDecoder(bytes.fromhex("62225c"))
        assert decoder.decode() == '"\\'

    def test_text_string_unicode_u00fc(self):
        """RFC 8949 Appendix A: "ü" (U+00FC) -> 0x62c3bc"""
        decoder = CBORDecoder(bytes.fromhex("62c3bc"))
        assert decoder.decode() == "\u00fc"

    def test_text_string_unicode_u6c34(self):
        """RFC 8949 Appendix A: "水" (U+6C34) -> 0x63e6b0b4"""
        decoder = CBORDecoder(bytes.fromhex("63e6b0b4"))
        assert decoder.decode() == "\u6c34"

    def test_text_string_unicode_u10151(self):
        """RFC 8949 Appendix A: "𐅑" (U+10151) -> 0x64f0908591"""
        decoder = CBORDecoder(bytes.fromhex("64f0908591"))
        assert decoder.decode() == "\U00010151"

    # =========================================================================
    # Arrays (Major Type 4)
    # =========================================================================

    def test_array_empty(self):
        """RFC 8949 Appendix A: [] -> 0x80"""
        decoder = CBORDecoder(bytes.fromhex("80"))
        assert decoder.decode() == []

    def test_array_1_2_3(self):
        """RFC 8949 Appendix A: [1, 2, 3] -> 0x83010203"""
        decoder = CBORDecoder(bytes.fromhex("83010203"))
        assert decoder.decode() == [1, 2, 3]

    def test_array_nested(self):
        """RFC 8949 Appendix A: [1, [2, 3], [4, 5]] -> 0x8301820203820405"""
        decoder = CBORDecoder(bytes.fromhex("8301820203820405"))
        assert decoder.decode() == [1, [2, 3], [4, 5]]

    def test_array_25_elements(self):
        """RFC 8949 Appendix A: [1..25] -> 0x98190102...181819"""
        decoder = CBORDecoder(
            bytes.fromhex("98190102030405060708090a0b0c0d0e0f101112131415161718181819")
        )
        assert decoder.decode() == list(range(1, 26))

    # =========================================================================
    # Maps (Major Type 5)
    # =========================================================================

    def test_map_empty(self):
        """RFC 8949 Appendix A: {} -> 0xa0"""
        decoder = CBORDecoder(bytes.fromhex("a0"))
        assert decoder.decode() == {}

    def test_map_1_2_3_4(self):
        """RFC 8949 Appendix A: {1: 2, 3: 4} -> 0xa201020304"""
        decoder = CBORDecoder(bytes.fromhex("a201020304"))
        assert decoder.decode() == {1: 2, 3: 4}

    def test_map_with_strings_and_arrays(self):
        """RFC 8949 Appendix A: {"a": 1, "b": [2, 3]} -> 0xa26161016162820203"""
        decoder = CBORDecoder(bytes.fromhex("a26161016162820203"))
        assert decoder.decode() == {"a": 1, "b": [2, 3]}

    def test_array_with_map(self):
        """RFC 8949 Appendix A: ["a", {"b": "c"}] -> 0x826161a161626163"""
        decoder = CBORDecoder(bytes.fromhex("826161a161626163"))
        assert decoder.decode() == ["a", {"b": "c"}]

    def test_map_5_pairs(self):
        """RFC 8949 Appendix A: {"a": "A", "b": "B", "c": "C", "d": "D", "e": "E"}"""
        decoder = CBORDecoder(
            bytes.fromhex("a56161614161626142616361436164614461656145")
        )
        assert decoder.decode() == {"a": "A", "b": "B", "c": "C", "d": "D", "e": "E"}

    # =========================================================================
    # Tags (Major Type 6)
    # =========================================================================

    def test_tag_0_datetime_string(self):
        """RFC 8949 Appendix A: 0("2013-03-21T20:04:00Z") -> 0xc074..."""
        decoder = CBORDecoder(
            bytes.fromhex("c074323031332d30332d32315432303a30343a30305a")
        )
        result = decoder.decode()
        assert result == {"tag": 0, "value": "2013-03-21T20:04:00Z"}

    def test_tag_1_epoch_time(self):
        """RFC 8949 Appendix A: 1(1363896240) -> 0xc11a514b67b0"""
        decoder = CBORDecoder(bytes.fromhex("c11a514b67b0"))
        result = decoder.decode()
        assert result == {"tag": 1, "value": 1363896240}

    def test_tag_1_epoch_time_float(self):
        """RFC 8949 Appendix A: 1(1363896240.5) -> 0xc1fb41d452d9ec200000"""
        decoder = CBORDecoder(bytes.fromhex("c1fb41d452d9ec200000"))
        result = decoder.decode()
        assert result["tag"] == 1
        assert abs(result["value"] - 1363896240.5) < 0.001

    def test_tag_23_base16_hint(self):
        """RFC 8949 Appendix A: 23(h'01020304') -> 0xd74401020304"""
        decoder = CBORDecoder(bytes.fromhex("d74401020304"))
        result = decoder.decode()
        assert result == {"tag": 23, "value": bytes.fromhex("01020304")}

    def test_tag_24_encoded_cbor(self):
        """RFC 8949 Appendix A: 24(h'6449455446') -> 0xd818456449455446"""
        decoder = CBORDecoder(bytes.fromhex("d818456449455446"))
        result = decoder.decode()
        assert result == {"tag": 24, "value": bytes.fromhex("6449455446")}

    def test_tag_32_uri(self):
        """RFC 8949 Appendix A: 32("http://www.example.com") -> 0xd82076..."""
        decoder = CBORDecoder(
            bytes.fromhex("d82076687474703a2f2f7777772e6578616d706c652e636f6d")
        )
        result = decoder.decode()
        assert result == {"tag": 32, "value": "http://www.example.com"}

    # =========================================================================
    # Indefinite-Length Items
    # =========================================================================

    def test_indefinite_byte_string(self):
        """RFC 8949 Appendix A: (_ h'0102', h'030405') -> 0x5f42010243030405ff"""
        decoder = CBORDecoder(bytes.fromhex("5f42010243030405ff"))
        assert decoder.decode() == bytes.fromhex("0102030405")

    def test_indefinite_text_string(self):
        """RFC 8949 Appendix A: (_ "strea", "ming") -> 0x7f657374726561646d696e67ff"""
        decoder = CBORDecoder(bytes.fromhex("7f657374726561646d696e67ff"))
        assert decoder.decode() == "streaming"

    def test_indefinite_array_empty(self):
        """RFC 8949 Appendix A: [_ ] -> 0x9fff"""
        decoder = CBORDecoder(bytes.fromhex("9fff"))
        assert decoder.decode() == []

    def test_indefinite_array_nested(self):
        """RFC 8949 Appendix A: [_ 1, [2, 3], [_ 4, 5]] -> 0x9f018202039f0405ffff"""
        decoder = CBORDecoder(bytes.fromhex("9f018202039f0405ffff"))
        assert decoder.decode() == [1, [2, 3], [4, 5]]

    def test_indefinite_array_mixed_1(self):
        """RFC 8949 Appendix A: [_ 1, [2, 3], [4, 5]] -> 0x9f01820203820405ff"""
        decoder = CBORDecoder(bytes.fromhex("9f01820203820405ff"))
        assert decoder.decode() == [1, [2, 3], [4, 5]]

    def test_indefinite_array_mixed_2(self):
        """RFC 8949 Appendix A: [1, [2, 3], [_ 4, 5]] -> 0x83018202039f0405ff"""
        decoder = CBORDecoder(bytes.fromhex("83018202039f0405ff"))
        assert decoder.decode() == [1, [2, 3], [4, 5]]

    def test_indefinite_array_mixed_3(self):
        """RFC 8949 Appendix A: [1, [_ 2, 3], [4, 5]] -> 0x83019f0203ff820405"""
        decoder = CBORDecoder(bytes.fromhex("83019f0203ff820405"))
        assert decoder.decode() == [1, [2, 3], [4, 5]]

    def test_indefinite_array_25_elements(self):
        """RFC 8949 Appendix A: [_ 1..25] -> 0x9f0102...1819ff"""
        decoder = CBORDecoder(
            bytes.fromhex("9f0102030405060708090a0b0c0d0e0f101112131415161718181819ff")
        )
        assert decoder.decode() == list(range(1, 26))

    def test_indefinite_map_with_nested_indefinite_array(self):
        """RFC 8949 Appendix A: {_ "a": 1, "b": [_ 2, 3]} -> 0xbf61610161629f0203ffff"""
        decoder = CBORDecoder(bytes.fromhex("bf61610161629f0203ffff"))
        assert decoder.decode() == {"a": 1, "b": [2, 3]}

    def test_array_with_indefinite_map(self):
        """RFC 8949 Appendix A: ["a", {_ "b": "c"}] -> 0x826161bf61626163ff"""
        decoder = CBORDecoder(bytes.fromhex("826161bf61626163ff"))
        assert decoder.decode() == ["a", {"b": "c"}]

    def test_indefinite_map_fun_amt(self):
        """RFC 8949 Appendix A: {_ "Fun": true, "Amt": -2} -> 0xbf6346756ef563416d7421ff"""
        decoder = CBORDecoder(bytes.fromhex("bf6346756ef563416d7421ff"))
        assert decoder.decode() == {"Fun": True, "Amt": -2}


class TestCBORDecoderBignums(CodeTransparencyClientTestBase):
    """Test cases for bignum decoding (RFC 8949 Appendix A)."""

    def test_bignum_positive(self):
        """RFC 8949 Appendix A: 18446744073709551616 (2^64) -> 0xc249010000000000000000"""
        decoder = CBORDecoder(bytes.fromhex("c249010000000000000000"))
        result = decoder.decode()
        # This is tag 2 (positive bignum) with byte string value
        assert result["tag"] == 2
        assert result["value"] == bytes.fromhex("010000000000000000")
        # The byte string represents 2^64 in big-endian
        bignum_value = int.from_bytes(result["value"], "big")
        assert bignum_value == 18446744073709551616

    def test_bignum_negative(self):
        """RFC 8949 Appendix A: -18446744073709551617 -> 0xc349010000000000000000"""
        decoder = CBORDecoder(bytes.fromhex("c349010000000000000000"))
        result = decoder.decode()
        # This is tag 3 (negative bignum) with byte string value
        assert result["tag"] == 3
        assert result["value"] == bytes.fromhex("010000000000000000")
        # For negative bignum, value = -1 - n where n is the byte string value
        bignum_value = -1 - int.from_bytes(result["value"], "big")
        assert bignum_value == -18446744073709551617


class TestCBORDecoderEdgeCases(CodeTransparencyClientTestBase):
    """Edge case and abuse scenario tests for CBORDecoder.

    These tests verify that the decoder properly handles malformed,
    truncated, or malicious CBOR data that could cause issues in production.
    """

    # =========================================================================
    # Empty and Truncated Data
    # =========================================================================

    def test_empty_data(self):
        """Decoding empty data should raise ValueError."""
        decoder = CBORDecoder(b"")
        with pytest.raises(ValueError, match="No CBOR data to decode"):
            decoder.decode()

    def test_truncated_uint8(self):
        """Truncated uint8 (additional info 24 but no following byte)."""
        decoder = CBORDecoder(bytes.fromhex("18"))  # uint, 1-byte follows, but missing
        with pytest.raises(ValueError, match="Unexpected end of data reading uint8"):
            decoder.decode()

    def test_truncated_uint16(self):
        """Truncated uint16 (additional info 25 but only 1 byte follows)."""
        decoder = CBORDecoder(bytes.fromhex("1901"))  # uint, 2-byte follows, but only 1
        with pytest.raises(ValueError, match="Unexpected end of data reading uint16"):
            decoder.decode()

    def test_truncated_uint32(self):
        """Truncated uint32 (additional info 26 but only 3 bytes follow)."""
        decoder = CBORDecoder(
            bytes.fromhex("1a010203")
        )  # uint, 4-byte follows, but only 3
        with pytest.raises(ValueError, match="Unexpected end of data reading uint32"):
            decoder.decode()

    def test_truncated_uint64(self):
        """Truncated uint64 (additional info 27 but only 7 bytes follow)."""
        decoder = CBORDecoder(
            bytes.fromhex("1b01020304050607")
        )  # uint, 8-byte follows, but only 7
        with pytest.raises(ValueError, match="Unexpected end of data reading uint64"):
            decoder.decode()

    def test_truncated_byte_string(self):
        """Byte string with length exceeding available data."""
        decoder = CBORDecoder(
            bytes.fromhex("44010203")
        )  # 4-byte string, but only 3 bytes
        with pytest.raises(
            ValueError, match="Byte string length exceeds available data"
        ):
            decoder.decode()

    def test_truncated_text_string(self):
        """Text string with length exceeding available data."""
        decoder = CBORDecoder(
            bytes.fromhex("6448454c")
        )  # 4-byte text, but only 3 bytes "HEL"
        with pytest.raises(
            ValueError, match="Text string length exceeds available data"
        ):
            decoder.decode()

    def test_truncated_array(self):
        """Array with fewer elements than declared count."""
        decoder = CBORDecoder(
            bytes.fromhex("830102")
        )  # Array of 3, but only 2 elements
        with pytest.raises(ValueError, match="Unexpected end of CBOR data"):
            decoder.decode()

    def test_truncated_map_missing_value(self):
        """Map with key but no value."""
        decoder = CBORDecoder(
            bytes.fromhex("a10102")
        )  # Map of 1 pair, but key 1 has value, then key 2 has none
        # Actually this is valid: {1: 2}. Let's make a proper truncated case
        decoder = CBORDecoder(
            bytes.fromhex("a20102")
        )  # Map of 2 pairs, but only 1 complete pair
        with pytest.raises(ValueError, match="Unexpected end of CBOR data"):
            decoder.decode()

    def test_truncated_map_missing_key(self):
        """Map truncated in the middle."""
        decoder = CBORDecoder(bytes.fromhex("a1"))  # Map of 1 pair, but no key-value
        with pytest.raises(ValueError, match="Unexpected end of CBOR data"):
            decoder.decode()

    def test_truncated_half_float(self):
        """Half-precision float with missing bytes."""
        decoder = CBORDecoder(bytes.fromhex("f901"))  # Half float, but only 1 byte
        with pytest.raises(
            ValueError, match="Unexpected end of data reading half-precision float"
        ):
            decoder.decode()

    def test_truncated_single_float(self):
        """Single-precision float with missing bytes."""
        decoder = CBORDecoder(
            bytes.fromhex("fa010203")
        )  # Single float, but only 3 bytes
        with pytest.raises(
            ValueError, match="Unexpected end of data reading single-precision float"
        ):
            decoder.decode()

    def test_truncated_double_float(self):
        """Double-precision float with missing bytes."""
        decoder = CBORDecoder(
            bytes.fromhex("fb01020304050607")
        )  # Double float, but only 7 bytes
        with pytest.raises(
            ValueError, match="Unexpected end of data reading double-precision float"
        ):
            decoder.decode()

    def test_truncated_simple_value(self):
        """Two-byte simple value with missing second byte."""
        decoder = CBORDecoder(
            bytes.fromhex("f8")
        )  # Simple value extension, but no value byte
        with pytest.raises(
            ValueError, match="Unexpected end of data reading simple value"
        ):
            decoder.decode()

    # =========================================================================
    # Reserved Additional Info Values (RFC 8949)
    # =========================================================================

    def test_reserved_additional_info_28(self):
        """Reserved additional info value 28 should raise ValueError."""
        decoder = CBORDecoder(bytes.fromhex("1c"))  # Major type 0, additional info 28
        with pytest.raises(ValueError, match="Reserved additional info value: 28"):
            decoder.decode()

    def test_reserved_additional_info_29(self):
        """Reserved additional info value 29 should raise ValueError."""
        decoder = CBORDecoder(bytes.fromhex("1d"))  # Major type 0, additional info 29
        with pytest.raises(ValueError, match="Reserved additional info value: 29"):
            decoder.decode()

    def test_reserved_additional_info_30(self):
        """Reserved additional info value 30 should raise ValueError."""
        decoder = CBORDecoder(bytes.fromhex("1e"))  # Major type 0, additional info 30
        with pytest.raises(ValueError, match="Reserved additional info value: 30"):
            decoder.decode()

    def test_reserved_in_negative_int(self):
        """Reserved value in negative integer type."""
        decoder = CBORDecoder(bytes.fromhex("3c"))  # Major type 1, additional info 28
        with pytest.raises(ValueError, match="Reserved additional info value: 28"):
            decoder.decode()

    def test_reserved_in_byte_string(self):
        """Reserved value in byte string type."""
        decoder = CBORDecoder(bytes.fromhex("5c"))  # Major type 2, additional info 28
        with pytest.raises(ValueError, match="Reserved additional info value: 28"):
            decoder.decode()

    def test_reserved_in_text_string(self):
        """Reserved value in text string type."""
        decoder = CBORDecoder(bytes.fromhex("7c"))  # Major type 3, additional info 28
        with pytest.raises(ValueError, match="Reserved additional info value: 28"):
            decoder.decode()

    def test_reserved_in_array(self):
        """Reserved value in array type."""
        decoder = CBORDecoder(bytes.fromhex("9c"))  # Major type 4, additional info 28
        with pytest.raises(ValueError, match="Reserved additional info value: 28"):
            decoder.decode()

    def test_reserved_in_map(self):
        """Reserved value in map type."""
        decoder = CBORDecoder(bytes.fromhex("bc"))  # Major type 5, additional info 28
        with pytest.raises(ValueError, match="Reserved additional info value: 28"):
            decoder.decode()

    def test_reserved_in_tag(self):
        """Reserved value in tag type."""
        decoder = CBORDecoder(bytes.fromhex("dc"))  # Major type 6, additional info 28
        with pytest.raises(ValueError, match="Reserved additional info value: 28"):
            decoder.decode()

    def test_reserved_in_simple(self):
        """Reserved value in simple/float type."""
        decoder = CBORDecoder(bytes.fromhex("fc"))  # Major type 7, additional info 28
        with pytest.raises(ValueError, match="Reserved additional info value: 28"):
            decoder.decode()

    # =========================================================================
    # Break Stop Code Abuse
    # =========================================================================

    def test_break_outside_indefinite(self):
        """Break stop code (0xFF) outside indefinite-length context should raise."""
        decoder = CBORDecoder(bytes.fromhex("ff"))
        with pytest.raises(ValueError, match="Unexpected 'break' stop code"):
            decoder.decode()

    def test_break_in_definite_array(self):
        """Break inside a definite-length array should be treated as value."""
        # This tests that break is only valid in indefinite context
        decoder = CBORDecoder(bytes.fromhex("81ff"))  # Array of 1 containing break
        with pytest.raises(ValueError, match="Unexpected 'break' stop code"):
            decoder.decode()

    def test_break_in_definite_map_value(self):
        """Break as a map value in definite-length map."""
        decoder = CBORDecoder(bytes.fromhex("a101ff"))  # Map {1: break}
        with pytest.raises(ValueError, match="Unexpected 'break' stop code"):
            decoder.decode()

    # =========================================================================
    # Invalid Indefinite-Length Usage
    # =========================================================================

    def test_indefinite_length_unsigned_int(self):
        """Indefinite length is not allowed for unsigned integers (major type 0)."""
        decoder = CBORDecoder(bytes.fromhex("1f"))  # Major type 0, additional info 31
        with pytest.raises(
            ValueError, match="Indefinite length not allowed for major type 0"
        ):
            decoder.decode()

    def test_indefinite_length_negative_int(self):
        """Indefinite length is not allowed for negative integers (major type 1)."""
        decoder = CBORDecoder(bytes.fromhex("3f"))  # Major type 1, additional info 31
        with pytest.raises(
            ValueError, match="Indefinite length not allowed for major type 1"
        ):
            decoder.decode()

    def test_indefinite_length_tag(self):
        """Indefinite length is not allowed for tags (major type 6)."""
        decoder = CBORDecoder(bytes.fromhex("df"))  # Major type 6, additional info 31
        with pytest.raises(
            ValueError, match="Indefinite length not allowed for major type 6"
        ):
            decoder.decode()

    def test_indefinite_byte_string_with_text_chunk(self):
        """Indefinite byte string containing a text string chunk is invalid."""
        # 5f = indefinite byte string, 61 61 = text "a", ff = break
        decoder = CBORDecoder(bytes.fromhex("5f6161ff"))
        with pytest.raises(
            ValueError,
            match="Indefinite byte string chunk must be definite-length byte string",
        ):
            decoder.decode()

    def test_indefinite_byte_string_with_integer_chunk(self):
        """Indefinite byte string containing an integer chunk is invalid."""
        # 5f = indefinite byte string, 01 = integer 1, ff = break
        decoder = CBORDecoder(bytes.fromhex("5f01ff"))
        with pytest.raises(
            ValueError,
            match="Indefinite byte string chunk must be definite-length byte string",
        ):
            decoder.decode()

    def test_indefinite_text_string_with_byte_chunk(self):
        """Indefinite text string containing a byte string chunk is invalid."""
        # 7f = indefinite text string, 41 61 = byte string "a", ff = break
        decoder = CBORDecoder(bytes.fromhex("7f4161ff"))
        with pytest.raises(
            ValueError,
            match="Indefinite text string chunk must be definite-length text string",
        ):
            decoder.decode()

    def test_indefinite_text_string_with_array_chunk(self):
        """Indefinite text string containing an array chunk is invalid."""
        # 7f = indefinite text string, 80 = empty array, ff = break
        decoder = CBORDecoder(bytes.fromhex("7f80ff"))
        with pytest.raises(
            ValueError,
            match="Indefinite text string chunk must be definite-length text string",
        ):
            decoder.decode()

    def test_indefinite_byte_string_missing_break(self):
        """Indefinite byte string without break terminator."""
        # 5f = indefinite byte string, 41 01 = byte string with 1 byte, then truncated
        decoder = CBORDecoder(bytes.fromhex("5f4101"))
        with pytest.raises(ValueError, match="Unexpected end of CBOR data"):
            decoder.decode()

    def test_indefinite_array_missing_break(self):
        """Indefinite array without break terminator."""
        decoder = CBORDecoder(bytes.fromhex("9f0102"))  # Indefinite array [1, 2, ...
        with pytest.raises(ValueError, match="Unexpected end of CBOR data"):
            decoder.decode()

    def test_indefinite_map_missing_break(self):
        """Indefinite map without break terminator."""
        decoder = CBORDecoder(bytes.fromhex("bf0102"))  # Indefinite map {1: 2, ...
        with pytest.raises(ValueError, match="Unexpected end of CBOR data"):
            decoder.decode()

    # =========================================================================
    # Invalid UTF-8 in Text Strings
    # =========================================================================

    def test_invalid_utf8_lone_continuation(self):
        """Text string with invalid UTF-8: lone continuation byte."""
        # 62 = 2-byte text string, 80 80 = two lone continuation bytes
        decoder = CBORDecoder(bytes.fromhex("628080"))
        with pytest.raises(UnicodeDecodeError):
            decoder.decode()

    def test_invalid_utf8_truncated_sequence(self):
        """Text string with invalid UTF-8: truncated multi-byte sequence."""
        # 62 = 2-byte text string, c3 = start of 2-byte UTF-8, but second byte is ASCII
        decoder = CBORDecoder(bytes.fromhex("62c361"))
        with pytest.raises(UnicodeDecodeError):
            decoder.decode()

    def test_invalid_utf8_overlong_encoding(self):
        """Text string with invalid UTF-8: overlong encoding of ASCII."""
        # 62 = 2-byte text string, c0 80 = overlong encoding of NUL
        decoder = CBORDecoder(bytes.fromhex("62c080"))
        with pytest.raises(UnicodeDecodeError):
            decoder.decode()

    def test_invalid_utf8_surrogate(self):
        """Text string with invalid UTF-8: surrogate codepoint."""
        # 63 = 3-byte text string, ed a0 80 = U+D800 (surrogate)
        decoder = CBORDecoder(bytes.fromhex("63eda080"))
        with pytest.raises(UnicodeDecodeError):
            decoder.decode()

    # =========================================================================
    # Invalid Simple Value Encodings
    # =========================================================================

    def test_two_byte_simple_value_under_32(self):
        """Two-byte encoding for simple value < 32 is invalid (RFC 8949)."""
        # f8 = simple value extension, 00 = simple(0) - should use f0 instead
        decoder = CBORDecoder(bytes.fromhex("f800"))
        with pytest.raises(
            ValueError, match="Invalid two-byte encoding for simple value 0"
        ):
            decoder.decode()

    def test_two_byte_simple_value_31(self):
        """Two-byte encoding for simple value 31 is invalid."""
        decoder = CBORDecoder(bytes.fromhex("f81f"))
        with pytest.raises(
            ValueError, match="Invalid two-byte encoding for simple value 31"
        ):
            decoder.decode()

    def test_two_byte_simple_value_20_false(self):
        """Two-byte encoding for simple value 20 (false) is invalid."""
        decoder = CBORDecoder(bytes.fromhex("f814"))
        with pytest.raises(
            ValueError, match="Invalid two-byte encoding for simple value 20"
        ):
            decoder.decode()

    # =========================================================================
    # Large Allocation Attacks
    # =========================================================================

    def test_huge_byte_string_length(self):
        """Byte string with impossibly large length (should fail, not OOM)."""
        # 5b = byte string, 8-byte length follows = max uint64
        decoder = CBORDecoder(bytes.fromhex("5bffffffffffffffff"))
        with pytest.raises(
            ValueError, match="Byte string length exceeds available data"
        ):
            decoder.decode()

    def test_huge_text_string_length(self):
        """Text string with impossibly large length."""
        decoder = CBORDecoder(bytes.fromhex("7bffffffffffffffff"))
        with pytest.raises(
            ValueError, match="Text string length exceeds available data"
        ):
            decoder.decode()

    def test_huge_array_count(self):
        """Array with impossibly large count - should fail during iteration."""
        # 9b = array, 8-byte count = very large
        decoder = CBORDecoder(
            bytes.fromhex("9b0000000000000100")
        )  # 256 elements but no data
        with pytest.raises(ValueError, match="Unexpected end of CBOR data"):
            decoder.decode()

    def test_huge_map_count(self):
        """Map with impossibly large count."""
        decoder = CBORDecoder(
            bytes.fromhex("bb0000000000000100")
        )  # 256 pairs but no data
        with pytest.raises(ValueError, match="Unexpected end of CBOR data"):
            decoder.decode()

    # =========================================================================
    # Deeply Nested Structures (potential stack overflow)
    # =========================================================================

    def test_deeply_nested_arrays(self):
        """Deeply nested arrays should be handled (tests recursion limit)."""
        # Create 100 levels of nesting: [[[[...]]]]
        depth = 100
        data = bytes([0x81] * depth) + bytes([0x00])  # 100 x [array of 1] + integer 0
        decoder = CBORDecoder(bytes(data))
        result = decoder.decode()
        # Verify structure
        current = result
        for _ in range(depth):
            assert isinstance(current, list)
            assert len(current) == 1
            current = current[0]
        assert current == 0

    def test_deeply_nested_maps(self):
        """Deeply nested maps should be handled."""
        # Create 50 levels of nesting: {0: {0: {0: ...}}}
        depth = 50
        data = bytes([0xA1, 0x00] * depth) + bytes([0x00])  # 50 x {0: } + integer 0
        decoder = CBORDecoder(bytes(data))
        result = decoder.decode()
        current = result
        for _ in range(depth):
            assert isinstance(current, dict)
            assert 0 in current
            current = current[0]
        assert current == 0

    def test_deeply_nested_indefinite_arrays(self):
        """Deeply nested indefinite arrays."""
        depth = 50
        data = bytes([0x9F] * depth) + bytes([0x00]) + bytes([0xFF] * depth)
        decoder = CBORDecoder(bytes(data))
        result = decoder.decode()
        current = result
        for _ in range(depth):
            assert isinstance(current, list)
            assert len(current) == 1
            current = current[0]
        assert current == 0

    # =========================================================================
    # Map Edge Cases
    # =========================================================================

    def test_map_with_duplicate_keys(self):
        """Map with duplicate keys - last value wins (Python dict behavior)."""
        # a2 = map of 2, 01 02 = {1: 2}, 01 03 = {1: 3} (duplicate key)
        decoder = CBORDecoder(bytes.fromhex("a201020103"))
        result = decoder.decode()
        # Python dict keeps last value
        assert result == {1: 3}

    def test_map_with_non_string_keys(self):
        """Map with various non-string keys including unhashable array key."""
        # a2 = map of 2: {1: "a", [1,2]: "b"}
        # 01 = key 1, 61 61 = value "a"
        # 82 01 02 = key [1,2], 61 62 = value "b"
        decoder = CBORDecoder(bytes.fromhex("a2016161820102616a"))
        # Note: Lists are not hashable in Python, this should raise TypeError
        with pytest.raises(TypeError):
            decoder.decode()

    def test_map_with_bytes_key(self):
        """Map with bytes key (valid in CBOR, problematic in Python < 3.x)."""
        # a1 = map of 1, 41 01 = byte string [0x01], 02 = value 2
        decoder = CBORDecoder(bytes.fromhex("a1410102"))
        result = decoder.decode()
        assert result == {b"\x01": 2}

    # =========================================================================
    # Tag Edge Cases
    # =========================================================================

    def test_nested_tags(self):
        """Multiple nested tags."""
        # c0 c1 c2 01 = tag 0(tag 1(tag 2(1)))
        decoder = CBORDecoder(bytes.fromhex("c0c1c201"))
        result = decoder.decode()
        assert result["tag"] == 0
        assert result["value"]["tag"] == 1
        assert result["value"]["value"]["tag"] == 2
        assert result["value"]["value"]["value"] == 1

    def test_tag_with_truncated_value(self):
        """Tag followed by truncated data."""
        decoder = CBORDecoder(bytes.fromhex("c0"))  # Tag 0, but no value
        with pytest.raises(ValueError, match="Unexpected end of CBOR data"):
            decoder.decode()

    def test_very_large_tag_number(self):
        """Tag with maximum uint64 tag number."""
        # db = tag with 8-byte number, followed by value 0
        decoder = CBORDecoder(bytes.fromhex("dbffffffffffffffff00"))
        result = decoder.decode()
        assert result["tag"] == 18446744073709551615
        assert result["value"] == 0

    # =========================================================================
    # COSE_Sign1 Edge Cases
    # =========================================================================

    def test_cose_sign1_not_array(self):
        """COSE_Sign1 structure that is not an array."""
        # d2 = tag 18, a0 = empty map (should be array)
        decoder = CBORDecoder(bytes.fromhex("d2a0"))
        with pytest.raises(ValueError, match="Invalid COSE_Sign1 structure"):
            decoder.decode_cose_sign1()

    def test_cose_sign1_wrong_array_length(self):
        """COSE_Sign1 with wrong number of elements."""
        # d2 = tag 18, 83 = array of 3 (should be 4)
        decoder = CBORDecoder(bytes.fromhex("d2830102f6"))
        with pytest.raises(ValueError, match="Invalid COSE_Sign1 structure"):
            decoder.decode_cose_sign1()

    def test_cose_sign1_empty_array(self):
        """COSE_Sign1 with empty array."""
        decoder = CBORDecoder(bytes.fromhex("d280"))  # tag 18, empty array
        with pytest.raises(ValueError, match="Invalid COSE_Sign1 structure"):
            decoder.decode_cose_sign1()

    def test_cose_sign1_without_tag(self):
        """COSE_Sign1 structure without tag 18 (still valid structure)."""
        # 84 = array of 4, 40 = empty bstr (protected), a0 = empty map (unprotected),
        # f6 = null (payload), 40 = empty bstr (signature)
        decoder = CBORDecoder(bytes.fromhex("8440a0f640"))
        result = decoder.decode_cose_sign1()
        assert result["protected_headers"] == {}
        assert result["unprotected_headers"] == {}
        assert result["payload"] is None
        assert result["signature"] == b""

    def test_cose_sign1_with_invalid_protected_headers(self):
        """COSE_Sign1 with protected headers that are not a map when decoded."""
        # Protected headers decode to an array instead of map
        # 84 = array of 4, 42 8001 = bstr containing CBOR array [1]
        decoder = CBORDecoder(bytes.fromhex("84428001a0f640"))
        result = decoder.decode_cose_sign1()
        # Should handle gracefully - protected_headers becomes empty dict
        assert result["protected_headers"] == {}

    def test_cose_sign1_with_non_bytes_protected_headers(self):
        """COSE_Sign1 with protected headers that are not bytes."""
        # 84 = array of 4, 01 = integer (should be bstr), a0, f6, 40
        decoder = CBORDecoder(bytes.fromhex("8401a0f640"))
        result = decoder.decode_cose_sign1()
        assert result["protected_headers"] == {}

    def test_cose_sign1_with_nested_cwt_not_bytes(self):
        """COSE_Sign1 with CWT claim (key 15) that is not bytes."""
        # Protected headers map with key 15 = integer instead of bytes
        # a1 0f 01 = {15: 1}
        phdr = bytes.fromhex("a10f01")
        # Encode as CBOR byte string
        phdr_cbor = bytes([0x40 + len(phdr)]) + phdr
        full_data = bytes.fromhex("d284") + phdr_cbor + bytes.fromhex("a0f640")
        decoder = CBORDecoder(full_data)
        result = decoder.decode_cose_sign1()
        # CWT header is not bytes, so it should remain as-is
        assert result["protected_headers"][15] == 1

    # =========================================================================
    # Trailing Data
    # =========================================================================

    def test_trailing_data_after_valid_cbor(self):
        """Valid CBOR followed by extra bytes - decoder stops at first item."""
        decoder = CBORDecoder(bytes.fromhex("0101010101"))  # Five 1s
        result = decoder.decode()
        assert result == 1
        # Position should be at 1, not at end
        assert decoder.pos == 1

    def test_decode_multiple_items(self):
        """Decoder can decode multiple consecutive items."""
        decoder = CBORDecoder(bytes.fromhex("010203"))  # 1, 2, 3
        assert decoder.decode() == 1
        assert decoder.decode() == 2
        assert decoder.decode() == 3

    def test_decode_after_exhaustion(self):
        """Decoding after data is exhausted raises error."""
        decoder = CBORDecoder(bytes.fromhex("01"))
        decoder.decode()
        with pytest.raises(ValueError, match="Unexpected end of CBOR data"):
            decoder.decode()

    # =========================================================================
    # Float Special Cases
    # =========================================================================

    def test_half_float_all_zeros(self):
        """Half-precision float: +0.0"""
        decoder = CBORDecoder(bytes.fromhex("f90000"))
        assert decoder.decode() == 0.0

    def test_half_float_negative_zero(self):
        """Half-precision float: -0.0"""
        decoder = CBORDecoder(bytes.fromhex("f98000"))
        result = decoder.decode()
        assert result == 0.0
        assert math.copysign(1, result) == -1

    def test_half_float_smallest_positive(self):
        """Half-precision smallest positive subnormal."""
        decoder = CBORDecoder(bytes.fromhex("f90001"))
        result = decoder.decode()
        assert result > 0
        assert result < 0.0001

    def test_half_float_largest_subnormal(self):
        """Half-precision largest subnormal (just below smallest normal)."""
        decoder = CBORDecoder(bytes.fromhex("f903ff"))
        result = decoder.decode()
        assert result > 0
        assert result < 0.0001

    def test_single_float_denormalized(self):
        """Single-precision denormalized number."""
        decoder = CBORDecoder(
            bytes.fromhex("fa00000001")
        )  # Smallest positive subnormal
        result = decoder.decode()
        assert result > 0
        assert result < 1e-38

    def test_double_float_denormalized(self):
        """Double-precision denormalized number."""
        decoder = CBORDecoder(
            bytes.fromhex("fb0000000000000001")
        )  # Smallest positive subnormal
        result = decoder.decode()
        assert result > 0
        assert result < 1e-300

    # =========================================================================
    # Boundary Value Tests
    # =========================================================================

    def test_uint_boundary_23_24(self):
        """Test boundary between inline (23) and 1-byte (24) encoding."""
        # 23 encoded inline
        decoder = CBORDecoder(bytes.fromhex("17"))
        assert decoder.decode() == 23
        # 24 encoded with 1 extra byte
        decoder = CBORDecoder(bytes.fromhex("1818"))
        assert decoder.decode() == 24

    def test_uint_boundary_255_256(self):
        """Test boundary between 1-byte (255) and 2-byte (256) encoding."""
        decoder = CBORDecoder(bytes.fromhex("18ff"))
        assert decoder.decode() == 255
        decoder = CBORDecoder(bytes.fromhex("190100"))
        assert decoder.decode() == 256

    def test_uint_boundary_65535_65536(self):
        """Test boundary between 2-byte and 4-byte encoding."""
        decoder = CBORDecoder(bytes.fromhex("19ffff"))
        assert decoder.decode() == 65535
        decoder = CBORDecoder(bytes.fromhex("1a00010000"))
        assert decoder.decode() == 65536

    def test_uint_boundary_max_uint32(self):
        """Test max uint32 and transition to uint64."""
        decoder = CBORDecoder(bytes.fromhex("1affffffff"))
        assert decoder.decode() == 4294967295
        decoder = CBORDecoder(bytes.fromhex("1b0000000100000000"))
        assert decoder.decode() == 4294967296
