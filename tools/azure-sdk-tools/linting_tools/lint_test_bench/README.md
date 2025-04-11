# README

## Initial Setup


Install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Set the following environment variables:
```bash
export AZURE_OPENAI_ENDPOINT="<your-azure-openai-endpoint>"
export AZURE_OPENAI_MODEL="<your-azure-openai-model>"
export AZURE_OPENAI_VERSION="<your-azure-openai-version>"
export AZURE_OPENAI_KEY="<your-azure-openai-key>"
```


## Run the test bench
```bash
python pylint_test_bench.py
```

### Test Bench Output
The test bench will run pylint on the files in the /test_files directory. The final output will be saved under the /output-logs directory. To see the logging for a specific file, you can check the corresponding log file in the directory you are running in. The log files are named after the files they correspond to, with a .log extension. The output fixed pylint code will be saved under the /fixed_files directory. The fixed files are named after the original files, with a timestamp added to the name as they are iterated over. The output will also be printed to the console.