Microsoft Azure SDK for Python
==============================

.. image:: https://img.shields.io/pypi/v/azure.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/azure/

.. image:: https://img.shields.io/pypi/pyversions/azure.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/azure/

.. image:: http://www.quantifiedcode.com/api/v1/project/7e8a70bc3a1d445b95561f55712fee5a/badge.svg
    :target: http://www.quantifiedcode.com/app/project/7e8a70bc3a1d445b95561f55712fee5a

.. image:: https://travis-ci.org/Azure/azure-sdk-for-python.svg?branch=master
    :target: https://travis-ci.org/Azure/azure-sdk-for-python


This project provides a set of Python packages that make it easy to
access the Microsoft Azure components such as ServiceManagement, Storage\*, and ServiceBus.

The SDK supports Python 2.7, 3.3, 3.4 and 3.5.

\*Looking for the Azure Storage client library?  It moved to a `new GitHub repository <https://github.com/Azure/azure-storage-python>`__.

See important information if you're currently using this SDK < 1.0 in `this issue <https://github.com/Azure/azure-sdk-for-python/issues/440>`__.


INSTALLATION
============

``pip install azure``

If you want to install ``azure`` from source::

    git clone git://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python
    python setup.py install
	
If you need one specific package, you can install it directly, for instance:

``pip install azure-mgmt-compute``


DISCLAIMER ON PREVIEW VERSIONS
==============================

Please note that some packages are distributed as preview version and you will
need to tell pip:

- Use the ``--pre`` flag: ``pip install --pre azure-mgmt-web``

- Specify the version:  ``pip install azure-mgmt-web==0.30.0rc6``


Some of these generated libraries have not yet been tested extensively, and some have known issues.

Please send us your feedback!


Usage
=====

For detailed documentation, please view our `documentation on ReadTheDocs <http://azure-sdk-for-python.readthedocs.org>`__.

For further examples please visit the `Microsoft Azure Python Developer Center <http://azure.microsoft.com/en-us/develop/python/>`__.


Need Help?
==========

Be sure to check out the Microsoft Azure `Developer Forums on Stack Overflow <http://go.microsoft.com/fwlink/?LinkId=234489>`__
if you have trouble with the provided code.


Contribute Code or Provide Feedback
===================================

If you would like to become an active contributor to this project please
follow the instructions provided in `Microsoft Azure Projects Contribution Guidelines <http://azure.github.io/guidelines/>`__.

If you encounter any bugs with the library please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.


Learn More
==========

`Microsoft Azure Python Developer Center <http://azure.microsoft.com/en-us/develop/python/>`__
