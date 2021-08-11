# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure_devtools.scenario_tests import RecordingProcessor


class PurviewAccountRecordingProcessor(RecordingProcessor):
    def process_response(self, response):
        response["body"]["string"] = "private message"
        return response
