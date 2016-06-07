This is the README of the Python driver for Microsoft Azure DocumentDB.

Welcome to DocumentDB.


0) Pre-requirements:

    Python 2.7
    https://www.python.org/download/releases/2.7


    If you use Microsoft Visual Studio as IDE (we use 2013), please install the
    following extension for Python.
    http://microsoft.github.io/PTVS/


1) Installation:

    $ python setup.py install

    or

    $ pip install pydocumentdb


2) Testing:

Some of the test files such as [crud_tests.py](https://github.com/Azure/azure-documentdb-python/blob/fe95945cae62ee4a68ae53bc5519bec11f07522c/test/crud_tests.py) require you to enter your Azure DocumentDB master key and host endpoint in that file: 
    
    masterKey = '[YOUR_KEY_HERE]'
    host = '[YOUR_ENDPOINT_HERE]'

To run the tests:

    $ python test/crud_tests.py

    If you use Microsoft Visual Studio, open the project file python.pyproj,
    and press F5.

**Note:**  
Test cases in [crud_tests.py](https://github.com/Azure/azure-documentdb-python/blob/fe95945cae62ee4a68ae53bc5519bec11f07522c/test/crud_tests.py) create collections in your DocumentDB account. Collections are billing entities. By running these test cases, you may incur monetary costs on your account.
  

3) To generate documentations:

    Install Sphinx: http://sphinx-doc.org/install.html

    $ cd doc
    $ sphinx-apidoc -e -o .\api ..\pydocumentdb
    $ make.bat html