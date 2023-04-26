# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Tests for receipt verification."""

import pytest

from azure.confidentialledger.receipt._receipt_verification import (
    verify_receipt,
)

from azure.confidentialledger.receipt._models import (
    LeafComponents,
    ProofElement,
)

from ._shared.constants import (
    get_test_valid_receipt_1_dict,
    get_test_valid_receipt_2_dict,
    get_test_valid_service_certificate_2,
    get_test_valid_service_certificate_1,
)


@pytest.mark.parametrize(
    "input_receipt,input_service_cert",
    [
        [get_test_valid_receipt_1_dict(), get_test_valid_service_certificate_1()],
        [get_test_valid_receipt_2_dict(), get_test_valid_service_certificate_2()],
    ],
)
def test_receipt_verification_with_valid_receipt_returns_successfully(
    input_receipt, input_service_cert
):

    # Check that verify_receipt does not throw any exception
    # with a valid receipt and service certificate
    try:
        verify_receipt(input_receipt, input_service_cert)
    except Exception as e:
        pytest.fail(
            f"verify_receipt threw an exception with a valid receipt and service certificate {e}"
        )


@pytest.mark.parametrize(
    "input_leaf_components",
    [
        None,
        LeafComponents(
            claimsDigest="invalid_claims_digest",
            commitEvidence="invalid_commit_evidence",
            writeSetDigest="invalid_write_set_digest",
        ),
        LeafComponents(
            claimsDigest=get_test_valid_receipt_1_dict()["leaf_components"][
                "claims_digest"
            ],
            commitEvidence="invalid_commit_evidence",
            writeSetDigest="invalid_write_set_digest",
        ),
        LeafComponents(
            claimsDigest="invalid_claims_digest",
            commitEvidence="invalid_commit_evidence",
            writeSetDigest=get_test_valid_receipt_1_dict()["leaf_components"][
                "write_set_digest"
            ],
        ),
    ],
)
def test_receipt_verification_with_invalid_leaf_components_throws_exception(
    input_leaf_components,
):

    # Create a receipt with invalid leaf components
    receipt = get_test_valid_receipt_1_dict()
    receipt["leafComponents"] = input_leaf_components

    # Check that verify_receipt throws ValueError
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(receipt, get_test_valid_service_certificate_1())


@pytest.mark.parametrize("input_node_cert", [None, "invalid_cert_string"])
def test_receipt_verification_with_invalid_node_cert_throws_exception(input_node_cert):

    # Create a receipt with an invalid node certificate
    receipt = get_test_valid_receipt_1_dict()
    receipt["cert"] = input_node_cert

    # Check that verify_receipt throws ValueError
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(receipt, get_test_valid_service_certificate_1())


@pytest.mark.parametrize(
    "input_node_id",
    [None, "invalid_node_id", get_test_valid_receipt_2_dict()["nodeId"]],
)
def test_receipt_verification_with_invalid_node_id_throws_exception(input_node_id):

    # Create a receipt with an invalid node id
    receipt = get_test_valid_receipt_1_dict()
    receipt["node_id"] = input_node_id

    # Check that verify_receipt throws ValueError
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(receipt, get_test_valid_service_certificate_1())


def test_receipt_verification_with_missing_node_id_does_not_throw_exception():

    # Create a receipt with an invalid node id
    receipt = get_test_valid_receipt_1_dict()
    del receipt["node_id"]

    # Check that verify_receipt does throw any exception
    try:
        verify_receipt(receipt, get_test_valid_service_certificate_1())
    except Exception as e:
        pytest.fail(
            f"verify_receipt threw an exception with a valid receipt and service certificate {e}"
        )


@pytest.mark.parametrize(
    "input_proof_list",
    [
        None,
        [ProofElement()],
        [ProofElement(right="invalid_node_hash")],
        [ProofElement(right="invalid_node_hash")],
        [ProofElement(left="invalid_node_hash", right="invalid_node_hash")],
    ],
)
def test_receipt_verification_with_invalid_proof_list_throws_exception(
    input_proof_list,
):

    # Create a receipt with an invalid proof list
    receipt = get_test_valid_receipt_1_dict()
    receipt["proof"] = input_proof_list

    # Check that verify_receipt throws ValueError
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(receipt, get_test_valid_service_certificate_1())


@pytest.mark.parametrize("input_endorsements_list", [1, 2])
def test_receipt_verification_with_invalid_service_endorsements_throws_exception(
    input_endorsements_list,
):

    # Create a receipt with a null endorsements list
    receipt = get_test_valid_receipt_1_dict()
    receipt["service_endorsements"] = input_endorsements_list

    # Check that verify_receipt throws ValueError
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(receipt, get_test_valid_service_certificate_1())


def test_receipt_verification_with_missing_service_endorsements_does_not_throw_exception():

    # Create a receipt and remove the endorsements list
    receipt = get_test_valid_receipt_1_dict()
    del receipt["service_endorsements"]

    # Check that verify_receipt does throw any exception
    try:
        verify_receipt(receipt, get_test_valid_service_certificate_1())
    except Exception as e:
        pytest.fail(
            f"verify_receipt threw an exception with a valid receipt and service certificate {e}"
        )


@pytest.mark.parametrize(
    "input_signature", [None, get_test_valid_receipt_2_dict()["signature"]]
)
def test_receipt_verification_with_invalid_signature_throws_exception(input_signature):

    # Create a receipt with an invalid signature
    receipt = get_test_valid_receipt_1_dict()
    receipt["signature"] = input_signature

    # Check that verify_receipt throws ValueError
    with pytest.raises(ValueError):
        verify_receipt(receipt, get_test_valid_service_certificate_1())


@pytest.mark.parametrize("input_service_cert", [None, "invalid_cert_string"])
def test_receipt_verification_with_invalid_service_cert_throws_exception(
    input_service_cert,
):

    # Check that verify_receipt throws ValueError with invalid service certificate
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(get_test_valid_receipt_1_dict(), input_service_cert)


@pytest.mark.parametrize("input_service_cert", [get_test_valid_service_certificate_2()])
def test_receipt_verification_with_unknown_service_cert_throws_exception(
    input_service_cert,
):

    # Check that verify_receipt throws ValueError with unknown service certificate
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(get_test_valid_receipt_1_dict(), input_service_cert)


@pytest.mark.parametrize("input_node_cert", [get_test_valid_receipt_2_dict()["cert"]])
def test_receipt_verification_with_unknown_node_cert_throws_exception(input_node_cert):

    # Create a receipt with unknown node certificate
    receipt = get_test_valid_receipt_1_dict()
    receipt["cert"] = input_node_cert

    # Check that verify_receipt throws ValueError
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(receipt, get_test_valid_service_certificate_1())


@pytest.mark.parametrize(
    "input_endorsements_list", [[get_test_valid_service_certificate_2()]]
)
def test_receipt_verification_with_unknown_service_endorsements_throws_exception(
    input_endorsements_list,
):

    # Create a receipt with unknown endorsements list
    receipt = get_test_valid_receipt_1_dict()
    receipt["service_endorsements"] = input_endorsements_list

    # Check that verify_receipt throws ValueError
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(receipt, get_test_valid_service_certificate_1())


@pytest.mark.parametrize(
    "input_leaf_components", [get_test_valid_receipt_2_dict()["leafComponents"]]
)
def test_receipt_verification_with_unknown_leaf_components_throws_exception(
    input_leaf_components,
):

    # Create a receipt with unknown leaf components
    receipt = get_test_valid_receipt_1_dict()
    receipt["leafComponents"] = input_leaf_components

    # Check that verify_receipt throws ValueError
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(receipt, get_test_valid_service_certificate_1())


@pytest.mark.parametrize(
    "input_proof_list", [[], get_test_valid_receipt_2_dict()["proof"]]
)
def test_receipt_verification_with_unknown_proof_list_throws_exception(
    input_proof_list,
):

    # Create a receipt with unknown proof list
    receipt = get_test_valid_receipt_1_dict()
    receipt["proof"] = input_proof_list

    # Check that verify_receipt throws ValueError
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(receipt, get_test_valid_service_certificate_1())
