from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from baseTest import *
import unittest


class ExamplesTests(unittest.TestCase):

    @use_client
    def test_list_examples(self, client: LUISAuthoringClient):
            examples = client.examples.list(global_app_id, global_version_id)
            assert(len(examples) != 0)

    @use_client
    def test_list_examples_for_empty_application_returns_empty(self, client: LUISAuthoringClient):
            app_id = client.apps.add({
                'name': "Examples Tests App",
                'description': "New LUIS App",
                'culture': "en-us",
                'domain': "Comics",
                'usageScenario': "IoT"
            })
            examples = client.examples.list(app_id, global_version_id)
            client.apps.delete(app_id)
            assert(len(examples) == 0)

    @use_client
    def test_add_example(self, client: LUISAuthoringClient):
            app_id = client.apps.add({
                'name': "Examples Tests App",
                'description': "New LUIS App",
                'culture': "en-us",
                'domain': "Comics",
                'usageScenario': "IoT"
            })
            client.model.add_intent(app_id, "0.1", "WeatherInPlace")
            client.model.add_entity(app_id, "0.1", "Place")
            example = {
                'text': "whats the weather in buenos aires?",
                'intent_name': "WeatherInPlace",
                'entity_labels': [
                    {
                        'entity_name': "Place",
                        'start_char_index': 21,
                        'end_char_index': 34
                    }
                ]
            }
            result = client.examples.add(app_id, global_version_id, example)
            client.apps.delete(app_id)
            assert(example['text'] == result.utterance_text)

    @use_client
    def test_add_examples_in_batch(self, client: LUISAuthoringClient):
            app_id = client.apps.add({
                'name': "Examples Tests App",
                'description': "New LUIS App",
                'culture': "en-us",
                'domain': "Comics",
                'usageScenario': "IoT"
            })
            client.model.add_intent(app_id, "0.1", "WeatherInPlace")
            client.model.add_entity(app_id, "0.1", "Place")
            examples = [
                {
                    'text': "whats the weather in seattle?",
                    'intent_name': "WeatherInPlace",
                    'entity_labels': [
                        {
                            'entity_name': "Place",
                            'start_char_index': 21,
                            'end_char_index': 29
                        }
                    ]
                },
                {
                    'text': "whats the weather in buenos aires?",
                    'intent_name': "WeatherInPlace",
                    'entity_labels': [
                        {
                            'entity_name': "Place",
                            'start_char_index': 21,
                            'end_char_index': 34
                        }
                    ]
                }
            ]
            result = client.examples.batch(app_id, global_version_id, examples)
            client.apps.delete(app_id)

            assert(len(examples) == len(result))
            valid = True
            for r in result:
                assert(r.has_error == False)
                found = False
                for e in examples:
                    if r.value.utterance_text.lower() == e['text'].lower():
                        found = True
                valid = (found & valid)
            assert(valid == True)

    @use_client
    def test_add_examples_in_batch_some_invalid_examples_returns_some_errors(self, client: LUISAuthoringClient):
            app_id = client.apps.add({
                'name': "Examples Tests App",
                'description': "New LUIS App",
                'culture': "en-us",
                'domain': "Comics",
                'usageScenario': "IoT"
            })
            client.model.add_intent(app_id, "0.1", "WeatherInPlace")
            client.model.add_entity(app_id, "0.1", "Place")
            examples = [
                {
                    'text': "whats the weather in seattle?",
                    'intent_name': "InvalidIntent",
                    'entity_labels': [
                        {
                            'entity_name': "Place",
                            'start_char_index': 21,
                            'end_char_index': 29
                        }
                    ]
                },
                {
                    'text': "whats the weather in buenos aires?",
                    'intent_name': "IntentDoesNotExist",
                    'entity_labels': [
                        {
                            'entity_name': "Place",
                            'start_char_index': 21,
                            'end_char_index': 34
                        }
                    ]
                }
            ]
            result = client.examples.batch(app_id, global_version_id, examples)
            client.apps.delete(app_id)
            assert(len(examples) == len(result))

            has_error = False
            for r in result:
                if r.has_error == True:
                    has_error = True
            assert(has_error == True)

    @use_client
    def test_delete_example(self, client: LUISAuthoringClient):
            app_id = client.apps.add({
                'name': "Examples Tests App",
                'description': "New LUIS App",
                'culture': "en-us",
                'domain': "Comics",
                'usageScenario': "IoT"
            })
            example = {
                'text': "Abuamra is awesome",
                'intent_name': "None",
                'entity_labels': []
            }
            result = client.examples.add(app_id, global_version_id, example)
            example_id = result.example_id
            client.examples.delete(app_id, global_version_id, example_id)
            examples = client.examples.list(app_id, global_version_id)
            client.apps.delete(app_id)
            for e in examples:
                assert(e.id != example_id)
