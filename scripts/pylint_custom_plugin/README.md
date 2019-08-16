## Pylint Guidelines 

In order to lint for the guidelines, you must make sure you are using the pylintrc file.

How to run pylint locally using the pylintrc (settings file):

1. Run pylint at the root of the repo and it will automatically find the pylintrc:
    ```bash
    C:\azure-sdk-for-python>pylint sdk/storage/azure-storage-blob/azure/storage/blob
    ```
2. Add the --rcfile command line argument with a relative path to the pylintrc from your current directory:
    ```bash
    C:\azure-sdk-for-python\sdk\storage\azure-storage-blob\azure\storage>pylint --rcfile="../../../../../pylintrc" blob
    ```
3. Set the environment variable PYLINTRC to the absolute path of the pylintrc file:
    ```bash
    set PYLINTRC=C:\azure-sdk-for-python\pylintrc
    ```
    Run pylint:
    ```bash
    C:\azure-sdk-for-python\sdk\storage\azure-storage-blob\azure\storage>pylint blob
    ```
4. Run pylint at the package level using tox and it will find the pylintrc file:
    ```bash
    C:\azure-sdk-for-python\sdk\storage\azure-storage-blob>tox -c ../../../eng/tox/tox.ini -e lint
    ```

How to disable a pylint error:
```bash
# pylint:disable=missing-client-creation-from-connection-string
```

Guidelines that are currently linted:

