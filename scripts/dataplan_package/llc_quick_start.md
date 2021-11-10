The documentation describes how to generate LLC code with autorest

# Prerequisites

- Python 3.6 or later is required

- Nodejs 14.x.x or later is required


# Prepare Environment(Windows)

assume work path is `D:\`

1. create virtual environment

   ```
   python venv venv-dev
   .\venv-dev4\Scripts\Activate.ps1
   ```

2. prepare SDK repo if needed

   ```
   git clone https://github.com/Azure/azure-sdk-for-python.git
   ```

3. prepare autorest

   ```
   npm install -g autorest
   ```


# Generate code(Windows)

If it is the first time for service to generate SDK, you need the [script](llc_initial.py) to help generate necessary files(setup.py, CHANGELOG.md, etc) and go to [Create](#Create);If you just want to update code, go to [Update](#Update)

## Create

Before using the script, you need to run the following command:

```
pip install -r D:\azure-sdk-for-python\scripts\dataplan_package\dev_requirements.txt
```

### Parameter Introduction

The scripts needs necessary parameters to generate SDK code:

- `--input-file`: absolute path or url path of swagger input file. For example: `https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/webpubsub/data-plane/WebPubSub/stable/2021-10-01/webpubsub.json` or `D:\azure-rest-api-specs\specification\webpubsub\data-plane\WebPubSub\stable\2021-10-01\webpubsub.json`
- `--output-folder`: absolute path where generated SDK package will be put
- `--package-name`: package name. For example: "azure-messaging-webpubsub"
- `--package-pprint-name`: print name of the package. For example: "Azure Web PubSub Service"
- `--client-name`: client name. For example: "WebPubSubServiceClient"
- `--credential-scope`: each service for data plan has specific scopes. For example: " https://webpubsub.azure.com/.default"

Here is the example, just try to run it:

```
python D:\azure-sdk-for-python\scripts\dataplan_package\llc_initial.py --output-folder D:\azure-sdk-for-python\sdk\llcexample\azure-messaging-webpubsubservic --input-file https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/webpubsub/data-plane/WebPubSub/stable/2021-10-01/webpubsub.json --credential-scope https://webpubsub.azure.com/.default --package-name azure-messaging-webpubsubserviceexample --package-pprint-name "Azure WebPubSub Service" --client-name WebPubSubServiceClient
```

After running the scripts successfully, it creates necessary files and common test framework. **But remember to edit `README.md`, test files under `tests` and sample files under `samples`  since customers need more info to understand the package.**

You don't need it anymore after one-time successful run. Go to [Update](#Update) if you need to regenerate code.

## Update

After [Create](#Create), there will be `READMD.md` under `swagger` folder of `output_folder`. If need to update the code, run the following command:

```
autorest --version=3.6.2 --python --track2 --use=@autorest/python@5.11.1 --use=@autorest/modelerfour@4.19.2 --python-mode=update D:\azure-sdk-for-python\sdk\llcexample\azure-messaging-webpubsubserviceexample\swagger\README.md
```

If you want to try latest autorest, run the following command:

```
autorest --python --track2 --use=@autorest/python@latest --use=@autorest/modelerfour@latest --python-mode=update D:\azure-sdk-for-python\sdk\llcexample\azure-messaging-webpubsubserviceexample\swagger\README.md
```











