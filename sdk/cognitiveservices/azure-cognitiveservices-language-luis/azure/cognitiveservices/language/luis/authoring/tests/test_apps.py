from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from baseTest import *
import unittest


class AppsTests(unittest.TestCase):

    @use_client
    def test_list_applications(self, client: LUISAuthoringClient):
        app_id = client.apps.add({
            'name': "Existing LUIS App",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        list = client.apps.list()
        client.apps.delete(app_id)
        assert(list is not None)
        assert(len(list) != 0)

    @use_client
    def test_add_application(self, client: LUISAuthoringClient):
        app_id = client.apps.add({
            'name': "New LUIS App",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        saved_app = client.apps.get(app_id)
        client.apps.delete(app_id)
        assert(saved_app is not None)
        assert(saved_app.name == "New LUIS App")
        assert(saved_app.description == "New LUIS App")
        assert(saved_app.culture == "en-us")
        assert(saved_app.domain == "Comics")
        assert(saved_app.usage_scenario == "IoT")

    @use_client
    def test_get_application(self, client: LUISAuthoringClient):
        app_id = client.apps.add({
            'name': "Existing LUIS App",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        result = client.apps.get(app_id)
        client.apps.delete(app_id)
        assert(result is not None)
        assert(result.id == app_id)
        assert(result.name == "Existing LUIS App")
        assert(result.culture == "en-us")
        assert(result.domain == "Comics")
        assert(result.usage_scenario == "IoT")

    @use_client
    def test_update_application(self, client: LUISAuthoringClient):
        app_id = client.apps.add({
            'name': "LUIS App to be renamed",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        client.apps.update(app_id, "LUIS App name updated",
                           "LUIS App description updated")
        app = client.apps.get(app_id)
        client.apps.delete(app_id)
        assert(app is not None)
        assert(app.name == "LUIS App name updated")
        assert(app.description == "LUIS App description updated")

    @use_client
    def test_delete_application(self, client: LUISAuthoringClient):
        app_id = client.apps.add({
            'name': "LUIS App to be deleted",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        client.apps.delete(app_id)
        list = client.apps.list()
        for app in list:
            assert(app.name != "LUIS App to be deleted")

    @use_client
    def test_list_endpoints(self, client: LUISAuthoringClient):
        app_id = client.apps.add({
            'name': "Existing LUIS App",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        result = client.apps.list_endpoints(app_id)
        client.apps.delete(app_id)
        assert(result["westus"] ==
               "https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/" + app_id)
        assert(result["eastus2"] ==
               "https://eastus2.api.cognitive.microsoft.com/luis/v2.0/apps/" + app_id)
        assert(result["westcentralus"] ==
               "https://westcentralus.api.cognitive.microsoft.com/luis/v2.0/apps/" + app_id)
        assert(result["southeastasia"] ==
               "https://southeastasia.api.cognitive.microsoft.com/luis/v2.0/apps/" + app_id)

    @use_client
    def test_publish_application(self, client: LUISAuthoringClient):
        result = client.apps.publish(global_app_id, "0.1", False)
        assert(result.endpoint_url ==
               "https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/" + global_app_id)
        assert(result.endpoint_region == "westus")
        assert(result.is_staging == False)

    @use_client
    def test_download_query_logs(self, client: LUISAuthoringClient):
        app_id = client.apps.add({
            'name': "Existing LUIS App",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        stream = client.apps.download_query_logs(app_id)
        assert(stream is not None)
        client.apps.delete(app_id)

    @use_client
    def test_get_settings(self, client: LUISAuthoringClient):
        app_id = client.apps.add({
            'name': "Existing LUIS App",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        settings = client.apps.get_settings(app_id)
        client.apps.delete(app_id)
        assert(settings.is_public == False)
        assert(settings.id == app_id)

    @use_client
    def test_update_settings(self, client: LUISAuthoringClient):
        app_id = client.apps.add({
            'name': "Existing LUIS App",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        client.apps.update_settings(app_id, True)
        settings = client.apps.get_settings(app_id)
        client.apps.delete(app_id)
        assert(settings.is_public == True)

    @use_client
    def test_get_publish_settings(self, client: LUISAuthoringClient):
        test_app_id = client.apps.add({
            'name': "LUIS App for Settings test",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        settings = client.apps.get_publish_settings(test_app_id)
        client.apps.delete(test_app_id)

        assert(test_app_id == settings.id)
        assert(settings.is_sentiment_analysis_enabled == False)
        assert(settings.is_speech_enabled == False)
        assert(settings.is_spell_checker_enabled == False)

    @use_client
    def test_update_publish_settings(self, client: LUISAuthoringClient):
        app_id = client.apps.add({
            'name': "Existing LUIS App",
            'description': "New LUIS App",
            'culture': "en-us",
            'domain': "Comics",
            'usageScenario': "IoT"
        })
        client.apps.update_publish_settings(app_id, {'sentiment_analysis': True,
                                                     'speech': True,
                                                     'spell_checker': True
                                                     })
        settings = client.apps.get_publish_settings(app_id)
        client.apps.delete(app_id)
        assert(settings.is_sentiment_analysis_enabled == True)
        assert(settings.is_speech_enabled == True)
        assert(settings.is_spell_checker_enabled == True)

    @use_client
    def test_list_domains(self, client: LUISAuthoringClient):
        result = client.apps.list_domains()
        for domain in result:
            assert(domain is not None)

    @use_client
    def test_list_supported_cultures(self, client: LUISAuthoringClient):
        cultures_map = {
            'en-us': 'English',
            'zh-cn': 'Chinese',
            'fr-fr': 'French',
            'fr-ca': 'French Canadian',
            'es-es': 'Spanish',
            'es-mx': 'Spanish Mexican',
            'it-it': 'Italian',
            'de-de': 'German',
            'ja-jp': 'Japanese',
            'pt-br': 'Brazilian Portuguese',
            'ko-kr': 'Korean',
            'nl-nl': 'Dutch',
            'tr-tr': 'Turkish'
        }
        result = client.apps.list_supported_cultures()
        for culture in result:
            name = cultures_map[culture.code]
            assert(name.lower() == culture.name.lower())

    @use_client
    def test_list_usage_scenarios(self, client: LUISAuthoringClient):
        result = client.apps.list_usage_scenarios()
        for scenario in result:
            assert(scenario is not None)

    @use_client
    def test_list_available_custom_prebuild_domains(self, client: LUISAuthoringClient):
        result = client.apps.list_available_custom_prebuilt_domains()
        for prebuilt in result:
            assert(prebuilt is not None)
            assert(prebuilt.description is not None)
            assert(prebuilt.intents is not None)
            assert(prebuilt.entities is not None)

    # "list available custom prebuilt domains for culture", fails because of reported culture issue
    # def test_list_available_custom_prebuilt_domains_for_culture(self, client: LUISAuthoringClient):
    #     resultsUS = client.apps.list_available_custom_prebuilt_domains_for_culture(
    #         culture="en-us")
    #     resultsCN = client.apps.list_available_custom_prebuilt_domains_for_culture(
    #         culture="zh-cn")
    #     for resultUS in resultsUS:
    #         for resultCN in resultsCN:
    #             assert(resultCN.description != resultUS.description)

    @use_client
    def test_add_custom_prebuilt_domain(self, client: LUISAuthoringClient):
        app_id = client.apps.add_custom_prebuilt_domain(
            culture="en-us",
            domain_name="Communication"
        )
        client.apps.delete(app_id)
        assert(app_id != empty_id)
