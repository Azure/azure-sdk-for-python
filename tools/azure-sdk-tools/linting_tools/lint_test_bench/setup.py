"""Setup script for pylintBot package."""

import os
from setuptools import setup, find_packages

setup(
    name="pylintbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "azure-core>=1.29.5",
        "openai>=1.12.0",
        "azure-identity>=1.12.0"
    ],
    author="Microsoft Corporation",
    author_email="azpysdkhelp@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python",
    description="Azure SDK Linting Test Bench using OpenAI SDK",
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)