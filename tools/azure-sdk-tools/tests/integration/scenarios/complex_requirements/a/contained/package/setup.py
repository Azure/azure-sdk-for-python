from setuptools import setup, find_packages

version = "1.0.0b1"

setup(
    name="coretestserver",
    version=version,
    include_package_data=True,
    description="A fake package that can be installed",
    license="MIT License",
    author="Microsoft Corporation",
    packages=find_packages(),
    install_requires=[
        "flask==2.2.2",
    ],
)
