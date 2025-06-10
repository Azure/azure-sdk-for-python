import hashlib
import os
import time
from typing import Dict, List, Union
from urllib.parse import urlparse
from azure.core import exceptions
import pytest

from devtools_testutils import recorded_by_proxy
from devtools_testutils import (
    PemCertificate,
    create_combined_bundle,
    is_live,
    is_live_and_not_recording,
    set_function_recording_options,
)

from azure.confidentialledger import (
    ConfidentialLedgerCertificateCredential,
    ConfidentialLedgerClient,
)

from _shared.constants import (
    TEST_PROXY_CERT,
    USER_CERTIFICATE_THUMBPRINT,
    USER_CERTIFICATE_PRIVATE_KEY,
    USER_CERTIFICATE_PUBLIC_KEY,
)
from _shared.testcase import ConfidentialLedgerPreparer, ConfidentialLedgerTestCase


class TestConfidentialLedgerClient(ConfidentialLedgerTestCase):
    def create_confidentialledger_client(self, endpoint, ledger_id, use_aad_auth) -> ConfidentialLedgerClient:
        # Always explicitly fetch the TLS certificate.
        network_cert = self.set_ledger_identity(ledger_id)

        # The ACL instance should already have the potential AAD user added as an Administrator.
        credential = self.get_credential(ConfidentialLedgerClient)
        aad_based_client = self.create_client_from_credential(
            ConfidentialLedgerClient,
            credential=credential,
            endpoint=endpoint,
            ledger_certificate_path=self.network_certificate_path,  # type: ignore
        )

        certificate_credential = ConfidentialLedgerCertificateCredential(
            certificate_path=self.user_certificate_path
        )
        certificate_based_client = self.create_client_from_credential(
            ConfidentialLedgerClient,
            credential=certificate_credential,
            endpoint=endpoint,
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

        if not use_aad_auth:
            # We need to add the certificate-based user as an Administrator. 
            aad_based_client.create_or_update_ledger_user(
                USER_CERTIFICATE_THUMBPRINT, {"assignedRoles": ["Administrator"]}
            )

            # Sleep to make sure all replicas know the user is added.
            time.sleep(3)

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
    @recorded_by_proxy
    def test_append_entry_flow_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=True
        )
        self.append_entry_flow_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_append_entry_flow_aad_ledger_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=True
        )
        self.append_entry_flow_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_append_entry_flow_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=False
        )
        self.append_entry_flow_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_append_entry_flow_cert_ledger_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=False
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
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=True
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
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=False
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
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=True
        )
        self.range_query_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_range_query_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=False
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
    def test_user_endpoint_must_redirect(self, **kwargs):
        # all API versions earlier than 2024-08-26 will be redirected to use the /ledgerUsers endpoint
        # instead of the /users endpoint.
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=True
        )
    
        aad_user_id = "0" * 36  # AAD Object Ids have length 36
        cert_user_id = (
            "7F:75:58:60:70:A8:B6:15:A2:CD:24:55:25:B9:64:49:F8:BF:F0:E3:4D:92:EA:B2:8C:30:E6:2D:F4"
            ":77:30:1F"
        )

        for user_id in [aad_user_id, cert_user_id]:
            with pytest.raises(exceptions.HttpResponseError) as excinfo:
                client.create_or_update_user(user_id, {"assignedRole": "Contributor"})
            assert str(excinfo.value).startswith("(ApiVersionRedirect)")

            with pytest.raises(exceptions.HttpResponseError) as excinfo:
                client.delete_user(user_id)
            assert str(excinfo.value).startswith("(ApiVersionRedirect)")

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_user_management_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=True
        )
        self.user_management_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_user_management_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=False
        )
        self.user_management_actions(client)

    def user_management_actions(self, client):    
        aad_user_id = "0" * 36  # AAD Object Ids have length 36
        cert_user_id = (
            "7F:75:58:60:70:A8:B6:15:A2:CD:24:55:25:B9:64:49:F8:BF:F0:E3:4D:92:EA:B2:8C:30:E6:2D:F4"
            ":77:30:1F"
        )

        for user_id in [aad_user_id, cert_user_id]:
            client.delete_ledger_user(user_id)

            time.sleep(3)  # Let the DELETE user operation be committed, just in case.

            user = client.create_or_update_ledger_user(user_id, {"assignedRoles": ["Contributor"]})
            assert user["userId"] == user_id
            assert user["assignedRoles"] == ["Contributor"]

            time.sleep(3)  # Let the PATCH user operation be committed, just in case.

            user = client.get_ledger_user(user_id)
            assert user["userId"] == user_id
            assert user["assignedRoles"] == ["Contributor"]

            user = client.create_or_update_ledger_user(user_id, {"assignedRoles": ["Reader"]})
            assert user["userId"] == user_id
            assert user["assignedRoles"] == ["Reader"]

            time.sleep(3)  # Let the PATCH user operation be committed, just in case.

            user = client.get_ledger_user(user_id)
            assert user["userId"] == user_id
            assert user["assignedRoles"] == ["Contributor","Reader"]

            client.delete_ledger_user(user_id)

            time.sleep(3)  # Let the DELETE user operation be committed, just in case.

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_verification_methods_aad_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=True
        )
        self.verification_methods_actions(client)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_verification_methods_cert_user(self, **kwargs):
        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=False
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
            assert quote["raw"]
            assert quote["quoteVersion"]

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_tls_cert_convenience_aad_user(self, **kwargs):
        try:
            os.remove(self.network_certificate_path)  # Remove file so the auto-magic kicks in.
        except FileNotFoundError:
            pass

        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")

        # Create the client directly instead of going through the create_confidentialledger_client
        # as we don't need any additional setup.
        credential = self.get_credential(ConfidentialLedgerClient, is_async=False)
        self.create_client_from_credential(
            ConfidentialLedgerClient,
            credential=credential,
            endpoint=confidentialledger_endpoint,
            ledger_certificate_path=self.network_certificate_path,  # type: ignore
        )
        self.tls_cert_convenience_actions(confidentialledger_id)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_tls_cert_convenience_cert_user(self, **kwargs):
        try:
            os.remove(self.network_certificate_path)  # Remove file so the auto-magic kicks in.
        except FileNotFoundError:
            pass

        confidentialledger_endpoint = kwargs.pop("confidentialledger_endpoint")
        confidentialledger_id = kwargs.pop("confidentialledger_id")

        # Create the client directly instead of going through the create_confidentialledger_client
        # as we don't need any additional setup.
        certificate_credential = ConfidentialLedgerCertificateCredential(
            certificate_path=self.user_certificate_path
        )
        self.create_client_from_credential(
            ConfidentialLedgerClient,
            credential=certificate_credential,
            endpoint=confidentialledger_endpoint,
            ledger_certificate_path=self.network_certificate_path,  # type: ignore
        )
        self.tls_cert_convenience_actions(confidentialledger_id)

    def tls_cert_convenience_actions(self, confidentialledger_id: str):
        with open(self.network_certificate_path) as infile:
            certificate = infile.read()

        expected_cert = self.set_ledger_identity(confidentialledger_id)

        assert certificate == expected_cert

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_user_defined_endpoint(self, confidentialledger_endpoint, confidentialledger_id):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=True
        )

        # We need to add the certificate-based user as an Administrator. 
        user_endpoint = client.create_user_defined_endpoint(
            {
                "metadata": {
                    "endpoints": {
                        "/content": {
                            "get": {
                                "js_module": "test.js",
                                "js_function": "content",
                                "forwarding_required": "never",
                                "redirection_strategy": "none",
                                "authn_policies": ["no_auth"],
                                "mode": "readonly",
                                "openapi": {},
                            }
                        }
                    }
                },
                "modules": [
                    {
                        "name": "test.js",
                        "module": """
                        import { foo } from "./bar/baz.js";

                        export function content(request) {
                            return {
                                statusCode: 200,
                                body: {
                                    payload: foo(),
                                },
                            };
                        }
                        """,
                    },
                    {
                        "name": "bar/baz.js",
                        "module": """
                        export function foo() {
                            return "Test content";
                        }
                        """,
                    },
                ],
            }
        )

        saved_endpoint = client.get_user_defined_endpoint()
        assert saved_endpoint["metadata"]["endpoints"]["/content"]["GET"]["js_module"] == "test.js"

        # We are setting endpoints and modules to empty to have the UDF tests work since UDE and UDF cannot be created simultaneously.
        user_endpoint = {"metadata": {"endpoints": {}}, "modules": []}
        assert user_endpoint["metadata"]["endpoints"] == {}
        assert user_endpoint["modules"] == []

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_user_defined_role(self, confidentialledger_endpoint, confidentialledger_id):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=True
        )

        role_name = "modify"

        client.create_user_defined_role([{"role_name": role_name, "role_actions": ["/content/read"]}])
        time.sleep(3)

        roles = client.get_user_defined_role(role_name=role_name)
        assert roles[0]["role_name"] == role_name
        assert roles[0]["role_actions"] == ["/content/read"]

        client.update_user_defined_role(
            [
                {"role_name": role_name, "role_actions": ["/content/write", "/content/read"]}
            ]
        )
        time.sleep(3)

        roles = client.get_user_defined_role(role_name=role_name)
        assert roles[0]["role_name"] == role_name
        assert roles[0]["role_actions"] == ["/content/write", "/content/read"]

        client.delete_user_defined_role(role_name=role_name)
        time.sleep(3)

    @ConfidentialLedgerPreparer()
    @recorded_by_proxy
    def test_user_defined_function(self, confidentialledger_endpoint, confidentialledger_id):
        client = self.create_confidentialledger_client(
            confidentialledger_endpoint, confidentialledger_id, use_aad_auth=True
        )

        client.create_user_defined_endpoint({"metadata": {"endpoints": {}}, "modules": []})
        functionId = "myFunction"

        client.create_user_defined_function(functionId, {"code":"export function main() { return true }"} )
        time.sleep(3)                

        userFunction = client.get_user_defined_function(functionId)
        assert userFunction["code"] == "export function main() { return true }"

        client.delete_user_defined_function(functionId)
        time.sleep(3)