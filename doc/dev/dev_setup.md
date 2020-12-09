# Getting the tests to run

This section describes how to create a dev environment, in order to run the SDK tests,
or execute the various commands available in the toolbox.

## Setting up a virtual environment

1.  If you don't already have it, install Python:

    - Windows: https://www.python.org/downloads/ or from the [Windows store](ht tps://www.microsoft.com/p/python-37/9nj46sx7x90p)
    - Ubuntu/Debian `sudo apt-get install python3`
    - RHEL/CentOS `sudo yum install python3`

    Python is also available in Bash for Windows natively.

3.  Clone the repository and go to the folder

    ```
    git clone https://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python
    ```

2.  Create a [virtual environment](https://docs.python.org/3/tutorial/venv.html)
    You can initialize a virtual environment this way:

    ```
    python -m venv env # Might be "python3" or "py -3.6" depending on your Python installation
    source env/bin/activate      # Linux shell (Bash, ZSH, etc.) only
    ./env/scripts/activate       # PowerShell only
    ./env/scripts/activate.bat   # Windows CMD only
    ```

4. Setup your development environment

    Install the development requirements for a specific library (e.g. Azure Form Recognizer), [Tox](https://tox.readthedocs.io/en/latest/), and an editable install of your library:
    ```
    azure-sdk-for-python> cd sdk/formrecognizer/azure-ai-formrecognizer
    azure-sdk-for-python/sdk/formrecognizer/azure-ai-formrecognizer> pip install -r dev_requirements.txt
    azure-sdk-for-python/sdk/formrecognizer/azure-ai-formrecognizer> pip install tox tox-monorepo
    azure-sdk-for-python/sdk/formrecognizer/azure-ai-formrecognizer> pip install -e .
    ```

5.  Create a .env file to store your secrets.

    The recommended place to store your .env file is one directory higher than the `azure-sdk-for-python` location.
    This ensures the secrets will be loaded by the interpreter and most importantly not be committed to Git history.
