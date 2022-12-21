# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Tests for receipt verification."""

from azure.confidentialledger.receiptverification.models import (
    LeafComponents,
    ProofElement,
)
import pytest

from azure.confidentialledger.receiptverification import (
    verify_receipt,
)
from azure.confidentialledger.receiptverification.exceptions import (
    EndorsementVerificationException,
    LeafNodeComputationException,
    ReceiptVerificationException,
    RootNodeComputationException,
    RootSignatureVerificationException,
)
from ._shared.constants import (
    get_test_valid_receipt_2,
    get_test_valid_service_certificate_2,
    get_test_valid_service_certificate_1,
    get_test_valid_receipt_1,
)


@pytest.mark.parametrize(
    "input_receipt,input_service_cert",
    [
        [get_test_valid_receipt_1(), get_test_valid_service_certificate_1()],
        [get_test_valid_receipt_2(), get_test_valid_service_certificate_2()],
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


@pytest.mark.parametrize("input_is_signature_transaction", [True, None])
def test_receipt_verification_with_signature_transaction_throws_exception(
    input_is_signature_transaction,
):

    # Create a receipt for a signature transaction
    receipt = get_test_valid_receipt_1()
    receipt.is_signature_transaction = input_is_signature_transaction

    # Check that verify_receipt throws ValueError
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(receipt, get_test_valid_service_certificate_1())

    assert type(exception.value.__cause__) is ValueError
    assert (
        exception.value.__cause__.args[0]
        == "Receipt verification for signature transactions is not supported."
    )


@pytest.mark.parametrize(
    "input_leaf_components",
    [
        None,
        LeafComponents(
            claims_digest="invalid_claims_digest",
            commit_evidence="invalid_commit_evidence",
            write_set_digest="invalid_write_set_digest",
        ),
        LeafComponents(
            claims_digest=get_test_valid_receipt_1().leaf_components.claims_digest,
            commit_evidence="invalid_commit_evidence",
            write_set_digest="invalid_write_set_digest",
        ),
        LeafComponents(
            claims_digest="invalid_claims_digest",
            commit_evidence="invalid_commit_evidence",
            write_set_digest=get_test_valid_receipt_1().leaf_components.write_set_digest,
        ),
    ],
)
def test_receipt_verification_with_invalid_leaf_components_throws_exception(
    input_leaf_components,
):

    # Create a receipt with invalid leaf components
    receipt = get_test_valid_receipt_1()
    receipt.leaf_components = input_leaf_components

    # Check that verify_receipt throws ReceiptVerificationException
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(receipt, get_test_valid_service_certificate_1())

    assert type(exception.value.__cause__) is LeafNodeComputationException
    assert (
        exception.value.__cause__.args[0]
        == f"Encountered exception when computing leaf node hash from leaf components {input_leaf_components}."
    )


@pytest.mark.parametrize("input_node_cert", [None, "invalid_cert_string"])
def test_receipt_verification_with_invalid_node_cert_throws_exception(input_node_cert):

    # Create a receipt with an invalid node certificate
    receipt = get_test_valid_receipt_1()
    receipt.cert = input_node_cert

    # Check that verify_receipt throws ReceiptVerificationException
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(receipt, get_test_valid_service_certificate_1())

    assert type(exception.value.__cause__) is ValueError
    assert (
        exception.value.__cause__.args[0]
        == f"PEM certificate {input_node_cert} is not valid."
    )


@pytest.mark.parametrize(
    "input_node_id", [None, "invalid_node_id", get_test_valid_receipt_2().node_id]
)
def test_receipt_verification_with_invalid_node_id_throws_exception(input_node_id):

    # Create a receipt with an invalid node id
    receipt = get_test_valid_receipt_1()
    receipt.node_id = input_node_id

    # Check that verify_receipt throws ReceiptVerificationException
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(receipt, get_test_valid_service_certificate_1())

    assert type(exception.value.__cause__) is RootSignatureVerificationException
    assert (
        "Encountered exception when verifying signature"
        in exception.value.__cause__.args[0]
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
    receipt = get_test_valid_receipt_1()
    receipt.proof = input_proof_list

    # Check that verify_receipt throws ReceiptVerificationException
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(receipt, get_test_valid_service_certificate_1())

    assert type(exception.value.__cause__) is RootNodeComputationException
    assert (
        exception.value.__cause__.args[0]
        == f"Encountered exception when computing root node hash from proof list {input_proof_list}."
    )


@pytest.mark.parametrize("input_endorsements_list", [None])
def test_receipt_verification_with_invalid_service_endorsements_throws_exception(
    input_endorsements_list,
):

    # Create a receipt with an invalid endorsements list
    receipt = get_test_valid_receipt_1()
    receipt.service_endorsements = input_endorsements_list

    # Check that verify_receipt throws ReceiptVerificationException
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(receipt, get_test_valid_service_certificate_1())

    assert type(exception.value.__cause__) is ValueError
    assert (
        exception.value.__cause__.args[0]
        == "Endorsements certificates list need to be present."
    )


@pytest.mark.parametrize(
    "input_signature", [None, get_test_valid_receipt_2().signature]
)
def test_receipt_verification_with_invalid_signature_throws_exception(input_signature):

    # Create a receipt with an invalid signature
    receipt = get_test_valid_receipt_1()
    receipt.signature = input_signature

    # Check that verify_receipt throws ReceiptVerificationException
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(receipt, get_test_valid_service_certificate_1())

    assert type(exception.value.__cause__) is RootSignatureVerificationException
    assert (
        exception.value.__cause__.args[0]
        == f"Encountered exception when verifying signature {input_signature} over root node hash."
    )


@pytest.mark.parametrize("input_service_cert", [None, "invalid_cert_string"])
def test_receipt_verification_with_invalid_service_cert_throws_exception(
    input_service_cert,
):

    # Check that verify_receipt throws ReceiptVerificationException with invalid service certificate
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(get_test_valid_receipt_1(), input_service_cert)

    assert type(exception.value.__cause__) is ValueError
    assert (
        exception.value.__cause__.args[0]
        == f"PEM certificate {input_service_cert} is not valid."
    )


@pytest.mark.parametrize("input_service_cert", [get_test_valid_service_certificate_2()])
def test_receipt_verification_with_unknown_service_cert_throws_exception(
    input_service_cert,
):

    # Check that verify_receipt throws ReceiptVerificationException with unknown service certificate
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(get_test_valid_receipt_1(), input_service_cert)

    assert type(exception.value.__cause__) is EndorsementVerificationException
    assert (
        "Encountered exception when verifying endorsement of certificate"
        in exception.value.__cause__.args[0]
    )


@pytest.mark.parametrize("input_node_cert", [get_test_valid_receipt_2().cert])
def test_receipt_verification_with_unknown_node_cert_throws_exception(input_node_cert):

    # Create a receipt with unknown node certificate
    receipt = get_test_valid_receipt_1()
    receipt.cert = input_node_cert

    # Check that verify_receipt throws ReceiptVerificationException
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(receipt, get_test_valid_service_certificate_1())

    assert type(exception.value.__cause__) is EndorsementVerificationException
    assert (
        "Encountered exception when verifying endorsement of certificate"
        in exception.value.__cause__.args[0]
    )


@pytest.mark.parametrize(
    "input_endorsements_list", [[get_test_valid_service_certificate_2()]]
)
def test_receipt_verification_with_unknown_service_endorsements_throws_exception(
    input_endorsements_list,
):

    # Create a receipt with unknown endorsements list
    receipt = get_test_valid_receipt_1()
    receipt.service_endorsements = input_endorsements_list

    # Check that verify_receipt throws ReceiptVerificationException
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(receipt, get_test_valid_service_certificate_1())

    assert type(exception.value.__cause__) is EndorsementVerificationException
    assert (
        "Encountered exception when verifying endorsement of certificate"
        in exception.value.__cause__.args[0]
    )


@pytest.mark.parametrize(
    "input_leaf_components", [get_test_valid_receipt_2().leaf_components]
)
def test_receipt_verification_with_unknown_leaf_components_throws_exception(
    input_leaf_components,
):

    # Create a receipt with unknown leaf components
    receipt = get_test_valid_receipt_1()
    receipt.leaf_components = input_leaf_components

    # Check that verify_receipt throws ReceiptVerificationException
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(receipt, get_test_valid_service_certificate_1())

    assert type(exception.value.__cause__) is RootSignatureVerificationException
    assert (
        "Encountered exception when verifying signature"
        in exception.value.__cause__.args[0]
    )


@pytest.mark.parametrize("input_proof_list", [[], get_test_valid_receipt_2().proof])
def test_receipt_verification_with_unknown_proof_list_throws_exception(
    input_proof_list,
):

    # Create a receipt with unknown proof list
    receipt = get_test_valid_receipt_1()
    receipt.proof = input_proof_list

    # Check that verify_receipt throws ReceiptVerificationException
    with pytest.raises(
        ReceiptVerificationException,
        match="Encountered exception when verifying receipt",
    ) as exception:
        verify_receipt(receipt, get_test_valid_service_certificate_1())

    assert type(exception.value.__cause__) is RootSignatureVerificationException
    assert (
        "Encountered exception when verifying signature"
        in exception.value.__cause__.args[0]
    )
