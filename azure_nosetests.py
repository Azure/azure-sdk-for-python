#!/usr/bin/env python

import os.path, nose, glob, sys
packages = [os.path.dirname(p) for p in glob.glob('azure*/setup.py')]
sys.path += packages

nose.main()