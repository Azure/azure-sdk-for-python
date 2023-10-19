# Dev Setup

## Installing in Development mode
To install `azure-ai-generative` in development mode

To isolate environment, install Anaconda3, open "Anaconda Powershell Prompt" and run the following:

```shell
conda create -n azure-ai-generative -y python=3.8
conda activate azure-ai-generative
```

- Navigate to `azure-ai-generative` folder
- Run `pip install -e .[tests]`. This command should be run from `azure-ai-generative` directory


To use `evaluate` install extra `[evaluate]` by running:

```
 pip install -e .[evaluate] --extra-index-url=https://azuremlsdktestpypi.azureedge.net/Create-Dev-Index/102333570
```

To use MLIndex and QA Generation related features include the `[index, qa_generation]` extras:

```
pip install -e .[tests,index,cognitive_search,faiss,document_parsing,hugging_face,qa_generation]
```

To install promptflow as an extra, run:

```
pip install -e .[promptflow] --extra-index-url https://azuremlsdktestpypi.azureedge.net/promptflow/
```

## Generating whl locally

To generate whl locally run following command:
- Run `python setup.py bdist_wheel` from `azure-ai-generative` directory
- Above command will create `dist` directory which has `.whl` and `.tar.gz` file.
- Run `pip install <location to .whl file>` this should install `azure-ai-generative` sdk

## Testing

Make sure to install test dependencies:

```shell
pip install pytest pytest-asyncio
```

### Unit tests

To run QA Generation e2e tests, run the following:

```shell
cd .\src\azure-ai-generative\tests\test-qa
pytest -m unittest --log-level DEBUG --log-cli-level DEBUG .
```

### E2E tests

To run QA Generation e2e tests, run the following:

```shell
$Env:OPENAI_API_BASE="https://<example>.openai.azure.com/"
$Env:OPENAI_API_KEY="<aoai-key>"
cd .\src\azure-ai-generative\tests\test-qa\e2etests
pytest -m e2etest --log-level DEBUG --log-cli-level DEBUG .
```