from azure.ai.generative._utils._open_ai_utils import build_open_ai_protocol

class TestOpenAIUtils:
    def test_passes_with_existing_open_ai_protocol(self):
        protocol = "azure_open_ai://deployment/my-deployment-name/model/my-model-name"
        assert(build_open_ai_protocol(protocol) == protocol)

    def test_passes_with_model_name(self):
        protocol = "my-model-name"
        assert(build_open_ai_protocol(protocol) == "azure_open_ai://deployment/my-model-name/model/my-model-name")

    def test_passes_with_none_model_name(self):
        protocol = None
        assert(build_open_ai_protocol(protocol) == None)
