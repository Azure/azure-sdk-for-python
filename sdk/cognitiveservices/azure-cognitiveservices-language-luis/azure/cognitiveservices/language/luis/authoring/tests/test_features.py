from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from baseTest import *
import unittest
import json


class FeaturesList(unittest.TestCase):

    @use_client
    def test_list_features(self, client: LUISAuthoringClient):
        with open('session_records/ImportApp.json') as json_file:
            app = json.load(json_file)
            app_id = client.apps.import_method(
                app, "Test list features of LUIS App")
            features = client.features.list(app_id, "0.1")
            print(app_id)
            client.apps.delete(app_id)
            assert(len(features.pattern_features) > 0)
            assert(len(features.phraselist_features) > 0)
