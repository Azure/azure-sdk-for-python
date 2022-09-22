Microsoft Azure SDK for Python
==============================

.. image:: https://img.shields.io/pypi/v/azure.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/azure/

.. image:: https://img.shields.io/pypi/pyversions/azure.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/azure/

.. image:: https://dev.azure.com/azure-sdk/public/_apis/build/status/46?branchName=master
    :target: https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46&branchName=master

.. image:: https://travis-ci.org/Azure/azure-sdk-for-python.svg?branch=master
    :target: https://travis-ci.org/Azure/azure-sdk-for-python

.. image:: https://img.shields.io/badge/dependencies-analyzed-blue.svg
    :target: https://azuresdkartifacts.blob.core.windows.net/azure-sdk-for-python/dependencies/dependencies.html

This project provides a set of Python packages that make it easy to
access Management (Virtual Machines, ...) or Runtime (ServiceBus using HTTP, Batch, Monitor) components of
`Microsoft Azure <https://azure.microsoft.com/>`_
Complete feature list of this repo and where to find Python packages not in this repo can be found on our 
`Azure SDK for Python documentation <https://docs.microsoft.com/python/api/overview/azure/?view=azure-python>`__.

The SDK supports Python 2.7, 3.4, 3.5 and 3.6.

If you're currently using the ``azure`` package < 1.0 then please read important information in `this issue <https://github.com/Azure/azure-sdk-for-python/issues/440>`__.


INSTALLATION
============

You can install each Azure service's library individually:

.. code-block:: console

   $ pip install azure-batch          # Install the latest Batch runtime library
   $ pip install azure-mgmt-storage   # Install the latest Storage management library

Preview packages can be installed using the ``--pre`` flag:

.. code-block:: console

   $ pip install --pre azure-mgmt-compute # will install only the latest Compute Management library


The full list of available packages and their latest version can be found on our 
`documentation on docs.microsoft.com <https://docs.microsoft.com/python/azure/>`__

If you want to install all packages of the repo from source::

    git clone git://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python
    python setup.py install

Usage
=====

For detailed documentation, please view our `documentation on docs.microsoft.com <https://docs.microsoft.com/python/azure/>`__. 

For further samples please visit the `Azure Samples website <https://azure.microsoft.com/resources/samples/?platform=python>`__.

Tests
=====

For detailed documentation about our test framework, please visit this `Azure SDK test tutorial <https://github.com/Azure/azure-sdk-for-python/wiki/Contributing-to-the-tests>`__.

Need Help?
==========

Be sure to check out the Microsoft Azure `Developer Forums on Stack Overflow <http://go.microsoft.com/fwlink/?LinkId=234489>`__
if you have trouble with the provided code. Most questions are tagged `azure and python <https://stackoverflow.com/questions/tagged/azure+python>`__.


Contribute Code or Provide Feedback
===================================

If you would like to become an active contributor to this project please
follow the instructions provided in `Microsoft Azure Projects Contribution Guidelines <http://azure.github.io/guidelines/>`__.

If you encounter any bugs with the library please file an issue in the
`Issues <https://github.com/Azure/azure-sdk-for-python/issues>`__
section of the project.

Code of Conduct 
===============

This project has adopted the `Microsoft Open Source Code of Conduct <https://opensource.microsoft.com/codeofconduct/>`__. For more information see the `Code of Conduct FAQ <https://opensource.microsoft.com/codeofconduct/faq/>`__ or contact `opencode@microsoft.com <mailto:opencode@microsoft.com>`__ with any additional questions or comments.

Learn More
==========

`Microsoft Azure Python Developer Center <http://azure.microsoft.com/en-us/develop/python/>`__


.. image::  https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2FREADME.png
