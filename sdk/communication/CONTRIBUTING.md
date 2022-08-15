# Contributing Guide

This a contributing guide made specifically for the Azure Communication Services SDK. The Azure SDK repo also has a contributing guide that might help you in some other general processes this guide assumes you have done. If you haven't checked that one out yet, you can find it [here](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md)

The Azure Communication Services SDK for Python currently consists of 4 different packages. While each package has its own set of environment variables to make their tests run successfully, all of them follow a similar structure that allows a smooth onboarding process.

Let's get started with how to setup the repo itself.

## Installation process

To get started with any of the packages, change directory to the package you want to install and run the `pip install .` command. This will install all of the local files necessary for you to run the corresponding tests. It's important to note that if you made changes to the local files and want to run the tests again, you must run the `pip install .` command from the package root folder to update the files with your new changes.

In each SDK directory, run the following command to ensure packages to support development is installed correctly,
`python -m pip install -r .\dev_requirements.txt`.

Once the package has been installed on your machine, let's jump on how to run the tests to see that everything is in order.

## Testing

Make sure to check out the general contributing guide the Azure SDK repo has for a more in-depth look at testing and setting up your dev environment. You can check out the contributing file [here](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md)


When you go inside the tests folder of the package you are working with, you will see a folder called `recordings`. This folder contains, as its name suggests, recordings of successful calls to the API that allow us to run the tests in PLAYBACK mode and remove the necessity of hitting the actual resources every time we may want to test.

### Playback mode

To run the tests in PLAYBACK mode, set an environment variable called `AZURE_TEST_RUN_LIVE` and set its value to `false` (If the variable if not set, the default will be `false`). After your variable has been set, change directory to the `tests` folder of the package you're working on and run the `pytest .` command.

If the tests are successful, we can proceed to run the tests in LIVE mode.

### Live mode

Because in LIVE mode we are hitting an actual resource, we must set the appropriate environment variable to make sure the code tests against the resource we want. Set up an env variable called `COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING` (just needed for SMS and Phone Numbers SDKs) and set it to the connection string of the resource you want to test against.

Depending on which package you are testing, it may need special environment variables to test succesfully. The names of these variables can be found inside each test file in the `setUp()` function. Make sure to set these variables before running the tests themselves. You may need to restart your development environment after creating or updating these environment variables.

You can run the `pytest .` command after setting the `AZURE_TEST_RUN_LIVE` variable to `true`.

### Managed Identity Tests

If you ran the tests in LIVE mode, you may have noticed that the files inside the recordings folder were updated. If any of the tests failed, you will see the error message right there in the recording file as well as in your terminal logs.

The most probable thing is that the managed identity tests will fail at first. This is because we haven't set up any managed identity credentials for the DefaultAzureCredential object inside the tests to reference to. There are multiple ways of creating a managed identity credential.

One of the easiest ways is to install the [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) and run the `az login` command. If you are listed as a contributor of the resource you are testing against, this should be enough for the DefaultAzureCredential object to get the corresponding Azure Active Directory credentials you need.

Another way to authenticate is to set up 3 environment variables called `AZURE_CLIENT_ID`, `AZURE_TENANT_ID` and `AZURE_CLIENT_SECRET` and set their values to the ones from a registered Azure Active Directory application that is linked to the resource you are testing against.

If you are testing against a personal resource, you can check the [Managed Identity Quickstart Guide for ACS](https://docs.microsoft.com/azure/communication-services/quickstarts/managed-identity-from-cli) for an easy ramp-up process.

For a more in-depth look on how to authenticate using managed identity, refer to the [Azure Identity client library for Python](https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python) documentation. This document also has more ways for you to authenticate using the DefaultAzureCredential object besides the ones we discussed in this contributing file.

## Submitting a Pull Request

The easiest way for you to test and not worry about any breaking changes you may cause is to create a fork from the [Python Azure SDK repo](https://github.com/Azure/azure-sdk-for-python). After downloading your repo, make sure to add the original repo as an upstream. To do this, use the `git remote add upstream` command followed by the repo's URL.

Create a branch for any new feature you may want to add and when your changes are ready, push your branch to the origin. Because the upstream was already set, if you go to the Python Azure SDK repo you will see a message saying that you pushed changes to your fork and give you the option to create a PR from your fork to the original repo.

Make sure to name your PR with the following format when you are ready to submit it: [Communication] - `package-you-are-updating` - `pr-description`.

Additionally, write a good description about what your PR does in the description section of the PR itself. This will help your reviewers have a better understanding of what you are trying to accomplish in your PR.

## Samples

Each SDK has a samples folder where you can run example code for every function the SDK you are testing has to offer. These samples may have special requirements such as specific environment variables you may have to setup before running them. Make sure to take a look at these files and setup the environment as it is expected.

You can run these samples as you would run any other Python code snippet. First, change directory to the samples folder and then use the `python <name-of-the-sample-file>` command to run the code. Running these samples against a real resource may cost money depending on which SDK you are testing.