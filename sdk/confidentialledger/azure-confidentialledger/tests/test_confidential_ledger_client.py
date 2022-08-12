import hashlib
import os
import time
from typing import Dict, List, Union
from urllib.parse import urlparse

from devtools_testutils import recorded_by_proxy
from devtools_testutils import (
    PemCertificate,
    set_function_recording_options,
    create_combined_bundle,
    is_live_and_not_recording
)

from azure.confidentialledger import (
    ConfidentialLedgerCertificateCredential,
    ConfidentialLedgerClient,
)

test_proxy_cert = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", 'eng', 'common', 'testproxy', 'dotnet-devcert.crt'))

from _shared.constants import (
    USER_CERTIFICATE_THUMBPRINT,
    USER_CERTIFICATE_PRIVATE_KEY,
    USER_CERTIFICATE_PUBLIC_KEY,
)
from _shared.testcase import ConfidentialLedgerPreparer, ConfidentialLedgerTestCase


class TestConfidentialLedgerClient(ConfidentialLedgerTestCase):
    def create_confidentialledger_client(self, endpoint, ledger_id, is_aad, fetch_tls_cert=True):
        # Always explicitly fetch the TLS certificate.
        network_cert = self.set_ledger_identity(ledger_id)
        if not fetch_tls_cert:
            # For some test scenarios, remove the file so the client sees it doesn't exist and
            # creates it auto-magically.
            os.remove(self.network_certificate_path)

        # The Confidential Ledger always presents a self-signed certificate, so add that certificate
        # to the recording options for the Confidential Ledger endpoint.
        function_recording_options: Dict[str, Union[str, List[PemCertificate]]] = {
            "tls_certificate": network_cert,
            "tls_certificate_host": urlparse(endpoint).netloc,
        }
        set_function_recording_options(**function_recording_options)

        # The ACL instance should already have the potential AAD user added as an Administrator.
        credential = self.get_credential(ConfidentialLedgerClient)

        if not is_live_and_not_recording():
            # inject the test-proxy dev-cert into the path where the identity TLS certificate currently exists
            create_combined_bundle([self.network_certificate_path, test_proxy_cert], self.network_certificate_path)

        aad_based_client = self.create_client_from_credential(
            ConfidentialLedgerClient,
            credential=credential,
            endpoint=endpoint,
            # self.network_certificate_path is set via self.set_ledger_identity
            ledger_certificate_path=self.network_certificate_path,  # type: ignore
        )

        if not is_aad and not fetch_tls_cert:
            # Delete the network certificate again since we want to make sure a cert-based client
            # fetches it too.
            #
            # Since we create the cert-based client immediately, the certificate will still be
            # available for the above aad_based_client when we use it to add the cert-based user
            # to the ledger.
            os.remove(self.network_certificate_path)

        certificate_credential = ConfidentialLedgerCertificateCredential(
            certificate_path=self.user_certificate_path
        )
        certificate_based_client = ConfidentialLedgerClient(
            credential=certificate_credential,
            endpoint=endpoint,
            # self.network_certificate_path is set via self.set_ledger_identity
            ledger_certificate_path=self.network_certificate_path,  # type: ignore
        )

        if not is_aad:
            # We need to add the certificate-based user as an Administrator.
            aad_based_client.create_or_update_user(
                USER_CERTIFICATE_THUMBPRINT, {"assignedRole": "Administrator"}
            )

            # Sleep to make sure all replicas know the user is added.
            time.sleep(3)

            # Update the options to account for certificate-based authentication.
            function_recording_options["certificates"] = [
                PemCertificate(key=USER_CERTIFICATE_PRIVATE_KEY, data=USER_CERTIFICATE_PUBLIC_KEY)
            ]
            set_function_recording_options(**function_recording_options)

            client = certificate_based_client
        else:
            client = aad_based_client

        return client

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_append_entry_flow_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True
        )
        self.append_entry_flow_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_append_entry_flow_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False
        )
        self.append_entry_flow_actions(client)

    def append_entry_flow_actions(self, client):
        entry_contents = "Test entry from Python SDK"
        append_result = client.create_ledger_entry({"contents": entry_contents})
        assert append_result["transactionId"]
        assert append_result["collectionId"]

        append_result_sub_ledger_id = append_result["collectionId"]
        append_result_transaction_id = append_result["transactionId"]

        poller = client.begin_wait_for_commit(
            transaction_id=append_result_transaction_id
        )
        poller.wait()

        transaction_status = client.get_transaction_status(
            transaction_id=append_result_transaction_id
        )
        assert transaction_status["transactionId"] == append_result_transaction_id
        assert transaction_status["state"] == "Committed"

        poller = client.begin_get_receipt(transaction_id=append_result_transaction_id)
        receipt = poller.result()
        assert receipt["transactionId"] == append_result_transaction_id
        assert receipt["receipt"]

        latest_entry = client.get_current_ledger_entry()
        # The transaction ids may not be equal in the unfortunate edge case where an internal
        # operation occurs after the ledger append (e.g. because a node was restarted). Then,
        # the latest id will be higher.
        latest_entry_view = int(latest_entry["transactionId"].split(".")[0])
        latest_entry_seqno = int(latest_entry["transactionId"].split(".")[-1])
        append_result_view = int(append_result_transaction_id.split(".")[0])
        append_result_seqno = int(append_result_transaction_id.split(".")[-1])
        assert latest_entry_view >= append_result_view and latest_entry_seqno >= append_result_seqno
        assert latest_entry["contents"] == entry_contents
        assert latest_entry["collectionId"] == append_result_sub_ledger_id

        poller = client.begin_create_ledger_entry(
            {"contents": "Test entry 2 from Python SDK"}
        )
        poller.wait()

        latest_entry = client.get_current_ledger_entry()
        assert latest_entry["transactionId"] != append_result_transaction_id
        assert latest_entry["contents"] != entry_contents
        assert latest_entry["collectionId"] == append_result_sub_ledger_id

        poller = client.begin_get_ledger_entry(
            transaction_id=append_result_transaction_id
        )
        original_entry = poller.result()
        assert original_entry["entry"]["transactionId"] == append_result_transaction_id
        assert original_entry["entry"]["contents"] == entry_contents
        assert original_entry["entry"]["collectionId"] == append_result_sub_ledger_id

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_append_entry_flow_with_collection_id_aad_user(
        self, **kwargs,
    ):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True
        )
        self.append_entry_flow_with_collection_id_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_append_entry_flow_with_collection_id_cert_user(
        self, **kwargs,
    ):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False
        )
        self.append_entry_flow_with_collection_id_actions(client)

    def append_entry_flow_with_collection_id_actions(self, client):
        collection_id = "132"
        entry_contents = f"Test entry from Python SDK. Collection: {collection_id}"
        append_result = client.create_ledger_entry(
            {"contents": entry_contents},
            collection_id=collection_id,
        )
        assert append_result["transactionId"]
        assert append_result["collectionId"] == collection_id

        append_result_sub_ledger_id = append_result["collectionId"]
        append_result_transaction_id = append_result["transactionId"]

        poller = client.begin_wait_for_commit(
            transaction_id=append_result_transaction_id
        )
        poller.wait()

        transaction_status = client.get_transaction_status(
            transaction_id=append_result_transaction_id
        )
        assert transaction_status
        assert transaction_status["state"] == "Committed"

        poller = client.begin_get_receipt(transaction_id=append_result_transaction_id)
        receipt = poller.result()
        assert receipt["transactionId"] == append_result_transaction_id
        assert receipt["receipt"]

        latest_entry = client.get_current_ledger_entry(collection_id=collection_id)
        # The transaction ids may not be equal in the unfortunate edge case where an internal
        # operation occurs after the ledger append (e.g. because a node was restarted). Then,
        # the latest id will be higher.
        latest_entry_view = int(latest_entry["transactionId"].split(".")[0])
        latest_entry_seqno = int(latest_entry["transactionId"].split(".")[-1])
        append_result_view = int(append_result_transaction_id.split(".")[0])
        append_result_seqno = int(append_result_transaction_id.split(".")[-1])
        assert latest_entry_view >= append_result_view and latest_entry_seqno >= append_result_seqno
        assert latest_entry["contents"] == entry_contents
        assert latest_entry["collectionId"] == append_result_sub_ledger_id

        poller = client.begin_create_ledger_entry(
            {"contents": f"Test entry 2 from Python SDK. Collection: {collection_id}"},
            collection_id=collection_id,
        )
        poller.wait()

        latest_entry = client.get_current_ledger_entry(collection_id=collection_id)
        assert latest_entry["transactionId"] != append_result_transaction_id
        assert latest_entry["contents"] != entry_contents
        assert latest_entry["collectionId"] == collection_id

        poller = client.begin_get_ledger_entry(
            transaction_id=append_result_transaction_id,
            collection_id=collection_id,
        )
        original_entry = poller.result()
        assert original_entry["entry"]["transactionId"] == append_result_transaction_id
        assert original_entry["entry"]["contents"] == entry_contents
        assert original_entry["entry"]["collectionId"] == append_result_sub_ledger_id

        collections = client.list_collections()
        collection_ids = set()
        for collection in collections:
            collection_ids.add(collection["collectionId"])
        assert collection_id in collection_ids

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_range_query_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True
        )
        self.range_query_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_range_query_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False
        )
        self.range_query_actions(client)

    def range_query_actions(self, client):
        num_collections = 5

        # Send 2 messages per collection. No need to test pagination over many pages because:
        # 1. Each page is 1000 entries, so we'd have to send 1001 * num_collections messages and
        #    and read them all; not ideal!
        # 2. The pagination _should_ be tested often enough because the first response is typically
        #    not ready, with a nextLink pointing at the original query and an empty list of entires,
        #    as the historical query is just starting.
        num_messages_sent = num_collections * 2

        messages = {m: [] for m in range(num_collections)}
        for i in range(num_messages_sent):
            message = "message-{0}".format(i)
            kwargs = (
                {} if num_collections == 0 else {"collection_id": "{0}".format(i % num_collections)}
            )

            if i != num_messages_sent - 1:
                append_result = client.create_ledger_entry({"contents": message}, **kwargs)
            else:
                append_poller = client.begin_create_ledger_entry({"contents": message}, **kwargs)
                append_result = append_poller.result()

            messages[i % num_collections].append(
                (append_result["transactionId"], message, kwargs)
            )

        num_matched = 0
        for i in range(num_collections):
            query_result = client.list_ledger_entries(
                from_transaction_id=messages[i][0][0],
                to_transaction_id=messages[i][-1][0],
                **messages[i][0][2],
            )
            for index, historical_entry in enumerate(query_result):
                assert historical_entry["transactionId"] == messages[i][index][0]
                assert historical_entry["contents"] == messages[i][index][1]
                collection_id = messages[i][index][2].get("collection_id", None)
                if collection_id is not None:
                    assert historical_entry["collectionId"] == collection_id

                num_matched += 1

        assert num_matched == num_messages_sent

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_user_management_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True
        )
        self.user_management_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_user_management_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False
        )
        self.user_management_actions(client)

    def user_management_actions(self, client):
        aad_user_id = "0" * 36  # AAD Object Ids have length 36
        cert_user_id = (
            "7F:75:58:60:70:A8:B6:15:A2:CD:24:55:25:B9:64:49:F8:BF:F0:E3:4D:92:EA:B2:8C:30:E6:2D:F4"
            ":77:30:1F"
        )
        for user_id in [aad_user_id, cert_user_id]:
            user = client.create_or_update_user(
                user_id, {"assignedRole": "Contributor"}
            )
            assert user["userId"] == user_id
            assert user["assignedRole"] == "Contributor"

            time.sleep(3)  # Let the PATCH user operation be committed, just in case.

            user = client.get_user(user_id)
            assert user["userId"] == user_id
            assert user["assignedRole"] == "Contributor"

            user = client.create_or_update_user(user_id, {"assignedRole": "Reader"})
            assert user["userId"] == user_id
            assert user["assignedRole"] == "Reader"

            time.sleep(3)  # Let the PATCH user operation be committed, just in case.

            user = client.get_user(user_id)
            assert user["userId"] == user_id
            assert user["assignedRole"] == "Reader"

            client.delete_user(user_id)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_verification_methods_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True
        )
        self.verification_methods_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_verification_methods_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False
        )
        self.verification_methods_actions(client)

    def verification_methods_actions(self, client):
        consortium = client.list_consortium_members()
        consortium_size = 0
        for member in consortium:
            assert member["certificate"]
            assert member["id"]
            consortium_size += 1
        assert consortium_size == 1

        constitution = client.get_constitution()
        assert constitution["script"]
        assert constitution["digest"]
        assert (
            constitution["digest"].lower() == 
            hashlib.sha256(constitution["script"].encode()).hexdigest().lower()
        )

        ledger_enclaves = client.get_enclave_quotes()
        assert len(ledger_enclaves["enclaveQuotes"]) == 3
        assert ledger_enclaves["currentNodeId"] in ledger_enclaves["enclaveQuotes"]
        for node_id, quote in ledger_enclaves["enclaveQuotes"].items():
            assert node_id == quote["nodeId"]
            assert quote["nodeId"]
            assert quote["mrenclave"]
            assert quote["raw"]
            assert quote["quoteVersion"]

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_tls_cert_convenience_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True, fetch_tls_cert=False,
        )
        self.tls_cert_convenience_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_tls_cert_convenience_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False, fetch_tls_cert=False,
        )
        self.tls_cert_convenience_actions(client)

    def tls_cert_convenience_actions(self, client):
        # It's sufficient to use any arbitrary endpoint to test the TLS connection.
        constitution = client.get_constitution()
        assert constitution["script"]
