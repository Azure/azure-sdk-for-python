# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Tests for application claims."""

import pytest

from azure.confidentialledger.receipt._claims_digest_computation import (
    compute_claims_digest,
)


from ._shared.claims_constants import (
    get_test_application_claims_with_claim_digest_dict,
    get_test_application_claims_with_ledger_entry_dict,
)


@pytest.mark.parametrize(
    "input_claims",
    [
        get_test_application_claims_with_claim_digest_dict(),
        get_test_application_claims_with_ledger_entry_dict(),
        [
            get_test_application_claims_with_claim_digest_dict()[0],
            get_test_application_claims_with_ledger_entry_dict()[0],
        ],
    ],
)
def test_claims_digest_computation_with_valid_claims_returns_successfully(input_claims):
    # Check that compute_claims_digest does not throw any exception
    # with valid claims
    try:
        compute_claims_digest(input_claims)
    except Exception as e:
        pytest.fail(f"compute_claims_digest threw an exception with valid claims {e}")


@pytest.mark.parametrize(
    "input_claims",
    [
        None,
        {},
        [],
        [
            {
                "unknown_key": "unknown_value",
            }
        ],
        [
            {
                "digest": {},
            }
        ],
    ],
)
def test_claims_digest_computation_with_invalid_claim_throws_exception(input_claims):
    # Check that compute_claims_digest throws AssertionError
    with pytest.raises(
        AssertionError,
    ):
        compute_claims_digest(input_claims)


@pytest.mark.parametrize(
    "input_claim_kind,input_claims",
    [
        [None, get_test_application_claims_with_ledger_entry_dict()],
        [None, get_test_application_claims_with_claim_digest_dict()],
        ["invalid_claim_kind", get_test_application_claims_with_ledger_entry_dict()],
        ["invalid_claim_kind", get_test_application_claims_with_claim_digest_dict()],
    ],
)
def test_claims_digest_computation_with_invalid_kind_throws_exception(
    input_claim_kind, input_claims
):
    # Create a claim with an invalid kind
    input_claims[0]["kind"] = input_claim_kind

    # Check that compute_claims_digest throws AssertionError
    with pytest.raises(
        AssertionError,
    ):
        compute_claims_digest(input_claims)


@pytest.mark.parametrize(
    "input_ledger_entry_claim,input_claims",
    [
        [None, get_test_application_claims_with_ledger_entry_dict()],
        [
            {
                "collectionId": "invalid_collection",
                "contents": "invalid_contents",
                "secretKey": "invalid_secret_key",
            },
            get_test_application_claims_with_ledger_entry_dict(),
        ],
        [
            {
                "protocol": get_test_application_claims_with_ledger_entry_dict()[0][
                    "ledgerEntry"
                ]["protocol"],
                "contents": "invalid_contents",
            },
            get_test_application_claims_with_ledger_entry_dict(),
        ],
    ],
)
def test_claims_digest_computation_with_invalid_ledger_entry_claim_throws_exception(
    input_ledger_entry_claim, input_claims
):
    # Create a claim with invalid ledger entry claim
    input_claims[0]["ledgerEntry"] = input_ledger_entry_claim

    # Check that compute_claims_digest throws AssertionError
    with pytest.raises(
        AssertionError,
    ):
        compute_claims_digest(input_claims)


@pytest.mark.parametrize(
    "input_ledger_entry_protocol,input_claims",
    [
        ["invalid_protocol", get_test_application_claims_with_ledger_entry_dict()],
    ],
)
def test_claims_digest_computation_with_invalid_ledger_entry_claim_protocol_throws_exception(
    input_ledger_entry_protocol, input_claims
):
    # Create a claim with invalid ledger entry claim protocol
    input_claims[0]["ledgerEntry"]["protocol"] = input_ledger_entry_protocol

    # Check that compute_claims_digest throws ValueError
    with pytest.raises(
        ValueError,
    ):
        compute_claims_digest(input_claims)


@pytest.mark.parametrize(
    "input_ledger_entry_secret_key,input_claims",
    [
        ["invalid_key", get_test_application_claims_with_ledger_entry_dict()],
    ],
)
def test_claims_digest_computation_with_invalid_ledger_entry_claim_secret_key_throws_exception(
    input_ledger_entry_secret_key, input_claims
):
    # Create a claim with invalid ledger entry claim secret key
    input_claims[0]["ledgerEntry"]["secretKey"] = input_ledger_entry_secret_key

    # Check that compute_claims_digest throws ValueError
    with pytest.raises(
        ValueError,
    ):
        compute_claims_digest(input_claims)


@pytest.mark.parametrize(
    "input_digest_claim,input_claims",
    [
        [None, get_test_application_claims_with_claim_digest_dict()],
        [
            {
                "value": "invalid_value",
                "contents": "invalid_contents",
            },
            get_test_application_claims_with_claim_digest_dict(),
        ],
        [
            {
                "protocol": get_test_application_claims_with_claim_digest_dict()[0][
                    "digest"
                ]["protocol"],
            },
            get_test_application_claims_with_claim_digest_dict(),
        ],
    ],
)
def test_claims_digest_computation_with_invalid_digest_claim_throws_exception(
    input_digest_claim, input_claims
):
    # Create a claim with invalid digest claim
    input_claims[0]["digest"] = input_digest_claim

    # Check that compute_claims_digest throws AssertionError
    with pytest.raises(
        AssertionError,
    ):
        compute_claims_digest(input_claims)


@pytest.mark.parametrize(
    "input_digest_protocol,input_claims",
    [
        ["invalid_protocol", get_test_application_claims_with_claim_digest_dict()],
    ],
)
def test_claims_digest_computation_with_unknown_digest_claim_protocol_does_not_throw_exception(
    input_digest_protocol, input_claims
):
    # Create a claim with invalid digest claim protocol
    input_claims[0]["digest"]["protocol"] = input_digest_protocol

    # Check that compute_claims_digest does not throw any exception
    try:
        compute_claims_digest(input_claims)
    except Exception as e:
        pytest.fail(f"compute_claims_digest threw an exception with valid claims {e}")
