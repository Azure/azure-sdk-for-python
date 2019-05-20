# Microsoft Azure Cosmos Python SDK

Welcome to the repo containing all things Python for the Azure Cosmos DB API which is published with name [azure-cosmos](https://pypi.python.org/pypi/azure-cosmos/). For documentation please see the Microsoft Azure [link](https://docs.microsoft.com/en-us/azure/cosmos-db/sql-api-sdk-python).


## Pre-requirements

Python 2.7, Python 3.3, Python 3.4, or Python 3.5
https://www.python.org/downloads/

If you use Microsoft Visual Studio as IDE (we use 2015), please install the
following extension for Python.
http://microsoft.github.io/PTVS/

Install Cosmos DB emulator
Follow instruction at https://docs.microsoft.com/en-us/azure/cosmos-db/local-emulator 

## Installation:

    $ python setup.py install

    or

    $ pip install azure-cosmos


## Running Testing
Clone the repo 
```bash
git clone https://github.com/Azure/azure-cosmos-python.git
cd azure-cosmos-python
```

Most of the test files under test sub-folder require you to enter your Azure Cosmos master key and host endpoint: 
    
    masterKey = '[YOUR_KEY_HERE]'
    host = '[YOUR_ENDPOINT_HERE]'

To run the tests:

    $ python -m unittest discover -s .\test -p "*.py" 

    If you use Microsoft Visual Studio, open the project file python.pyproj,
    and run all the tests in Test Explorer.

**Note:**  
Most of the test cases create containers in your Cosmos account. Containers are billing entities. By running these test cases, you may incur monetary costs on your account.
  

## Documentation generation

    Install Sphinx: http://sphinx-doc.org/install.html

    $ cd doc
    $ sphinx-apidoc -f -e -o api ..\azure\cosmos
    $ make.bat html
