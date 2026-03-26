---
name: generate-api-markdown
description: Generate an API markdown file and token file using ApiView. Use this when the user wants to generate an API markdown file and review API changes.
---

# Generate API Markdown

## Prerequisites

1. Activate your virtual environment with a Python version that is strictly less than the version limit specified in `eng/tools/azure-sdk-tools/azpysdk/apistub.py`.
2. Install the required dependencies:
   ```bash
   cd <repo_root>
   pip install -e ./eng/tools/azure-sdk-tools
   ```

## Instructions

1. Navigate to the desired package directory
2. Run the command:
   ```bash
   azpysdk apistub --md .
3. The command outputs the location of the generated markdown file. Provide this file to the user for review.