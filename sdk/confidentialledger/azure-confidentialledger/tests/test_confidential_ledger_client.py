import hashlib

from azure.confidentialledger import (
    ConfidentialLedgerCertificateCredential,
    ConfidentialLedgerClient,
)

from .constants import USER_CERTIFICATE_THUMBPRINT
from .testcase import ConfidentialLedgerPreparer, ConfidentialLedgerTestCase


class ConfidentialLedgerClientTest(ConfidentialLedgerTestCase):
    def create_confidentialledger_client(self, endpoint, is_aad):
        self.set_ledger_identity(endpoint)

        # The ACL instance should already have the potential AAD user added as an Administrator.
        credential = self.get_credential(ConfidentialLedgerClient)
        client = self.create_client_from_credential(
            ConfidentialLedgerClient,
            credential=credential,
            ledger_uri=endpoint,
            # self.network_certificate_path is set via self.set_ledger_identity
            ledger_certificate_path=self.network_certificate_path,  # type: ignore
        )

        if not is_aad:
            # Add the certificate-based user.
            client.confidential_ledger.create_or_update_user(
                USER_CERTIFICATE_THUMBPRINT, {"assignedRole": "Administrator"}
            )

            credential = ConfidentialLedgerCertificateCredential(
                certificate_path=self.user_certificate_path
            )
            client = ConfidentialLedgerClient(
                credential=credential,
                ledger_uri=endpoint,
                # self.network_certificate_path is set via self.set_ledger_identity
                ledger_certificate_path=self.network_certificate_path,  # type: ignore
            )

        return client

    @ConfidentialLedgerPreparer()
    def test_append_entry_flow_aad_user(self, confidentialledger_endpoint):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, is_aad=True
        )
        self.append_entry_flow_actions(client)

    @ConfidentialLedgerPreparer()
    def test_append_entry_flow_cert_user(self, confidentialledger_endpoint):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, is_aad=False
        )
        self.append_entry_flow_actions(client)

    def append_entry_flow_actions(self, client):
        entry_contents = "Test entry from Python SDK"
        append_result = client.confidential_ledger.post_ledger_entry(
            {"contents": entry_contents}
        )
        self.assertTrue(append_result["transactionId"])
        self.assertTrue(append_result["collectionId"])

        append_result_sub_ledger_id = append_result["collectionId"]
        append_result_transaction_id = append_result["transactionId"]

        poller = client.confidential_ledger.begin_wait_for_commit(
            transaction_id=append_result_transaction_id
        )
        poller.wait()

        transaction_status = client.confidential_ledger.get_transaction_status(
            transaction_id=append_result_transaction_id
        )
        self.assertEqual(
            transaction_status["transactionId"], append_result_transaction_id
        )
        self.assertEqual(transaction_status["state"], "Committed")

        poller = client.confidential_ledger.begin_get_receipt(
            transaction_id=append_result_transaction_id
        )
        receipt = poller.result()
        self.assertEqual(receipt["transactionId"], append_result_transaction_id)
        self.assertTrue(receipt["receipt"])

        latest_entry = client.confidential_ledger.get_current_ledger_entry()
        # The transaction ids may not be equal in the unfortunate edge case where a governance
        # operation occurs after the ledger append (e.g. because a node was restarted). Then,
        # the latest id will be higher.
        self.assertGreaterEqual(
            latest_entry["transactionId"], append_result_transaction_id
        )
        self.assertEqual(latest_entry["contents"], entry_contents)
        self.assertEqual(latest_entry["collectionId"], append_result_sub_ledger_id)

        poller = client.confidential_ledger.begin_post_ledger_entry(
            {"contents": "Test entry 2 from Python SDK"}
        )
        poller.wait()

        latest_entry = client.confidential_ledger.get_current_ledger_entry()
        self.assertNotEqual(latest_entry["transactionId"], append_result_transaction_id)
        self.assertNotEqual(latest_entry["contents"], entry_contents)
        self.assertEqual(latest_entry["collectionId"], append_result_sub_ledger_id)

        poller = client.confidential_ledger.begin_get_ledger_entry(
            transaction_id=append_result_transaction_id
        )
        original_entry = poller.result()
        self.assertEqual(
            original_entry["entry"]["transactionId"], append_result_transaction_id
        )
        self.assertEqual(original_entry["entry"]["contents"], entry_contents)
        self.assertEqual(
            original_entry["entry"]["collectionId"], append_result_sub_ledger_id
        )

    @ConfidentialLedgerPreparer()
    def test_append_entry_flow_with_collection_id_aad_user(
        self, confidentialledger_endpoint
    ):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, is_aad=True
        )
        self.append_entry_flow_with_collection_id_actions(client)

    @ConfidentialLedgerPreparer()
    def test_append_entry_flow_with_collection_id_cert_user(
        self, confidentialledger_endpoint
    ):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, is_aad=False
        )
        self.append_entry_flow_with_collection_id_actions(client)

    def append_entry_flow_with_collection_id_actions(self, client):
        collection_id = "132"
        entry_contents = f"Test entry from Python SDK. Collection: {collection_id}"
        append_result = client.confidential_ledger.post_ledger_entry(
            {"contents": entry_contents},
            collection_id=collection_id,
        )
        self.assertTrue(append_result["transactionId"])
        self.assertEqual(append_result["collectionId"], collection_id)

        append_result_sub_ledger_id = append_result["collectionId"]
        append_result_transaction_id = append_result["transactionId"]

        poller = client.confidential_ledger.begin_wait_for_commit(
            transaction_id=append_result_transaction_id
        )
        poller.wait()

        transaction_status = client.confidential_ledger.get_transaction_status(
            transaction_id=append_result_transaction_id
        )
        self.assertIsNotNone(transaction_status)
        self.assertEqual(transaction_status["state"], "Committed")

        poller = client.confidential_ledger.begin_get_receipt(
            transaction_id=append_result_transaction_id
        )
        receipt = poller.result()
        self.assertEqual(receipt["transactionId"], append_result_transaction_id)
        self.assertTrue(receipt["receipt"])

        latest_entry = client.confidential_ledger.get_current_ledger_entry(
            collection_id=collection_id
        )
        # The transaction ids may not be equal in the unfortunate edge case where a governance
        # operation occurs after the ledger append (e.g. because a node was restarted). Then,
        # the latest id will be higher.
        self.assertGreaterEqual(
            latest_entry["transactionId"], append_result_transaction_id
        )
        self.assertEqual(latest_entry["contents"], entry_contents)
        self.assertEqual(latest_entry["collectionId"], append_result_sub_ledger_id)

        poller = client.confidential_ledger.begin_post_ledger_entry(
            {"contents": f"Test entry 2 from Python SDK. Collection: {collection_id}"},
            collection_id=collection_id,
        )
        poller.wait()

        latest_entry = client.confidential_ledger.get_current_ledger_entry(
            collection_id=collection_id
        )
        self.assertNotEqual(latest_entry["transactionId"], append_result_transaction_id)
        self.assertNotEqual(latest_entry["contents"], entry_contents)
        self.assertEqual(latest_entry["collectionId"], collection_id)

        poller = client.confidential_ledger.begin_get_ledger_entry(
            transaction_id=append_result_transaction_id,
            collection_id=collection_id,
        )
        original_entry = poller.result()
        self.assertEqual(
            original_entry["entry"]["transactionId"], append_result_transaction_id
        )
        self.assertEqual(original_entry["entry"]["contents"], entry_contents)
        self.assertEqual(
            original_entry["entry"]["collectionId"], append_result_sub_ledger_id
        )

        collections = client.confidential_ledger.list_collections()
        collection_ids = set()
        for collection in collections:
            collection_ids.add(collection["collectionId"])
        self.assertIn("collection_id", collection_ids)

    @ConfidentialLedgerPreparer()
    def test_range_query_aad_user(self, confidentialledger_endpoint):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, is_aad=True
        )
        self.range_query_actions(client)

    @ConfidentialLedgerPreparer()
    def test_range_query_cert_user(self, confidentialledger_endpoint):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, is_aad=False
        )
        self.range_query_actions(client)

    def range_query_actions(self, client):
        modulus = 5
        num_messages_sent = 2001  # Should result in 2 pages.

        messages = {m: [] for m in range(modulus)}
        for i in range(num_messages_sent):
            message = "message-{0}".format(i)
            kwargs = (
                {} if modulus == 0 else {"collection_id": "{0}".format(i % modulus)}
            )
            append_result = client.confidential_ledger.post_ledger_entry(
                {"contents": message}, **kwargs
            )

            messages[i % modulus].append(
                (append_result["transactionId"], message, kwargs)
            )

        num_matched = 0
        for i in range(modulus):
            query_result = client.confidential_ledger.list_ledger_entries(
                from_transaction_id=messages[i][0][0], **messages[i][0][2]
            )
            for index, historical_entry in enumerate(query_result):
                self.assertEqual(
                    historical_entry["transactionId"], messages[i][index][0]
                )
                self.assertEqual(historical_entry["contents"], messages[i][index][1])
                collection_id = messages[i][index][2].get("collection_id", None)
                if collection_id is not None:
                    self.assertEqual(historical_entry["collectionId"], collection_id)

                num_matched += 1

        # Due to replication delay, it's possible not all messages are matched.
        self.assertGreaterEqual(num_matched, 0.9 * num_messages_sent)

    @ConfidentialLedgerPreparer()
    def test_user_management_aad_user(self, confidentialledger_endpoint):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, is_aad=True
        )
        self.user_management_actions(client)

    @ConfidentialLedgerPreparer()
    def test_user_management_cert_user(self, confidentialledger_endpoint):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, is_aad=False
        )
        self.user_management_actions(client)

    def user_management_actions(self, client):
        aad_user_id = "0" * 36  # AAD Object Ids have length 36
        cert_user_id = (
            "7F:75:58:60:70:A8:B6:15:A2:CD:24:55:25:B9:64:49:F8:BF:F0:E3:4D:92:EA:B2:8C:30:E6:2D:F4"
            ":77:30:1F"
        )
        for user_id in [aad_user_id, cert_user_id]:
            user = client.confidential_ledger.create_or_update_user(
                user_id, {"assignedRole": "Contributor"}
            )
            self.assertEqual(user["userId"], user_id)
            self.assertEqual(user["assignedRole"], "Contributor")

            user = client.confidential_ledger.get_user(user_id)
            self.assertEqual(user["userId"], user_id)
            self.assertEqual(user["assignedRole"], "Contributor")

            client.confidential_ledger.delete_user(user_id)

            user = client.confidential_ledger.create_or_update_user(
                user_id, {"assignedRole": "Reader"}
            )
            self.assertEqual(user["userId"], user_id)
            self.assertEqual(user["assignedRole"], "Reader")

            user = client.confidential_ledger.get_user(user_id)
            self.assertEqual(user["userId"], user_id)
            self.assertEqual(user["assignedRole"], "Reader")

            client.confidential_ledger.delete_user(user_id)

    @ConfidentialLedgerPreparer()
    def test_verification_methods_aad_user(self, confidentialledger_endpoint):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, is_aad=True
        )
        self.verification_methods_actions(client)

    @ConfidentialLedgerPreparer()
    def test_verification_methods_cert_user(self, confidentialledger_endpoint):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, is_aad=False
        )
        self.verification_methods_actions(client)

    def verification_methods_actions(self, client):
        consortium = client.confidential_ledger.get_consortium_members()
        self.assertEqual(len(consortium["members"]), 1)
        for member in consortium["members"]:
            self.assertTrue(member["certificate"])
            self.assertTrue(member["id"])

        constitution = client.confidential_ledger.get_constitution()
        self.assertTrue(constitution["script"])
        self.assertTrue(constitution["digest"])
        self.assertEqual(
            constitution["digest"].lower(),
            hashlib.sha256(constitution["script"].encode()).hexdigest().lower(),
        )

        ledger_enclaves = client.confidential_ledger.get_enclave_quotes()
        self.assertEqual(len(ledger_enclaves["enclaveQuotes"]), 3)
        self.assertIn(
            ledger_enclaves["currentNodeId"], ledger_enclaves["enclaveQuotes"]
        )
        for node_id, quote in ledger_enclaves["enclaveQuotes"].items():
            self.assertEqual(node_id, quote["nodeId"])
            self.assertTrue(quote["nodeId"])
            self.assertTrue(quote["mrenclave"])
            self.assertTrue(quote["raw"])
            self.assertTrue(quote["quoteVersion"])
