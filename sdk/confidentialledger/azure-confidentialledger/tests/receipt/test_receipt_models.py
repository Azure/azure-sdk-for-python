# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Tests for models used for receipt application claims verification."""

import pytest

from azure.confidentialledger.receipt._receipt_models import (
    LeafComponents,
    ProofElement,
    Receipt,
)

from azure.confidentialledger.receipt._utils import (
    _convert_dict_to_camel_case,
)

from ._shared.receipt_constants import (
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
        )
    except Exception as e:
        pytest.fail(f"Receipt __init__ threw an exception with a valid receipt {e}")


def test_receipt_init_throws_exceptions_with_missing_required_fields():
    # Throws exception when missing different required fields
    with pytest.raises(TypeError, match="missing . required .* argument"):
        Receipt(
            signature="test_signature",
        )


def test_receipt_init_throws_exceptions_with_missing_required_fields_in_subobjects():
    # Throws exception when missing required fields inside LeafComponents
    with pytest.raises(TypeError, match="missing . required .* argument"):
        Receipt(
            is_signature_transaction=False,
            cert="test_cert",
            nodeId="test_node_id",
            serviceEndorsements=[],
            leafComponents=LeafComponents(
                claimsDigest="test_claims_digest",
                writeSetDigest="test_write_set_digest",
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

    # Check that the receipt created from dict is the same as the expected receipt
    assert receipt == expected_receipt
