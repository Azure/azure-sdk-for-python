# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import requests

from azure_devtools.perfstress_tests import PerfStressTest


class RequestsGetTest(PerfStressTest):
    async def global_setup(self):
        type(self).session = requests.Session()

    def run_sync(self):
        type(self).session.get(self.args.url).text

    @staticmethod
    def add_arguments(parser):
        parser.add_argument("-u", "--url", required=True)
