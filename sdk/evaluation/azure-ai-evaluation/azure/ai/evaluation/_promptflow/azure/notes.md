# Notes about removing azure-ai-ml

- Do we need to use the AzureMLOnBehalfOfCredential?
  - This seems to be used for:
    - [Azure Machine Learning Compute](https://docs.microsoft.com/azure/machine-learning/concept-compute-target#azure-machine-learning-compute-managed)
    - [Azure Machine Learning Serverless Spark Compute](https://learn.microsoft.com/en-us/azure/machine-learning/apache-spark-azure-ml-concepts#serverless-spark-compute)

- Do we need to check the PF_USE_AZURE_CLI_CREDENTIAL environment variable to determine if we want to use the Azure CLI credential?
