.. azure-cosmos documentation master file, created by
   sphinx-quickstart on Fri Jun 27 15:42:45 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Azure Cosmos Python SDK
========================================

System Requirements:
--------------------

    The supported Python versions are 2.7, 3.3, 3.4 and 3.5. To download Python, please visit https://www.python.org/download/releases.


    Python Tools for Visual Studio is required when using Microsoft Visual
    Studio to develop Python applications. To download Python Tools for Visual Studio, please visit http://microsoft.github.io/PTVS.


Installation:
-------------

    Method 1:

    1. Download the Azure Cosmos Python SDK source from
       https://github.com/Azure/azure-cosmos-python which is needed to manage the Azure Cosmos database service.

    2. Execute the following setup script in bash shell:

       .. code-block:: bash

         $ python setup.py install

    Method 2:

    1. Install the Azure Cosmos Python SDK using pip.
       For more information on pip, please visit https://pypi.python.org/pypi/pip

    2. Execute the following in bash shell:

       .. code-block:: bash

         $ pip install azure-cosmos

To run tests:
-------------

    .. code-block:: bash

      $ python -m unittest discover -s .\test -p "*.py"

    If you use Microsoft Visual Studio, open the project file python.pyproj,
    and run all the tests in Test Explorer.


To generate documentations:
---------------------------

    Install Sphinx: http://sphinx-doc.org/install.html

    .. code-block:: bash

      $ cd doc
      $ sphinx-apidoc -f -e -o api ..\azure
      $ make.bat html


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
  :hidden:

  api/azure
  api/modules