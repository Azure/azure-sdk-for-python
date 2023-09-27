# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Tests for receipt verification."""

import pytest

from azure.confidentialledger.receipt._receipt_verification import (
    verify_receipt,
)

from azure.confidentialledger.receipt._receipt_models import (
    LeafComponents,
    ProofElement,
)

from ._shared.receipt_constants import (
    get_test_valid_receipt_1_dict,
    get_test_valid_receipt_2_dict,
    get_test_valid_service_certificate_2,
    get_test_valid_service_certificate_1,
)

from ._shared.claims_constants import (
    get_test_application_claims_with_claim_digest_dict,
    get_test_application_claims_with_ledger_entry_dict,
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


@pytest.mark.parametrize(
    "input_receipt,input_service_cert,input_claims",
    [
        [
            {
                "cert": "-----BEGIN CERTIFICATE-----\nMIIBxTCCAUygAwIBAgIRAMR89lUNeIghDUfpyHi3QzIwCgYIKoZIzj0EAwMwFjEU\nMBIGA1UEAwwLQ0NGIE5ldHdvcmswHhcNMjMwNDI1MTgxNDE5WhcNMjMwNzI0MTgx\nNDE4WjATMREwDwYDVQQDDAhDQ0YgTm9kZTB2MBAGByqGSM49AgEGBSuBBAAiA2IA\nBB1DiBUBr9/qapmvAIPm1o3o3LRViSOkfFVI4oPrw3SodLlousHrLz+HIe+BqHoj\n4nBjt0KAS2C0Av6Q+Xg5Po6GCu99GQSoSfajGqmjy3j3bwjsGJi5wHh1pNbPmMm/\nTqNhMF8wDAYDVR0TAQH/BAIwADAdBgNVHQ4EFgQUCPaDohOGjVgQ2Lb8Pmubg7Y5\nDJAwHwYDVR0jBBgwFoAU25KejcEmXDNnKvSLUwW/CQZIVq4wDwYDVR0RBAgwBocE\nfwAAATAKBggqhkjOPQQDAwNnADBkAjA8Ci9myzieoLoIy+7mUswVEjUG3wrEXtxA\nDRmt2PK9bTDo2m3aJ4nCQJtCWQRUlN0CMCMOsXL4NnfsSxaG5CwAVkDwLBUPv7Zy\nLfSh2oZ3Wn4FTxL0UfnJeFOz/CkDUtJI1A==\n-----END CERTIFICATE-----\n",
                "leafComponents": {
                    "claimsDigest": "d08d8764437d09b2d4d07d52293cddaf40f44a3ea2176a0528819a80002df9f6",
                    "commitEvidence": "ce:2.13:850a25da46643fa41392750b6ca03c7c7d117c27ae14e3322873de6322aa7cd3",
                    "writeSetDigest": "6637eddb8741ab54cc8a44725be67fd9be390e605f0537e5a278703860ace035",
                },
                "nodeId": "0db9a22e9301d1167a2a81596fa234642ad24bc742451a415b8d653af056795c",
                "proof": [
                    {
                        "left": "bcce25aa51854bd15257cfb0c81edc568a5a5fa3b81e7106c125649db93ff599"
                    },
                    {
                        "left": "cc82daa27e76b7525a1f37ed7379bb80f6aab99f2b36e2e06c750dd9393cd51b"
                    },
                    {
                        "left": "c53a15cbcc97e30ce748c0f44516ac3440e3e9cc19db0852f3aa3a3d5554dfae"
                    },
                ],
                "signature": "MGYCMQClZXVAFn+vflIIikwMz64YZGoH71DKnfMr3LXkQ0lhljSsvDrmtmi/oWwOsqy28PsCMQCMe4n9aXXK4R+vY0SIfRWSCCfaADD6teclFCkVNK4317ep+5ENM/5T/vDJf3V4IvI=",
            },
            "-----BEGIN CERTIFICATE-----\nMIIBvTCCAUOgAwIBAgIQGgBXsl9DwUaREaZ/qyKevDAKBggqhkjOPQQDAzAWMRQw\nEgYDVQQDDAtDQ0YgTmV0d29yazAeFw0yMzA0MjUxODE0MTlaFw0yMzA3MjQxODE0\nMThaMBYxFDASBgNVBAMMC0NDRiBOZXR3b3JrMHYwEAYHKoZIzj0CAQYFK4EEACID\nYgAER8wP5Jm3xNdLjOmVJllpAqhE+rSG8RUpLqpYpThB7MlggAZkhekDQz6G27ma\n6fqqJQH1rJciopwuDVRVGMIb6iSxrrQ1CuDzqGs5t2sbyRmylicldebkmk9FTY1P\n0vIlo1YwVDASBgNVHRMBAf8ECDAGAQH/AgEAMB0GA1UdDgQWBBTbkp6NwSZcM2cq\n9ItTBb8JBkhWrjAfBgNVHSMEGDAWgBTbkp6NwSZcM2cq9ItTBb8JBkhWrjAKBggq\nhkjOPQQDAwNoADBlAjAHTALS7/P02s1AeSWQHrVZdgz9F++NjFa0cea7TjLa1aPl\n/Hr20J6fjuFgK0GPn+ECMQDnsje32P4rKabgSgX4GPd5h97zuZp4o1QQJJ4hrjy4\nxQY4JS7/UrUrqpITDL082Vk=\n-----END CERTIFICATE-----\n",
            [
                {
                    "kind": "LedgerEntry",
                    "ledgerEntry": {
                        "collectionId": "subledger:0",
                        "contents": "Hello world",
                        "protocol": "LedgerEntryV1",
                        "secretKey": "Jde/VvaIfyrjQ/B19P+UJCBwmcrgN7sERStoyHnYO0M=",
                    },
                }
            ],
        ],
        [
            {
                "cert": "-----BEGIN CERTIFICATE-----\nMIIBxTCCAUygAwIBAgIRAMR89lUNeIghDUfpyHi3QzIwCgYIKoZIzj0EAwMwFjEU\nMBIGA1UEAwwLQ0NGIE5ldHdvcmswHhcNMjMwNDI1MTgxNDE5WhcNMjMwNzI0MTgx\nNDE4WjATMREwDwYDVQQDDAhDQ0YgTm9kZTB2MBAGByqGSM49AgEGBSuBBAAiA2IA\nBB1DiBUBr9/qapmvAIPm1o3o3LRViSOkfFVI4oPrw3SodLlousHrLz+HIe+BqHoj\n4nBjt0KAS2C0Av6Q+Xg5Po6GCu99GQSoSfajGqmjy3j3bwjsGJi5wHh1pNbPmMm/\nTqNhMF8wDAYDVR0TAQH/BAIwADAdBgNVHQ4EFgQUCPaDohOGjVgQ2Lb8Pmubg7Y5\nDJAwHwYDVR0jBBgwFoAU25KejcEmXDNnKvSLUwW/CQZIVq4wDwYDVR0RBAgwBocE\nfwAAATAKBggqhkjOPQQDAwNnADBkAjA8Ci9myzieoLoIy+7mUswVEjUG3wrEXtxA\nDRmt2PK9bTDo2m3aJ4nCQJtCWQRUlN0CMCMOsXL4NnfsSxaG5CwAVkDwLBUPv7Zy\nLfSh2oZ3Wn4FTxL0UfnJeFOz/CkDUtJI1A==\n-----END CERTIFICATE-----\n",
                "leafComponents": {
                    "claimsDigest": "d08d8764437d09b2d4d07d52293cddaf40f44a3ea2176a0528819a80002df9f6",
                    "commitEvidence": "ce:2.13:850a25da46643fa41392750b6ca03c7c7d117c27ae14e3322873de6322aa7cd3",
                    "writeSetDigest": "6637eddb8741ab54cc8a44725be67fd9be390e605f0537e5a278703860ace035",
                },
                "nodeId": "0db9a22e9301d1167a2a81596fa234642ad24bc742451a415b8d653af056795c",
                "proof": [
                    {
                        "left": "bcce25aa51854bd15257cfb0c81edc568a5a5fa3b81e7106c125649db93ff599"
                    },
                    {
                        "left": "cc82daa27e76b7525a1f37ed7379bb80f6aab99f2b36e2e06c750dd9393cd51b"
                    },
                    {
                        "left": "c53a15cbcc97e30ce748c0f44516ac3440e3e9cc19db0852f3aa3a3d5554dfae"
                    },
                ],
                "signature": "MGYCMQClZXVAFn+vflIIikwMz64YZGoH71DKnfMr3LXkQ0lhljSsvDrmtmi/oWwOsqy28PsCMQCMe4n9aXXK4R+vY0SIfRWSCCfaADD6teclFCkVNK4317ep+5ENM/5T/vDJf3V4IvI=",
            },
            "-----BEGIN CERTIFICATE-----\nMIIBvTCCAUOgAwIBAgIQGgBXsl9DwUaREaZ/qyKevDAKBggqhkjOPQQDAzAWMRQw\nEgYDVQQDDAtDQ0YgTmV0d29yazAeFw0yMzA0MjUxODE0MTlaFw0yMzA3MjQxODE0\nMThaMBYxFDASBgNVBAMMC0NDRiBOZXR3b3JrMHYwEAYHKoZIzj0CAQYFK4EEACID\nYgAER8wP5Jm3xNdLjOmVJllpAqhE+rSG8RUpLqpYpThB7MlggAZkhekDQz6G27ma\n6fqqJQH1rJciopwuDVRVGMIb6iSxrrQ1CuDzqGs5t2sbyRmylicldebkmk9FTY1P\n0vIlo1YwVDASBgNVHRMBAf8ECDAGAQH/AgEAMB0GA1UdDgQWBBTbkp6NwSZcM2cq\n9ItTBb8JBkhWrjAfBgNVHSMEGDAWgBTbkp6NwSZcM2cq9ItTBb8JBkhWrjAKBggq\nhkjOPQQDAwNoADBlAjAHTALS7/P02s1AeSWQHrVZdgz9F++NjFa0cea7TjLa1aPl\n/Hr20J6fjuFgK0GPn+ECMQDnsje32P4rKabgSgX4GPd5h97zuZp4o1QQJJ4hrjy4\nxQY4JS7/UrUrqpITDL082Vk=\n-----END CERTIFICATE-----\n",
            [
                {
                    "kind": "ClaimDigest",
                    "digest": {
                        "protocol": "LedgerEntryV1",
                        "value": "feb516ef1f903c64f1e388d9ee9fde11f64d1e2bc170248828c9eab9894f9ab9",
                    },
                }
            ],
        ],
    ],
)
def test_receipt_verification_with_valid_application_claims_returns_successfully(
    input_receipt, input_service_cert, input_claims
):
    # Check that verify_receipt does not throw any exception
    # with a valid receipt, service certificate, and application claims
    try:
        verify_receipt(
            input_receipt, input_service_cert, application_claims=input_claims
        )
    except Exception as e:
        pytest.fail(
            f"verify_receipt threw an exception with a valid receipt, service certificate, and application claims {e}"
        )


@pytest.mark.parametrize(
    "input_receipt,input_service_cert,input_claims",
    [
        [
            get_test_valid_receipt_1_dict(),
            get_test_valid_service_certificate_1(),
            get_test_application_claims_with_claim_digest_dict(),
        ],
        [
            get_test_valid_receipt_2_dict(),
            get_test_valid_service_certificate_2(),
            get_test_application_claims_with_ledger_entry_dict(),
        ],
    ],
)
def test_receipt_verification_with_invalid_application_claims_throws_exception(
    input_receipt, input_service_cert, input_claims
):
    # Check that verify_receipt throws ValueError
    with pytest.raises(
        ValueError,
    ):
        verify_receipt(
            input_receipt, input_service_cert, application_claims=input_claims
        )
