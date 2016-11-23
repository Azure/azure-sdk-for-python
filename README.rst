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
access the Microsoft Azure components such as ServiceManagement, Storage\*, and ServiceBus.

The SDK supports Python 2.7, 3.3, 3.4 and 3.5.

\*Looking for the Azure Storage client library?  It moved to a `new GitHub repository <https://github.com/Azure/azure-storage-python>`__.

See important information if you're currently using this SDK < 1.0 in `this issue <https://github.com/Azure/azure-sdk-for-python/issues/440>`__.


INSTALLATION
============

**The latest recommended release is currently a release candidate, tell this to pip to install it!**

The `azure` bundle meta-package will install all Azure SDKs at once:

- Use the ``--pre`` flag: ``pip install --pre azure``

- Specify the version:  ``pip install azure==2.0.0rc6``

You can also install only what you exactly need:

- Use the ``--pre`` flag: ``pip install --pre azure-mgmt-compute``

- Specify the version:  ``pip install azure-mgmt-compute==0.30.0rc6``

If you want to install ``azure`` from source::

    git clone git://github.com/Azure/azure-sdk-for-python.git
    cd azure-sdk-for-python
    python setup.py install

DISCLAIMER
==========

This is a release candidate. However, the core packages, from code quality/completeness perspectives can at this time be considered "stable" - 
it will be officially labeled as such in September (in sync with other languages).

We are not planning on any further major changes until then.

The following packages are still labeled "preview" but can be considered "stable":

- azure-mgmt-resource 0.31.0
- azure-mgmt-compute 0.32.0
- azure-mgmt-network 0.30.0
- azure-mgmt-storage 0.30.0rc6
- azure-mgmt-keyvault 0.30.0

The following packages are already released as "stable" and are officially production ready:

- azure-batch 1.1.0
- azure-mgmt-batch 2.0.0
- azure-mgmt-devtestlabs 1.0.0
- azure-mgmt-logic 1.0.0
- azure-mgmt-redis 2.0.0
- azure-mgmt-scheduler 1.0.0
- azure-mgmt-servermanager 1.0.0
- azure-servicebus 0.20.3
- azure-servicemanagement-legacy 0.20.5
- azure-storage 0.33.0

The following packages are also available as preview only, not ready for production,
and will NOT be installed with the 2.0.0rc6 "azure" meta-package. We removed then from the 2.0.0rc6
to prepare our customers to the 2.0.0 stable release that will only contains the stable packages
listed before.

- azure-graphrbac 0.30.0rc6
- azure-monitor 0.1.0
- azure-mgmt-authorization 0.30.0rc6
- azure-mgmt-cdn 0.30.0rc6
- azure-mgmt-cognitiveservices 0.30.0rc6
- azure-mgmt-containerregistry 0.1.0
- azure-mgmt-datalake-analytics 0.1.0
- azure-mgmt-datalake-store 0.1.0
- azure-mgmt-commerce 0.30.0rc6
- azure-mgmt-eventhub 0.1.0
- azure-mgmt-dns 0.30.0rc6
- azure-mgmt-iothub 0.1.0
- azure-mgmt-media 0.1.0
- azure-mgmt-notificationhubs 0.30.0
- azure-mgmt-powerbiembedded 0.30.0rc6
- azure-mgmt-servicebus 0.1.0
- azure-mgmt-sql 0.1.0
- azure-mgmt-trafficmanager 0.30.0rc6
- azure-mgmt-web 0.30.1


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
