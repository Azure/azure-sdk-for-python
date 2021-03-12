from setuptools import find_packages, setup

setup(
    name="azure-farmbeats",
    version="0.1.0",
    description="Azure Farmbeats Client Library v0",
    packages=find_packages(),
    author="Microsoft Corporation",
    license="MIT License",
    install_requires=["azure-identity", "azure-core", "requests", "urllib3"],
)
