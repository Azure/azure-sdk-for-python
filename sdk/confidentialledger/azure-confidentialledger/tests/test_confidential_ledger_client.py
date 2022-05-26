import hashlib

from azure.confidentialledger import (
    ConfidentialLedgerCertificateCredential,
    ConfidentialLedgerClient,
)

from .testcase import ConfidentialLedgerPreparer, ConfidentialLedgerTestCase


class ConfidentialLedgerClientTest(ConfidentialLedgerTestCase):
    def create_confidentialledger_client(self, endpoint, is_aad):
        # The ACL instance should already have the potential AAD and cert users added as
        # Administrators.

        if is_aad:
            credential = self.get_credential(ConfidentialLedgerClient)
            client = self.create_client_from_credential(
                ConfidentialLedgerClient,
                credential=credential,
                ledger_uri=endpoint,
                ledger_certificate_path=self.network_certificate_path,
            )
        else:
            credential = ConfidentialLedgerCertificateCredential(
                certificate_path=self.user_certificate_path
            )
            client = ConfidentialLedgerClient(
                credential=credential,
                ledger_uri=endpoint,
                ledger_certificate_path=self.network_certificate_path,
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
        append_result = client.append_to_ledger(entry_contents=entry_contents)
        self.assertTrue(append_result["transactionId"])
        self.assertTrue(append_result["subLedgerId"])

        append_result_sub_ledger_id = append_result["subLedgerId"]
        append_result_transaction_id = append_result["transactionId"]

        client.wait_until_durable(transaction_id=append_result_transaction_id)

        transaction_status = client.get_transaction_status(
            transaction_id=append_result_transaction_id
        )
        self.assertIsNotNone(transaction_status)
        self.assertIs(transaction_status, "Committed")

        receipt = client.get_transaction_receipt(
            transaction_id=append_result_transaction_id
        )
        self.assertEqual(receipt["transactionId"], append_result_transaction_id)
        self.assertTrue(receipt["contents"])

        latest_entry = client.get_ledger_entry()
        # The transaction ids may not be equal in the unfortunate edge case where a governance
        # operation occurs after the ledger append (e.g. because a node was restarted). Then,
        # the latest id will be higher.
        self.assertGreaterEqual(
            latest_entry["transactionId"], append_result_transaction_id
        )
        self.assertEqual(latest_entry["contents"], entry_contents)
        self.assertEqual(latest_entry["subLedgerId"], append_result_sub_ledger_id)

        client.append_to_ledger("Test entry 2 from Python SDK", wait_for_commit=True)

        latest_entry = client.get_ledger_entry()
        self.assertNotEqual(latest_entry["transactionId"], append_result_transaction_id)
        self.assertNotEqual(latest_entry["contents"], entry_contents)
        self.assertEqual(latest_entry["subLedgerId"], append_result_sub_ledger_id)

        original_entry = client.get_ledger_entry(
            transaction_id=append_result_transaction_id
        )
        self.assertEqual(original_entry["transactionId"], append_result_transaction_id)
        self.assertEqual(original_entry["contents"], entry_contents)
        self.assertEqual(original_entry["subLedgerId"], append_result_sub_ledger_id)

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
        entry_contents = "Test sub-ledger entry from Python SDK"
        append_result = client.append_to_ledger(
            entry_contents=entry_contents, sub_ledger_id=collection_id
        )
        self.assertTrue(append_result["transactionId"])
        self.assertEqual(append_result["subLedgerId"], collection_id)

        append_result_sub_ledger_id = append_result["subLedgerId"]
        append_result_transaction_id = append_result["transactionId"]

        client.wait_until_durable(transaction_id=append_result_transaction_id)

        transaction_status = client.get_transaction_status(
            transaction_id=append_result_transaction_id
        )
        self.assertIsNotNone(transaction_status)
        self.assertIs(transaction_status, "Committed")

        receipt = client.get_transaction_receipt(
            transaction_id=append_result_transaction_id
        )
        self.assertEqual(receipt["transactionId"], append_result_transaction_id)
        self.assertTrue(receipt["contents"])

        latest_entry = client.get_ledger_entry(sub_ledger_id=collection_id)
        # The transaction ids may not be equal in the unfortunate edge case where a governance
        # operation occurs after the ledger append (e.g. because a node was restarted). Then,
        # the latest id will be higher.
        self.assertGreaterEqual(
            latest_entry["transactionId"], append_result_transaction_id
        )
        self.assertEqual(latest_entry["contents"], entry_contents)
        self.assertEqual(latest_entry["subLedgerId"], append_result_sub_ledger_id)

        client.append_to_ledger(
            "Test sub-ledger entry 2 from Python SDK",
            sub_ledger_id=collection_id,
            wait_for_commit=True,
        )

        latest_entry = client.get_ledger_entry(sub_ledger_id=collection_id)
        self.assertNotEqual(latest_entry["transactionId"], append_result_transaction_id)
        self.assertNotEqual(latest_entry["contents"], entry_contents)
        self.assertEqual(latest_entry["subLedgerId"], collection_id)

        original_entry = client.get_ledger_entry(
            transaction_id=append_result_transaction_id, sub_ledger_id=collection_id
        )
        self.assertEqual(original_entry["transactionId"], append_result_transaction_id)
        self.assertEqual(original_entry["contents"], entry_contents)
        self.assertEqual(original_entry["subLedgerId"], append_result_sub_ledger_id)

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
                {} if modulus == 0 else {"sub_ledger_id": "{0}".format(i % modulus)}
            )
            append_result = client.append_to_ledger(entry_contents=message, **kwargs)

            messages[i % modulus].append(
                (append_result["transactionId"], message, kwargs)
            )

        num_matched = 0
        for i in range(modulus):
            query_result = client.get_ledger_entries(
                from_transaction_id=messages[i][0][0], **messages[i][0][2]
            )
            for index, historical_entry in enumerate(query_result):
                self.assertEqual(historical_entry["transactionId"], messages[i][index][0])
                self.assertEqual(historical_entry["contents"], messages[i][index][1])
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
            user = client.create_or_update_user(user_id, "Contributor")
            self.assertEqual(user["id"], user_id)
            self.assertEqual(user["role"], "Contributor")

            user = client.get_user(user_id)
            self.assertEqual(user["id"], user_id)
            self.assertEqual(user["role"], "Contributor")

            client.delete_user(user_id)

            user = client.create_or_update_user(user_id, "Reader")
            self.assertEqual(user["id"], user_id)
            self.assertEqual(user["role"], "Reader")

            user = client.get_user(user_id)
            self.assertEqual(user["id"], user_id)
            self.assertEqual(user["role"], "Reader")

            client.delete_user(user_id)

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
        consortium = client.get_consortium()
        self.assertEqual(len(consortium["members"]), 1)
        for member in consortium["members"]:
            self.assertTrue(member["certificate"])
            self.assertTrue(member["id"])

        constitution = client.get_constitution()
        self.assertTrue(constitution["contents"])
        self.assertTrue(constitution["digest"])
        self.assertEqual(
            constitution["digest"].lower(),
            hashlib.sha256(constitution["contents"].encode()).hexdigest().lower(),
        )

        ledger_enclaves = client.get_enclave_quotes()
        self.assertEqual(len(ledger_enclaves["quotes"]), 3)
        self.assertIn(ledger_enclaves["sourceNode"], ledger_enclaves["quotes"])
        for node_id, quote in ledger_enclaves["quotes"].items():
            self.assertEqual(node_id, quote["nodeId"])
            self.assertTrue(quote["nodeId"])
            self.assertTrue(quote["mrenclave"])
            self.assertTrue(quote["rawQuote"])
            self.assertTrue(quote["version"])
