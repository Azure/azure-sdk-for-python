# APIView JSON to TXT Converter

This directory contains a Python script to convert APIView JSON files to TXT format.

## Directory Structure

```
apiview/
├── convert_json_to_txt.py    # Main conversion script
├── test/                      # Test directory
│   ├── test_convert_json_to_txt.py    # Unit and integration tests
│   └── data/                  # Test data
│       ├── azure-keyvault-secrets_python.json    # Sample JSON input
│       └── keyvault_secrets_4.10.0b1.txt         # Expected TXT output
└── README.md                  # This file
```

## Folders

### `test/`
Contains all test files and test data for validating the conversion script.

- **test_convert_json_to_txt.py** - Test suite covering:
  - Token processing logic
  - Review line processing with indentation
  - Full JSON to TXT conversion
  - Auto-generated filename validation

### `test/data/`
Contains sample files for testing:

- **azure-keyvault-secrets_python.json** - APIView JSON format example from azure-keyvault-secrets package
- **keyvault_secrets_4.10.0b1.txt** - Reference output in TXT format

## Usage

```bash
# Convert JSON to TXT with auto-generated filename
python convert_json_to_txt.py <input.json>

# Convert JSON to TXT with custom output filename
python convert_json_to_txt.py <input.json> <output.txt>
```

## Running Tests

```bash
python test/test_convert_json_to_txt.py
```

All 9 tests should pass.
