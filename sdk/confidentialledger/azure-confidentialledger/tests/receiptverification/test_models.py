# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Tests for models used for receipt verification."""

import pytest

from azure.confidentialledger.receiptverification.models import (
    LeafComponents,
    ProofElement,
    Receipt,
)

from azure.confidentialledger.receiptverification._utils import (
    _convert_dict_to_camel_case,
)

from ._shared.constants import (
    get_test_valid_receipt_1,
    get_test_valid_receipt_1_dict,
    get_test_valid_receipt_2,
    get_test_valid_receipt_2_dict,
)


def test_receipt_init_with_valid_receipt_arguments():

    # Check that Receipt constructor does not throw any exception
    # with valid receipt arguments
    try:
        Receipt(
            cert="test_cert",
            nodeId="test_node_id",
            serviceEndorsements=[],
            leafComponents=LeafComponents(
                claimsDigest="test_claims_digest",
                commitEvidence="test_commit_evidence",
                writeSetDigest="test_write_set_digest",
            ),
            proof=[
                ProofElement(
                    left="test_left",
                ),
            ],
            signature="test_signature",
        )
    except Exception as e:
        pytest.fail(f"Receipt __init__ threw an exception with a valid receipt {e}")


def test_receipt_init_with_missing_optional_arguments():

    # Check that Receipt constructor does not throw any exception
    # with optional missing arguments (e.g., service_endorsements)
    try:
        Receipt(
            cert="test_cert",
            nodeId="test_node_id",
            leafComponents=LeafComponents(
                claimsDigest="test_claims_digest",
                commitEvidence="test_commit_evidence",
                writeSetDigest="test_write_set_digest",
            ),
            proof=[
                ProofElement(
                    left="test_left",
                ),
            ],
            signature="test_signature",
            is_signature_transaction=False,
        )
    except Exception as e:
        pytest.fail(f"Receipt __init__ threw an exception with a valid receipt {e}")


def test_receipt_init_throws_exceptions_with_missing_required_fields():

    # Throws exception when missing different required fields
    with pytest.raises(TypeError, match="missing . required keyword-only argument"):
        Receipt(
            is_signature_transaction=False,
            signature="test_signature",
        )


def test_receipt_init_throws_exceptions_with_missing_required_fields_in_subobjects():

    # Throws exception when missing required fields inside LeafComponents
    with pytest.raises(TypeError, match="missing . required keyword-only argument"):
        Receipt(
            is_signature_transaction=False,
            cert="test_cert",
            node_id="test_node_id",
            service_endorsements=[],
            leaf_components=LeafComponents(
                claims_digest="test_claims_digest",
                write_set_digest="test_write_set_digest",
            ),
            proof=[
                ProofElement(
                    left="test_left",
                ),
            ],
            signature="test_signature",
        )


@pytest.mark.parametrize(
    "input_receipt_dict,expected_receipt",
    [
        [get_test_valid_receipt_1_dict(), get_test_valid_receipt_1()],
        [get_test_valid_receipt_2_dict(), get_test_valid_receipt_2()],
    ],
)
def test_receipt_creation_from_dict(input_receipt_dict, expected_receipt):

    receipt = Receipt.from_dict(_convert_dict_to_camel_case(input_receipt_dict))

    receipt.additional_properties = {}

    # Check that the receipt created from dict is the same as the expected receipt
    assert receipt == expected_receipt


@pytest.mark.parametrize(
    "input_receipt,expected_receipt_dict",
    [
        [get_test_valid_receipt_1(), get_test_valid_receipt_1_dict()],
        [get_test_valid_receipt_2(), get_test_valid_receipt_2_dict()],
    ],
)
def test_receipt_creation_to_dict(input_receipt, expected_receipt_dict):

    # Remove is_signature_transaction from expected receipt dict
    if "is_signature_transaction" in expected_receipt_dict:
        del expected_receipt_dict["is_signature_transaction"]

    # Check that the receipt dictionary created from a valid receipt is the same as the expected receipt
    assert Receipt.as_dict(input_receipt) == _convert_dict_to_camel_case(
        expected_receipt_dict
    )


@pytest.mark.parametrize(
    "input_receipt_dict,expected_receipt",
    [
        [get_test_valid_receipt_1_dict(), get_test_valid_receipt_1()],
        [get_test_valid_receipt_2_dict(), get_test_valid_receipt_2()],
    ],
)
def test_receipt_deserialization(input_receipt_dict, expected_receipt):

    receipt = Receipt.deserialize(_convert_dict_to_camel_case(input_receipt_dict))

    receipt.additional_properties = {}

    # Check that the receipt created from dict is the same as the expected receipt
    assert receipt == expected_receipt


@pytest.mark.parametrize(
    "input_receipt,expected_receipt_dict",
    [
        [get_test_valid_receipt_1(), get_test_valid_receipt_1_dict()],
        [get_test_valid_receipt_2(), get_test_valid_receipt_2_dict()],
    ],
)
def test_receipt_serialization(input_receipt, expected_receipt_dict):

    # Remove is_signature_transaction from expected receipt dict
    if "is_signature_transaction" in expected_receipt_dict:
        del expected_receipt_dict["is_signature_transaction"]

    # Check that the receipt dictionary created from a valid receipt is the same as the expected receipt
    assert Receipt.serialize(input_receipt) == _convert_dict_to_camel_case(
        expected_receipt_dict
    )
