from setuptools import find_packages, setup

setup(
    name="azure-farmbeats",
    version="0.1.0",
    description="Azure Farmbeats Client Library v0",
    packages=find_packages(),
    author="Microsoft Corporation",
    license="MIT License",
    install_requires=[
        "azure-identity<2.0.0,>=1.5.0",
        "azure-core<2.0.0,>=1.12.0",
        "requests<3.0.0,>=2.23.0",
        "urllib3<2.0.0,>=1.25.8"
    ],
)
