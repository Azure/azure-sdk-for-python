#!/usr/bin/env python

import os.path, nose, glob, sys, pkg_resources
packages = [os.path.dirname(p) for p in glob.glob('azure*/setup.py')]
sys.path += packages
# Declare it manually, because "azure-storage" is probably installed with pip
pkg_resources.declare_namespace('azure')

nose.main()