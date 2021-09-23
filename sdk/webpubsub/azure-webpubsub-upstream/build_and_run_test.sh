#!/bin/bash

declare -a PythonVersion=("3.5 3.6 3.7 3.8 3.9")

ImageName="azure-wps-upstream-py-sdk"

for version in $PythonVersion; do
    docker build -t $ImageName:$version --build-arg PythonVersion=$version .
    docker run $ImageName:$version
done