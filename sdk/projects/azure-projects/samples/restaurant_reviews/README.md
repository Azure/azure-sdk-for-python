# Restaurant Review Flask App

A simple app demonstrating Azure Projects with Azure Tables.

## Getting started

Azure Projects is designed to work with the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview), to develop apps locally, deploy them to Azure, and monitor them. 

1. Sign up for a [free Azure account](https://azure.microsoft.com/free/)
2. Install the [Azure Dev CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd). (If you opened this repository in a Dev Container, it's already installed for you.)
3. Authorize `azd`:

    ```shell
    azd auth login
    ```

### Local deployment

Azure Projects supports local deployment for testing and debugging.
**Warning**
Running a local deployment will still deploy backend resources in Azure, which may accrue costs while the app is running locally. The Azure Projects deployment should be shutdown once no longer needed.

1. Create a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments) and activate it.

2. Install the requirements:

    ```shell
    python3 -m pip install -r requirements.txt
    ```

3. First provision the underlying infrastructure, then you can run the Flask
debug server:

    ```shell
    azproj infra.py provision
    flask --app app
    ```

4. The development server can be shutdown with `CTRL+C`. But please note that this will not automatically teardown the backend resources.

5. To shutdown the backend app deployment, run:

    ```shell
    azproj infra.py down
    ```
