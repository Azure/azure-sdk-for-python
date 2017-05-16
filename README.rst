Microsoft Azure SDK for Python
==============================

.. image:: https://img.shields.io/pypi/v/azure.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/azure/

.. image:: https://img.shields.io/pypi/pyversions/azure.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/azure/

.. image:: https://travis-ci.org/Azure/azure-sdk-for-python.svg?branch=master
    :target: https://travis-ci.org/Azure/azure-sdk-for-python

.. image:: https://ci.appveyor.com/api/projects/status/m51hrgewcxknxhsd/branch/master?svg=true
    :target: https://ci.appveyor.com/project/lmazuel/azure-sdk-for-python/branch/master

This project provides a set of Python packages that make it easy to
access Management (Virtual Machines, ...) or Runtime (ServiceBus using HTTP, Batch, Monitor) components of
`Microsoft Azure <https://azure.microsoft.com/>`_
Complete feature list of this repo and where to find Python packages not in this repo can be found on our 
`Azure SDK for Python features chapter on ReadTheDocs <http://azure-sdk-for-python.readthedocs.io/en/latest/index.html#features>`__.

The SDK supports Python 2.7, 3.3, 3.4, 3.5 and 3.6.

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


You can also install a set of Azure libraries in a single line using the ``azure`` meta-package. 

.. code-block:: console

   $ pip install azure

We publish a preview version of this package, which you can access using the `--pre` flag:

.. code-block:: console

   $ pip install --pre azure

The full list of available packages and their latest version can be found on our 
`installation page on ReadTheDocs <http://azure-sdk-for-python.rtfd.io/en/latest/installation.html>`__.

If you want to install all packages of the repo from source::

    git clone git://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python
    python setup.py install

Usage
=====

For detailed documentation, please view our `documentation on ReadTheDocs <http://azure-sdk-for-python.readthedocs.org>`__.

For further examples please visit the `Microsoft Azure Python Developer Center <http://azure.microsoft.com/en-us/develop/python/>`__
or the `Azure Samples website <https://azure.microsoft.com/en-us/resources/samples/?platform=python>`__.


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
