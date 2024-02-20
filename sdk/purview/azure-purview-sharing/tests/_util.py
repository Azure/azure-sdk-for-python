# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure_devtools.scenario_tests import RecordingProcessor
import json

class PurviewSharingRecordingProcessor(RecordingProcessor):
    def process_response(self, response):
        try:
            body = json.loads(response["body"]["string"])
            for value in body["value"]:
                value["properties"]["subscriptionId"] = "000"
            response["body"]["string"] = json.dumps(body)
        finally:
            return response