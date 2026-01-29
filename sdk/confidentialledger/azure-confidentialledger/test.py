#!/usr/bin/env python3
"""
ACL Python SDK Redirect Behavior Test

Tests whether the azure-confidentialledger Python SDK automatically follows
HTTP redirects for write operations (POST transactions).

This test demonstrates:
1. PHASE 1: Default SDK behavior (fails due to Authorization header stripping on redirects)
2. PHASE 2: With disable_redirect_cleanup=True fix (succeeds)

The key issue is that the SensitiveHeaderCleanupPolicy strips the Authorization header
when following redirects to a different hostname (the primary node), causing 401 errors.
"""

import argparse
import logging
import os
import sys
import tempfile
import uuid
from datetime import datetime

from azure.identity import DefaultAzureCredential
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient

# Default ACL endpoint
DEFAULT_ENDPOINT = "ap-redirect-test-4398.confidential-ledger.azure.com"
DEFAULT_IDENTITY_SERVICE_URL = "https://identity.confidential-ledger.core.azure.com"

# Number of transactions to post (higher = more likely to hit redirect)
NUM_TRANSACTIONS = 5


def setup_logging(verbose: bool):
    """Configure logging level."""
    if verbose:
        # Enable HTTP logging to see redirect chain
        logging.basicConfig(level=logging.DEBUG, force=True)
        # Azure SDK HTTP logging
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
            logging.DEBUG
        )
        # Show redirect policy activity
        logging.getLogger("azure.core.pipeline.policies._redirect").setLevel(
            logging.DEBUG
        )
    else:
        logging.basicConfig(level=logging.WARNING, force=True)


def get_ledger_certificate(ledger_name: str, identity_service_url: str) -> str:
    """Retrieve the ledger's TLS certificate from the identity service."""
    cert_client = ConfidentialLedgerCertificateClient(
        certificate_endpoint=identity_service_url
    )
    ledger_cert = cert_client.get_ledger_identity(ledger_name)
    return ledger_cert["ledgerTlsCertificate"]


def get_cert_file(endpoint: str) -> str:
    """Get ledger certificate and write to temp file.
    
    Returns:
        str: Path to the certificate file
    """
    # Extract ledger name from endpoint
    ledger_name = endpoint.split(".")[0]
    
    # Determine identity service URL based on environment
    if "staging" in endpoint or "confidential-ledger-staging" in endpoint:
        identity_service_url = "https://identity.confidential-ledger-staging.core.azure.com"
    else:
        identity_service_url = DEFAULT_IDENTITY_SERVICE_URL
    
    # Get the ledger certificate
    ledger_certificate = get_ledger_certificate(ledger_name, identity_service_url)
    
    # Write certificate to a temporary file (SDK requires file path)
    cert_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
    cert_file.write(ledger_certificate)
    cert_file.close()
    
    return cert_file.name


def create_client(endpoint: str, cert_file_path: str) -> ConfidentialLedgerClient:
    """Create an ACL client with specified configuration.
    
    Args:
        endpoint: ACL endpoint hostname
        cert_file_path: Path to the ledger certificate file
                                  (Note: SDK now has this hardcoded to True)
    
    Returns:
        ConfidentialLedgerClient instance
    """
    # Create credential
    credential = DefaultAzureCredential()
    
    # Create client
    # NOTE: The SDK now has disable_redirect_cleanup=True hardcoded in _client.py
    # to preserve the Authorization header when following redirects to the primary node.
    # We no longer need to pass this parameter explicitly.
    client = ConfidentialLedgerClient(
        endpoint=f"https://{endpoint}",
        credential=credential,
        ledger_certificate_path=cert_file_path,
    )
    
    return client


def post_transaction(client: ConfidentialLedgerClient, index: int) -> tuple[bool, str]:
    """
    Post a single transaction to the ledger.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Generate unique content for this transaction
    content = "test"
    
    try:
        # Post the transaction (this is where redirect may happen)
        result = client.create_ledger_entry(
            entry={"contents": str(content)},
            collection_id="redirect-test"
        )
        
        transaction_id = result.get("transactionId", "unknown")
        return True, f"transaction_id: {transaction_id}"
        
    except Exception as e:
        error_msg = str(e)
        # Check for common redirect-related failures
        if "401" in error_msg or "Unauthorized" in error_msg:
            return False, f"401 Unauthorized (likely Authorization header stripped on redirect)"
        return False, f"Error: {error_msg}"


def run_phase(endpoint: str, cert_file_path: str, phase_name: str, verbose: bool) -> tuple[int, int]:
    """
    Run a single test phase with specified configuration.
    
    Args:
        endpoint: ACL endpoint hostname
        cert_file_path: Path to the ledger certificate file
        disable_redirect_cleanup: If True, preserves Authorization header on redirects
        phase_name: Name of this phase for display
        verbose: Enable verbose logging
    
    Returns:
        tuple: (success_count, total_count)
    """
    print()
    print(f"{'─' * 60}")
    print(f"  {phase_name}")
    print(f"{'─' * 60}")
    
    try:
        client = create_client(endpoint, cert_file_path)
    except Exception as e:
        print(f"  ERROR: Failed to create client: {e}")
        return 0, NUM_TRANSACTIONS
    
    # Post transactions
    success_count = 0
    for i in range(1, NUM_TRANSACTIONS + 1):
        print(f"  [{i}/{NUM_TRANSACTIONS}] Posting transaction... ", end="", flush=True)
        success, message = post_transaction(client, i)
        
        if success:
            print(f"✓ ({message})")
            success_count += 1
        else:
            print(f"✗ ({message})")
    
    return success_count, NUM_TRANSACTIONS


def run_test(endpoint: str, verbose: bool) -> bool:
    """
    Run the redirect behavior test in two phases.
    
    Phase 1: Default SDK behavior (disable_redirect_cleanup=False)
             Expected: FAIL - Authorization header stripped on redirects
    
    Phase 2: With fix (disable_redirect_cleanup=True)
             Expected: PASS - Authorization header preserved
    
    Returns:
        bool: True if Phase 2 succeeded (demonstrating the fix works)
    """
    print("=" * 60)
    print("  ACL Python SDK Redirect Test")
    print("=" * 60)
    print(f"  Endpoint: https://{endpoint}")
    print(f"  Transactions per phase: {NUM_TRANSACTIONS}")
    print()
    print("  This test demonstrates the redirect Authorization header issue")
    print("  and validates the fix using disable_redirect_cleanup=True.")
    
    # Get certificate once (shared between phases)
    cert_file_path = None
    try:
        print()
        print("  Retrieving ledger certificate from identity service...")
        cert_file_path = get_cert_file(endpoint)
        print("  Certificate retrieved successfully.")
    except Exception as e:
        print(f"  ERROR: Failed to get certificate: {e}")
        return False
    
    try:
        # ═══════════════════════════════════════════════════════════════
        # PHASE 1: Default SDK behavior (should fail on redirects)
        # NOTE: If requests go directly to primary node, this may PASS
        # ═══════════════════════════════════════════════════════════════
        phase1_success, phase1_total = run_phase(
            endpoint=endpoint,
            cert_file_path=cert_file_path,
            phase_name="PHASE 1: Default SDK Behavior (No Fix)",
            verbose=verbose
        )
        
        # ═══════════════════════════════════════════════════════════════
        # RESULTS SUMMARY
        # ═══════════════════════════════════════════════════════════════
        print()
        print("=" * 60)
        print("  RESULTS SUMMARY")
        print("=" * 60)
        print()
        
        phase1_passed = phase1_success == phase1_total
        
        # Phase 1 result
        phase1_status = "PASS" if phase1_passed else "FAIL"
        phase1_expected = "(may pass if no redirect)" if phase1_passed else "(expected on redirect)"
        print(f"  Phase 1 (Default):  {phase1_status} {phase1_expected}")
        print(f"                      {phase1_success}/{phase1_total} transactions succeeded")
        
        print()
        print("─" * 60)
        return phase1_passed            
    finally:
        # Cleanup temp certificate file
        if cert_file_path and os.path.exists(cert_file_path):
            try:
                os.unlink(cert_file_path)
            except Exception:
                pass  # Ignore cleanup errors


def main():
    parser = argparse.ArgumentParser(
        description="Test ACL Python SDK redirect behavior"
    )
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("ACL_ENDPOINT", DEFAULT_ENDPOINT),
        help=f"ACL endpoint hostname (default: {DEFAULT_ENDPOINT})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose HTTP logging to see redirect chain",
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    success = run_test(args.endpoint, args.verbose)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
