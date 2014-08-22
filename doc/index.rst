.. pydocumentdb documentation master file, created by
   sphinx-quickstart on Fri Jun 27 15:42:45 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pydocumentdb's documentation!
========================================

Contents:

About This Documentation
------------------------
This documentation is generated using the `Sphinx
<http://sphinx.pocoo.org/>`_ documentation generator. The source files
for the documentation are located in the *doc/* directory of the
**PyDocumentDB** distribution. To generate the docs locally run the
following command from the root directory of the **PyDocumentDB** source:

.. code-block:: bash

  $ python setup.py install
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