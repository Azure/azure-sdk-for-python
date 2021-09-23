#!/bin/sh
python setup.py develop
pip install -r dev_requirements.txt
pytest tests