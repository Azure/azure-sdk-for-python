from setuptools import find_packages, setup

setup(
    name="farmbeats",
    packages=find_packages(),
    version="0.1.0",
    description="Farmbeats SDK v0",
    author="Agnivesh",
    license="Restricted",
    install_requires=["azure-identity", "azure-core", "requests", "urllib3"],
)
