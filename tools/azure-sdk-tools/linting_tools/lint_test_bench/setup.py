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
    author="Your Name",
    author_email="your.email@example.com",
    description="Azure SDK Linting Bot using Azure OpenAI",
    python_requires=">=3.8",
)