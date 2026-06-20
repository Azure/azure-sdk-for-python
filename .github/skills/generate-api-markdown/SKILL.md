---
name: generate-api-markdown
description: Generate an API markdown file and token file using ApiView. Use this when the user wants to generate an API markdown file and review API changes.
---

# Generate API Markdown

## Prerequisites

1. Activate your virtual environment.
2. Install the required dependencies:
   ```bash
   cd <repo_root>
   pip install -e ./eng/tools/azure-sdk-tools
   ```

## Instructions

1. Navigate to the desired package directory
2. Run the command:
   ```bash
   azpysdk apistub .
   ```
3. The command generates `api.md` and `api.metadata.yml` in the package directory, which are the files needed to pass the API consistency check. Provide these files to the user for review.
4. If the user explicitly asks for the raw APIView token file, run `azpysdk apistub . --token-file` instead.