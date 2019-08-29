from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from msrest.authentication import CognitiveServicesCredentials

global_app_id = "e7f5f63a-efec-4215-815c-d0ed28106c0c"
global_version_id = "0.1"
global_app_id_error = "86226c53-b7a6-416f-876b-226b2b5ab07d"
global_none_id = "ed986e25-d092-412e-8a2b-9efefa3ee549"
authoring_key = "b15ebe3a1ec446a08f8021fe6f95f0f6"
empty_id = "00000000-0000-0000-0000-000000000000"
owner_email = "a-ahabu@microsoft.com"
closed_list_sample = {
    'name': "States",
    'sub_lists': [
        {
            "canonical_form": "New York",
            "list": ["ny", "new york"]
        },
        {
            "canonical_form": "Washington",
            "list": ["wa", "washington"]
        },
        {
            "canonical_form": "California",
            "list": ["ca", "california", "calif.", "cal."]
        }
    ]
}


def use_client(test):
    def do_test(*args, **kwargs):
        client = LUISAuthoringClient(
            'https://westus.api.cognitive.microsoft.com',
            CognitiveServicesCredentials(authoring_key),
        )
        kwargs['client'] = client
        return test(*args, **kwargs)
    return do_test
