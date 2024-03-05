from azure.ai.resources._index._models import parse_model_uri


def test_parse_model_uri():
    config = parse_model_uri("azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002", endpoint="azureml-rag-oai")
    assert config["kind"] == "open_ai"
    assert config["api_type"] == "azure"
    assert config["api_version"] == "2023-03-15-preview"
    assert config["api_base"] == "https://azureml-rag-oai.openai.azure.com"

    config = parse_model_uri("azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002", endpoint="https://azureml-rag-oai.openai.azure.com")
    assert config["kind"] == "open_ai"
    assert config["api_type"] == "azure"
    assert config["api_version"] == "2023-03-15-preview"
    assert config["api_base"] == "https://azureml-rag-oai.openai.azure.com"
    assert config["deployment"] == "text-embedding-ada-002"
    assert config["model"] == "text-embedding-ada-002"

    config = parse_model_uri("azure_open_ai://deployment/text-embedding-ada-002", endpoint="https://azureml-rag-oai.openai.azure.com")
    assert config["kind"] == "open_ai"
    assert config["api_type"] == "azure"
    assert config["api_version"] == "2023-03-15-preview"
    assert config["api_base"] == "https://azureml-rag-oai.openai.azure.com"
    assert config["deployment"] == "text-embedding-ada-002"
    assert "model" not in config