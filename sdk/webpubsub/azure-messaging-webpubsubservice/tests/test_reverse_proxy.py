# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubservice._operations._operations import build_send_to_all_request
from azure.core.credentials import AzureKeyCredential
from testcase import WebpubsubTest, WebpubsubPowerShellPreparer
from azure.identity import DefaultAzureCredential

class WebpubsubReverseProxyTest(WebpubsubTest):

    def test_reverse_proxy_endpoint_redirection_azure_key_credential(self):
        def _callback(pipeline_request):
            assert pipeline_request.http_request.url.startswith("https://apim.contoso.com/")
            raise ValueError("Success!")
        wps_endpoint = "https://wps.contoso.com/"
        apim_endpoint = "https://apim.contoso.com/"
        credential = AzureKeyCredential("abcdabcdabcdabcdabcdabcdabcdabcd")
        client = WebPubSubServiceClient(wps_endpoint, "Hub", credential, reverse_proxy_endpoint=apim_endpoint)
        request = build_send_to_all_request('Hub', content='test_webpubsub_send_request', content_type='text/plain')

        with pytest.raises(ValueError) as ex:
            client.send_request(request, raw_request_hook=_callback)
        assert "Success!" in str(ex.value)

    def test_reverse_proxy_endpoint_redirection_identity(self):
        def _callback(pipeline_request):
            assert pipeline_request.http_request.url.startswith("https://apim.contoso.com/")
            raise ValueError("Success!")
        wps_endpoint = "https://wps.contoso.com/"
        apim_endpoint = "https://apim.contoso.com/"
        credential = self.get_credential(WebPubSubServiceClient)
        client = WebPubSubServiceClient(wps_endpoint, "Hub", credential, reverse_proxy_endpoint=apim_endpoint)
        request = build_send_to_all_request('Hub', content='test_webpubsub_send_request', content_type='text/plain')

        with pytest.raises(ValueError) as ex:
            client.send_request(request, raw_request_hook=_callback)
        assert "Success!" in str(ex.value)

    @WebpubsubPowerShellPreparer()
    def test_reverse_proxy_call(self, webpubsub_connection_string, webpubsub_reverse_proxy_endpoint):
        client = self.create_client(
            connection_string=webpubsub_connection_string,
            hub='hub',
            logging_enable=True,
            reverse_proxy_endpoint=webpubsub_reverse_proxy_endpoint
        )
        client.send_to_all({'Hello': 'reverse_proxy_endpoint!'})
