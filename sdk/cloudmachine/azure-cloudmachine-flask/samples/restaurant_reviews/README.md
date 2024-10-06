# Restaurant Review Flask App

A simple app demonstrating CloudMachine with Azure Tables.

## Getting started

CloudMachine is designed to work with the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview), to develop apps locally, deploy them to Azure, and monitor them. 

1. Sign up for a [free Azure account](https://azure.microsoft.com/free/)
2. Install the [Azure Dev CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd). (If you opened this repository in a Dev Container, it's already installed for you.)
3. Authorize `azd`:

    ```shell
    azd auth login
    ```

### Local deployment

CloudMachine supports local deployment for testing and debugging.
**Warning**
Running a local deployment will still deploy backend resources in Azure, which may accrew costs while the app is running locally. The CloudMachine deployment should be shutdown once no longer needed.

1. Create a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments) and activate it.

2. Install the requirements:

    ```shell
    python3 -m pip install -r requirements.txt
    ```

3. Run the Flask app using the `cm` CLI:

    ```shell
    flask --app app cm run
    ```

4. The app will now be running at the default endpoint `http://127.0.0.1:5000`. In order to configure the Flask development server, settings can be passed in before `cm`:

    ```shell
    flask --app app --debug -p 5001 cm run
    ```
5. The development server can be shutdown with `CTRL+C`. But please note that this will not automatically teardown the backend resources. Running the `cm run` command again will update the resource deployment if any modifications have been made to the `CloudMachineDeployment`.

6. To shutdown the backend app deployment, run:

    ```shell
    flask --app app cm down
    ```
