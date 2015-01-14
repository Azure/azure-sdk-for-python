.. pydocumentdb documentation master file, created by
   sphinx-quickstart on Fri Jun 27 15:42:45 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Azure DocumentDB Python SDK.
========================================

System Requirements:
--------------------

    The supported Python versions are 2.7 and 2.7.x.
    To download Python version 2.7, please visit
    https://www.python.org/download/releases/2.7


    Python Tools for Visual Studio is required when using Microsoft Visual
	Studio to develop Python applications.  To download Python Tools for
	Visual Studio, please visit
	http://pytools.codeplex.com/wikipage?title=PTVS%20Installation


Installation:
-------------

    Method 1:

    1. Download the Azure DocumentDB Python SDK source from
       https://github.com/Azure/azure-documentdb-python.

    2. Execute the following setup script in bash shell:

       .. code-block:: bash

         $ python setup.py install

    Method 2:

    1. Install the Azure DocumentDB Python SDK using pip.
       For more information on pip, please visit https://pypi.python.org/pypi/pip

    2. Execute the following in bash shell:

       .. code-block:: bash

         $ pip install -pre pydocumentdb

To run tests:
-------------

    .. code-block:: bash

      $ python test/crud_tests.py

    If you use Microsoft Visual Studio, open the project file python.pyproj,
    and press F5.


To generate documentations:
---------------------------

    Install Sphinx: http://sphinx-doc.org/install.html

    .. code-block:: bash

      $ cd doc
      $ sphinx-apidoc -e -o .\api ..\pydocumentdb
      $ make.bat html


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
  :hidden:

  api/pydocumentdb
  api/modules