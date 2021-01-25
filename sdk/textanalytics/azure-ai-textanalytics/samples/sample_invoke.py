# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.pipeline.transport import HttpRequest, HttpResponse
from azure.core.exceptions import HttpResponseError
import json
import os


class InvokeSample(object):

    def invoke(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
            logging_enable=True
        )

        documents = [
            """
            The concierge Paulette was extremely helpful. Sadly when we arrived the elevator was broken, but with Paulette's help we barely noticed this inconvenience.
            She arranged for our baggage to be brought up to our room with no extra charge and gave us a free meal to refurbish all of the calories we lost from
            walking up the stairs :). Can't say enough good things about my experience!
            """,
            """
            最近由于工作压力太大，我们决定去富酒店度假。那儿的温泉实在太舒服了，我跟我丈夫都完全恢复了工作前的青春精神！加油！
            """
        ]
        documents = [{"id": str(idx), "text": doc} for idx, doc in enumerate(documents)]

        # Version 1 : Build your own body
        request = HttpRequest("POST", "/languages",
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                "documents": documents
            })
        )

        # Version 2 : Use setter to json.dumps for you
        request = HttpRequest("POST", "/languages",
            headers={
                'Content-Type': 'application/json'
            },
        )
        request.set_json_body({
            "documents": documents
        })
        try:
            pipeline_response = text_analytics_client.invoke(request)  # type: PipelineResponse
            response = pipeline_response.http_response
            if response.status_code < 200 or response.status_code >= 400:
                raise HttpResponseError(response=response)
            print(response.text())
        except HttpResponseError as err:
            print(err)
            print(err.response.text())


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    sample = InvokeSample()
    sample.invoke()
