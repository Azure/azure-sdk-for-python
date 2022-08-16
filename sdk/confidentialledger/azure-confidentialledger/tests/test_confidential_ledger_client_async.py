import asyncio
import hashlib
import os
from typing import Dict, List, Union
from urllib.parse import urlparse

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import (
    PemCertificate,
    create_combined_bundle,
    is_live,
    is_live_and_not_recording,
    set_function_recording_options,
)

from azure.confidentialledger.aio import ConfidentialLedgerClient
from azure.confidentialledger import ConfidentialLedgerCertificateCredential

from _shared.constants import (
    TEST_PROXY_CERT,
    USER_CERTIFICATE_THUMBPRINT,
    USER_CERTIFICATE_PRIVATE_KEY,
    USER_CERTIFICATE_PUBLIC_KEY,
)
from _shared.testcase import ConfidentialLedgerPreparer, ConfidentialLedgerTestCase


class TestConfidentialLedgerClient(ConfidentialLedgerTestCase):
    async def create_confidentialledger_client(
        self, endpoint, ledger_id, is_aad, fetch_tls_cert=True
    ):
        # Always explicitly fetch the TLS certificate.
        network_cert = await self.set_ledger_identity_async(ledger_id)
        if not fetch_tls_cert:
            # For some test scenarios, remove the file so the client sees it doesn't exist and
            # creates it auto-magically.
            os.remove(self.network_certificate_path)

        # The ACL instance should already have the potential AAD user added as an Administrator.
        credential = self.get_credential(ConfidentialLedgerClient, is_async=True)
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

        # The Confidential Ledger always presents a self-signed certificate, so add that certificate
        # to the recording options for the Confidential Ledger endpoint.
        function_recording_options: Dict[str, Union[str, List[PemCertificate]]] = {
            "tls_certificate": network_cert,
            "tls_certificate_host": urlparse(endpoint).netloc,
        }
        if is_live():
            set_function_recording_options(**function_recording_options)

        if not is_live_and_not_recording():
            # For live, non-recorded tests, we want to test normal client behavior so the only
            # certificate used for TLS verification is the Confidential Ledger identity certificate.
            #
            # However, in this case outbound connections are to the proxy, so the certificate used
            # for verifying the TLS connection should actually be the test proxy's certificate.
            # With that in mind, we'll update the file at self.network_certificate_path to be a
            # certificate bundle including both the ledger's TLS certificate (though technically
            # unnecessary I think) and the test-proxy certificate. This way the client setup (i.e.
            # the logic for overriding the default certificate verification) is still tested when
            # the test-proxy is involved.
            #
            # Note the combined bundle should be created *after* any os.remove calls so we don't 
            # interfere with auto-magic certificate retrieval tests.
            create_combined_bundle(
                [self.network_certificate_path, TEST_PROXY_CERT],
                self.network_certificate_path
            )

        if not is_aad:
            # We need to add the certificate-based user as an Administrator.
            try:
                await aad_based_client.create_or_update_user(
                    USER_CERTIFICATE_THUMBPRINT, {"assignedRole": "Administrator"}
                )
            finally:
                await aad_based_client.close()

            # Sleep to make sure all replicas know the user is added.
            await asyncio.sleep(3)

            # Update the options to account for certificate-based authentication.
            function_recording_options["certificates"] = [
                PemCertificate(key=USER_CERTIFICATE_PRIVATE_KEY, data=USER_CERTIFICATE_PUBLIC_KEY)
            ]
            if is_live():
                set_function_recording_options(**function_recording_options)

            client = certificate_based_client
        else:
            client = aad_based_client

        return client

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_append_entry_flow_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True
        )
        try:
            await self.append_entry_flow_actions(client)
        finally:
            await client.close()

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_append_entry_flow_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False
        )
        try:
            await self.append_entry_flow_actions(client)
        finally:
            await client.close()

    async def append_entry_flow_actions(self, client):
        entry_contents = "Test entry from Python SDK"
        append_result = await client.create_ledger_entry({"contents": entry_contents})
        assert append_result["transactionId"]
        assert append_result["collectionId"]

        append_result_sub_ledger_id = append_result["collectionId"]
        append_result_transaction_id = append_result["transactionId"]

        poller = await client.begin_wait_for_commit(
            transaction_id=append_result_transaction_id
        )
        await poller.wait()

        transaction_status = await client.get_transaction_status(
            transaction_id=append_result_transaction_id
        )
        assert transaction_status["transactionId"] == append_result_transaction_id
        assert transaction_status["state"] == "Committed"

        poller = await client.begin_get_receipt(
            transaction_id=append_result_transaction_id
        )
        receipt = await poller.result()
        assert receipt["transactionId"] == append_result_transaction_id
        assert receipt["receipt"]

        latest_entry = await client.get_current_ledger_entry()
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

        poller = await client.begin_create_ledger_entry(
            {"contents": "Test entry 2 from Python SDK"}
        )
        await poller.wait()

        latest_entry = await client.get_current_ledger_entry()
        assert latest_entry["transactionId"] != append_result_transaction_id
        assert latest_entry["contents"] != entry_contents
        assert latest_entry["collectionId"] == append_result_sub_ledger_id

        poller = await client.begin_get_ledger_entry(
            transaction_id=append_result_transaction_id
        )
        original_entry = await poller.result()
        assert original_entry["entry"]["transactionId"] == append_result_transaction_id
        assert original_entry["entry"]["contents"] == entry_contents
        assert original_entry["entry"]["collectionId"] == append_result_sub_ledger_id

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_append_entry_flow_with_collection_id_aad_user(
        self, **kwargs,
    ):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True
        )
        try:
            await self.append_entry_flow_with_collection_id_actions(client)
        finally:
            await client.close()

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_append_entry_flow_with_collection_id_cert_user(
        self, **kwargs,
    ):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False
        )
        try:
            await self.append_entry_flow_with_collection_id_actions(client)
        finally:
            await client.close()

    async def append_entry_flow_with_collection_id_actions(self, client):
        collection_id = "132"
        entry_contents = f"Test entry from Python SDK. Collection: {collection_id}"
        append_result = await client.create_ledger_entry(
            {"contents": entry_contents},
            collection_id=collection_id,
        )
        assert append_result["transactionId"]
        assert append_result["collectionId"] == collection_id

        append_result_sub_ledger_id = append_result["collectionId"]
        append_result_transaction_id = append_result["transactionId"]

        poller = await client.begin_wait_for_commit(
            transaction_id=append_result_transaction_id
        )
        await poller.wait()

        transaction_status = await client.get_transaction_status(
            transaction_id=append_result_transaction_id
        )
        assert transaction_status
        assert transaction_status["state"] == "Committed"

        poller = await client.begin_get_receipt(
            transaction_id=append_result_transaction_id
        )
        receipt = await poller.result()
        assert receipt["transactionId"] == append_result_transaction_id
        assert receipt["receipt"]

        latest_entry = await client.get_current_ledger_entry(
            collection_id=collection_id
        )
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

        poller = await client.begin_create_ledger_entry(
            {"contents": f"Test entry 2 from Python SDK. Collection: {collection_id}"},
            collection_id=collection_id,
        )
        await poller.wait()

        latest_entry = await client.get_current_ledger_entry(
            collection_id=collection_id
        )
        assert latest_entry["transactionId"] != append_result_transaction_id
        assert latest_entry["contents"] != entry_contents
        assert latest_entry["collectionId"] == collection_id

        poller = await client.begin_get_ledger_entry(
            transaction_id=append_result_transaction_id,
            collection_id=collection_id,
        )
        original_entry = await poller.result()
        assert original_entry["entry"]["transactionId"] == append_result_transaction_id
        assert original_entry["entry"]["contents"] == entry_contents
        assert original_entry["entry"]["collectionId"] == append_result_sub_ledger_id

        collections = client.list_collections()
        collection_ids = set()
        async for collection in collections:
            collection_ids.add(collection["collectionId"])
        assert collection_id in collection_ids

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_range_query_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True
        )
        try:
            await self.range_query_actions(client)
        finally:
            await client.close()

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_range_query_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False
        )
        try:
            await self.range_query_actions(client)
        finally:
            await client.close()

    async def range_query_actions(self, client):
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
                append_result = await client.create_ledger_entry(
                    {"contents": message}, **kwargs
                )
            else:
                append_poller = await client.begin_create_ledger_entry(
                    {"contents": message},
                    **kwargs
                )
                append_result = await append_poller.result()

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
            index = 0
            async for historical_entry in query_result:
                assert historical_entry["transactionId"] == messages[i][index][0]
                assert historical_entry["contents"] == messages[i][index][1]
                collection_id = messages[i][index][2].get("collection_id", None)
                if collection_id is not None:
                    assert historical_entry["collectionId"] == collection_id

                index += 1
                num_matched += 1

        assert num_matched == num_messages_sent

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_user_management_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True
        )
        try:
            await self.user_management_actions(client)
        finally:
            await client.close()

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_user_management_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False
        )
        try:
            await self.user_management_actions(client)
        finally:
            await client.close()

    async def user_management_actions(self, client):
        aad_user_id = "0" * 36  # AAD Object Ids have length 36
        cert_user_id = (
            "7F:75:58:60:70:A8:B6:15:A2:CD:24:55:25:B9:64:49:F8:BF:F0:E3:4D:92:EA:B2:8C:30:E6:2D:F4"
            ":77:30:1F"
        )
        for user_id in [aad_user_id, cert_user_id]:
            user = await client.create_or_update_user(
                user_id, {"assignedRole": "Contributor"}
            )
            assert user["userId"] == user_id
            assert user["assignedRole"] == "Contributor"

            await asyncio.sleep(3)  # Let the PATCH user operation be committed, just in case.

            user = await client.get_user(user_id)
            assert user["userId"] == user_id
            assert user["assignedRole"] == "Contributor"

            user = await client.create_or_update_user(
                user_id, {"assignedRole": "Reader"}
            )
            assert user["userId"] == user_id
            assert user["assignedRole"] == "Reader"

            await asyncio.sleep(3)  # Let the PATCH user operation be committed, just in case.

            user = await client.get_user(user_id)
            assert user["userId"] == user_id
            assert user["assignedRole"] == "Reader"

            await client.delete_user(user_id)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_verification_methods_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True
        )
        try:
            await self.verification_methods_actions(client)
        finally:
            await client.close()

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_verification_methods_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False
        )
        try:
            await self.verification_methods_actions(client)
        finally:
            await client.close()

    async def verification_methods_actions(self, client):
        consortium = client.list_consortium_members()
        consortium_size = 0
        async for member in consortium:
            assert member["certificate"]
            assert member["id"]
            consortium_size += 1
        assert consortium_size == 1

        constitution = await client.get_constitution()
        assert constitution["script"]
        assert constitution["digest"]
        assert (
            constitution["digest"].lower() == 
            hashlib.sha256(constitution["script"].encode()).hexdigest().lower()
        )

        ledger_enclaves = await client.get_enclave_quotes()
        assert len(ledger_enclaves["enclaveQuotes"]) == 3
        assert ledger_enclaves["currentNodeId"] in ledger_enclaves["enclaveQuotes"]
        for node_id, quote in ledger_enclaves["enclaveQuotes"].items():
            assert node_id == quote["nodeId"]
            assert quote["nodeId"]
            assert quote["mrenclave"]
            assert quote["raw"]
            assert quote["quoteVersion"]

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_tls_cert_convenience_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=True, fetch_tls_cert=False,
        )
        try:
            await self.tls_cert_convenience_actions(client)
        finally:
            await client.close()

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy_async
    async def test_tls_cert_convenience_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = await self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, is_aad=False, fetch_tls_cert=False,
        )
        try:
            await self.tls_cert_convenience_actions(client)
        finally:
            await client.close()

    async def tls_cert_convenience_actions(self, client):
        # It's sufficient to use any arbitrary endpoint to test the TLS connection.
        constitution = await client.get_constitution()
        assert constitution["script"]
