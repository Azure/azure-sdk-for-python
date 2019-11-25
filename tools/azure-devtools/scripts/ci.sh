#!/usr/bin/env bash

pylint src/azure_devtools
pytest src/azure_devtools/scenario_tests/tests --cov=./