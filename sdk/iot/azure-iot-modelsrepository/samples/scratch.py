from azure.iot.modelsrepository import ModelsRepositoryClient
import pprint

client = ModelsRepositoryClient(repository_location="https://devicemodels.azure.com")
models = client.get_models(["dtmi:com:example:TemperatureController;1"])
pprint.pprint(models)

