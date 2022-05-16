import asyncio
import hashlib
import os
import tempfile
import time

from devtools_testutils import AzureTestCase

from azure.confidentialledger import (
    LedgerUserRole,
    TransactionState,
)

from .constants import NETWORK_CERTIFICATE, USER_CERTIFICATE
from .testcase_async import AsyncConfidentialLedgerTestCase

CONFIDENTIAL_LEDGER_URL = "https://fake-confidential-ledger.azure.com"


class AsyncConfidentialLedgerClientTestMixin:
    class AsyncBaseTest(AsyncConfidentialLedgerTestCase):
        def setUp(self):
            super().setUp()

            self.confidential_ledger_url = self.set_value_to_scrub(
                "CONFIDENTIAL_LEDGER_URL", CONFIDENTIAL_LEDGER_URL
            )

            with tempfile.NamedTemporaryFile(
                "w", suffix=".pem", delete=False
            ) as tls_cert_file:
                tls_cert_file.write(NETWORK_CERTIFICATE)
                self.network_certificate_path = tls_cert_file.name

            with tempfile.NamedTemporaryFile(
                "w", suffix=".pem", delete=False
            ) as user_cert_file:
                user_cert_file.write(
                    self.set_value_to_scrub(
                        "CONFIDENTIAL_LEDGER_USER_CERTIFICATE", USER_CERTIFICATE
                    )
                )
                self.user_certificate_path = user_cert_file.name

        def tearDown(self):
            os.remove(self.user_certificate_path)
            os.remove(self.network_certificate_path)

            # Since tearDown cannot be async
            task = asyncio.ensure_future(self.client.close())
            while not task.done:
                time.sleep(0.5)

            return super().tearDown()

        @AzureTestCase.await_prepared_test
        async def test_append_entry_flow(self):
            entry_contents = "Test entry from Python SDK"
            append_result = await self.client.append_to_ledger(
                entry_contents=entry_contents
            )
            self.assertTrue(append_result.transaction_id)
            self.assertTrue(append_result.sub_ledger_id)

            # Test unpacking
            append_result_sub_ledger_id, append_result_transaction_id = append_result

            await self.client.wait_until_durable(
                transaction_id=append_result_transaction_id
            )

            transaction_status = await self.client.get_transaction_status(
                transaction_id=append_result_transaction_id
            )
            self.assertIsNotNone(transaction_status)
            self.assertIs(transaction_status.state, TransactionState.COMMITTED)
            self.assertEqual(
                transaction_status.transaction_id, append_result_transaction_id
            )

            receipt = await self.client.get_transaction_receipt(
                transaction_id=append_result_transaction_id
            )
            self.assertEqual(receipt.transaction_id, append_result_transaction_id)
            self.assertTrue(receipt.contents)

            latest_entry = await self.client.get_ledger_entry()
            # The transaction ids may not be equal in the unfortunate edge case where a governance
            # operation occurs after the ledger append (e.g. because a node was restarted). Then,
            # the latest id will be higher.
            self.assertGreaterEqual(
                latest_entry.transaction_id, append_result_transaction_id
            )
            self.assertEqual(latest_entry.contents, entry_contents)
            self.assertEqual(latest_entry.sub_ledger_id, append_result_sub_ledger_id)

            await self.client.append_to_ledger(
                "Test entry 2 from Python SDK", wait_for_commit=True
            )

            latest_entry = await self.client.get_ledger_entry()
            self.assertNotEqual(
                latest_entry.transaction_id, append_result_transaction_id
            )
            self.assertNotEqual(latest_entry.contents, entry_contents)
            self.assertEqual(latest_entry.sub_ledger_id, append_result_sub_ledger_id)

            original_entry = await self.client.get_ledger_entry(
                transaction_id=append_result_transaction_id
            )
            self.assertEqual(
                original_entry.transaction_id, append_result_transaction_id
            )
            self.assertEqual(original_entry.contents, entry_contents)
            self.assertEqual(original_entry.sub_ledger_id, append_result_sub_ledger_id)

        @AzureTestCase.await_prepared_test
        async def test_append_entry_flow_with_sub_ledger_id(self):
            sub_ledger_id = "132"
            entry_contents = "Test sub-ledger entry from Python SDK"
            append_result = await self.client.append_to_ledger(
                entry_contents=entry_contents, sub_ledger_id=sub_ledger_id
            )
            self.assertTrue(append_result.transaction_id)
            self.assertEqual(append_result.sub_ledger_id, sub_ledger_id)

            # Test unpacking
            append_result_sub_ledger_id, append_result_transaction_id = append_result

            await self.client.wait_until_durable(
                transaction_id=append_result_transaction_id
            )

            transaction_status = await self.client.get_transaction_status(
                transaction_id=append_result_transaction_id
            )
            self.assertIsNotNone(transaction_status)
            self.assertIs(transaction_status.state, TransactionState.COMMITTED)
            self.assertEqual(
                transaction_status.transaction_id, append_result_transaction_id
            )

            receipt = await self.client.get_transaction_receipt(
                transaction_id=append_result_transaction_id
            )
            self.assertEqual(receipt.transaction_id, append_result_transaction_id)
            self.assertTrue(receipt.contents)

            latest_entry = await self.client.get_ledger_entry(
                sub_ledger_id=sub_ledger_id
            )
            # The transaction ids may not be equal in the unfortunate edge case where a governance
            # operation occurs after the ledger append (e.g. because a node was restarted). Then,
            # the latest id will be higher.
            self.assertGreaterEqual(
                latest_entry.transaction_id, append_result_transaction_id
            )
            self.assertEqual(latest_entry.contents, entry_contents)
            self.assertEqual(latest_entry.sub_ledger_id, append_result_sub_ledger_id)

            await self.client.append_to_ledger(
                "Test sub-ledger entry 2 from Python SDK",
                sub_ledger_id=sub_ledger_id,
                wait_for_commit=True,
            )

            latest_entry = await self.client.get_ledger_entry(
                sub_ledger_id=sub_ledger_id
            )
            self.assertNotEqual(
                latest_entry.transaction_id, append_result_transaction_id
            )
            self.assertNotEqual(latest_entry.contents, entry_contents)
            self.assertEqual(latest_entry.sub_ledger_id, sub_ledger_id)

            original_entry = await self.client.get_ledger_entry(
                transaction_id=append_result_transaction_id, sub_ledger_id=sub_ledger_id
            )
            self.assertEqual(
                original_entry.transaction_id, append_result_transaction_id
            )
            self.assertEqual(original_entry.contents, entry_contents)
            self.assertEqual(original_entry.sub_ledger_id, append_result_sub_ledger_id)

        @AzureTestCase.await_prepared_test
        async def test_range_query(self):
            modulus = 5
            num_messages_sent = 2001  # Should result in 2 pages.

            messages = {m: [] for m in range(modulus)}
            for i in range(num_messages_sent):
                message = "message-{0}".format(i)
                kwargs = (
                    {} if modulus == 0 else {"sub_ledger_id": "{0}".format(i % modulus)}
                )
                append_result = await self.client.append_to_ledger(
                    entry_contents=message, **kwargs
                )

                messages[i % modulus].append(
                    (append_result.transaction_id, message, kwargs)
                )

            num_matched = 0
            for i in range(modulus):
                query_result = self.client.get_ledger_entries(
                    from_transaction_id=messages[i][0][0], **messages[i][0][2]
                )
                index = 0
                async for historical_entry in query_result:
                    self.assertEqual(
                        historical_entry.transaction_id, messages[i][index][0]
                    )
                    self.assertEqual(historical_entry.contents, messages[i][index][1])
                    index += 1
                    num_matched += 1

            # Due to replication delay, it's possible not all messages are matched.
            self.assertGreaterEqual(num_matched, 0.9 * num_messages_sent)

        @AzureTestCase.await_prepared_test
        async def test_user_management(self):
            user_id = "0" * 36  # AAD Object Ids have length 36
            user = await self.client.create_or_update_user(
                user_id, LedgerUserRole.CONTRIBUTOR
            )
            self.assertEqual(user.id, user_id)
            self.assertEqual(user.role, LedgerUserRole.CONTRIBUTOR)

            user = await self.client.get_user(user_id)
            self.assertEqual(user.id, user_id)
            self.assertEqual(user.role, LedgerUserRole.CONTRIBUTOR)

            await self.client.delete_user(user_id)

            user = await self.client.create_or_update_user(
                user_id, LedgerUserRole.READER
            )
            self.assertEqual(user.id, user_id)
            self.assertEqual(user.role, LedgerUserRole.READER)

            user = await self.client.get_user(user_id)
            self.assertEqual(user.id, user_id)
            self.assertEqual(user.role, LedgerUserRole.READER)

            await self.client.delete_user(user_id)

        @AzureTestCase.await_prepared_test
        async def test_verification_methods(self):
            consortium = await self.client.get_consortium()
            self.assertEqual(len(consortium.members), 1)
            for member in consortium.members:
                self.assertTrue(member.certificate)
                self.assertTrue(member.id)

            constitution = await self.client.get_constitution()
            self.assertTrue(constitution.contents)
            self.assertTrue(constitution.digest)
            self.assertEqual(
                constitution.digest.lower(),
                hashlib.sha256(constitution.contents.encode()).hexdigest().lower(),
            )

            ledger_enclaves = await self.client.get_enclave_quotes()
            self.assertEqual(len(ledger_enclaves.quotes), 3)
            self.assertIn(ledger_enclaves.source_node, ledger_enclaves.quotes)
            for node_id, quote in ledger_enclaves.quotes.items():
                self.assertEqual(node_id, quote.node_id)
                self.assertTrue(quote.node_id)
                self.assertTrue(quote.mrenclave)
                self.assertTrue(quote.raw_quote)
                self.assertTrue(quote.version)
