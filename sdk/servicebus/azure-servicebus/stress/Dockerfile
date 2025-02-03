FROM mcr.microsoft.com/cbl-mariner/base/python:3

# To install a package from a git branch, add the line below to the end of the following installs:
# && yum install -y git
RUN yum update -y && yum install -y ca-certificates

WORKDIR /app

COPY ./scripts /app/stress/scripts

WORKDIR /app/stress/scripts
RUN pip install -r dev_requirements.txt
