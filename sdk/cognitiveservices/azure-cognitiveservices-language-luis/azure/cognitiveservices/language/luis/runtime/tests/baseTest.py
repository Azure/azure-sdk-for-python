from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials

authoring_key = "b15ebe3a1ec446a08f8021fe6f95f0f6"
appId = "0894d430-8f00-4bcd-8153-45e06a1feca1"
versionId = "0.1"
utterance = "today this is a test with post"
slotName = "production"
externalResolution = {'text': "post", 'external': True}
timezoneOffset = -360
verbose = True
isStaging = False


def use_client(test):
    def do_test(*args, **kwargs):
        client = LUISRuntimeClient(
            'https://westus.api.cognitive.microsoft.com',
            CognitiveServicesCredentials(authoring_key),
        )
        kwargs['client'] = client
        return test(*args, **kwargs)
    return do_test
