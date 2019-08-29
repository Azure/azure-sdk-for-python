from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from baseTest import *
import unittest
import json


class ImportExport(unittest.TestCase):

    @use_client
    def test_export_version(self, client: LUISAuthoringClient):
        app_id = client.apps.add({
            'name': "LUIS App to be exported",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        app = client.versions.export(app_id, global_version_id)
        client.apps.delete(app_id)
        assert(app is not None)
        assert("LUIS App to be exported" == app.name)

    @use_client
    def test_import_version(self, client: LUISAuthoringClient):
        with open('session_records/ImportApp.json') as json_file:
            app = json.load(json_file)
            testapp_id = client.apps.add({
                'name': "App To Be Imported",
                'description': "New LUIS App",
                'culture': "en-us",
                'domain': "Comics",
                'usageScenario': "IoT"
            })

            try:
                newVersion = client.versions.import_method(
                    testapp_id, app, "0.2")
            except Exception as ex:
                print(ex.error)
            finally:
                client.apps.delete(testapp_id)

            assert("0.2" == newVersion)

    @use_client
    def test_import_app(self, client: LUISAuthoringClient):
        with open('session_records/ImportApp.json') as json_file:
            app = json.load(json_file)
            app_id = client.apps.import_method(
                app, "Test list features of LUIS App")
            testapp_id = client.apps.import_method(app, "Test Import LUIS App")
            testApp = client.apps.get(testapp_id)
            client.apps.delete(testapp_id)
            assert(testApp is not None)
