# Deployment Template Unit Tests

This directory contains comprehensive unit tests for the Azure ML SDK deployment template functionality, providing 100% test coverage for entities and operations.

## Test Structure

```
tests/deployment_template/unittests/
├── __init__.py                                    # Package initialization
├── test_deployment_template.py                    # DeploymentTemplate entity tests
├── test_deployment_template_operations.py         # Operations layer tests
├── test_deployment_template_schema.py             # Schema and YAML loading tests
├── test_deployment_template_integration.py        # Integration and workflow tests
├── test_runner.py                                 # Test runner utilities
└── README.md                                      # This documentation
```

## Test Coverage Areas

### 1. DeploymentTemplate Entity Tests (`test_deployment_template.py`)

- **Initialization**: Basic and minimal field initialization
- **Field Handling**: Type/deployment_template_type field support
- **Serialization**: `_to_rest_object()` with camelCase field mapping
- **Deserialization**: `_from_rest_object()` with all field extraction
- **Data Validation**: Empty fields, None values, type checking
- **Edge Cases**: Large data sets, special characters, unicode support

### 2. Operations Layer Tests (`test_deployment_template_operations.py`)

- **CRUD Operations**: Create, Read, Update, Delete functionality
- **Input Types**: DeploymentTemplate objects, YAML files, PathLike objects
- **Error Handling**: HTTP errors, validation errors, file not found
- **Service Integration**: REST client calls, parameter validation
- **Edge Cases**: Large data, invalid inputs, authentication failures

### 3. Schema Tests (`test_deployment_template_schema.py`)

- **YAML Loading**: File parsing, data validation, object creation
- **Field Validation**: Required fields, optional fields, type checking
- **Serialization**: Round-trip load/dump consistency
- **Error Handling**: Invalid YAML, missing fields, type mismatches
- **Complex Data**: Nested structures, collections, unicode content

### 4. Integration Tests (`test_deployment_template_integration.py`)

- **Complete Workflows**: End-to-end CRUD operations
- **YAML to REST API**: File loading through API calls
- **Field Mapping**: Consistency throughout the workflow
- **Error Scenarios**: Complete error handling workflows
- **Performance**: Large data set handling

## Running Tests

### Prerequisites

```bash
# Ensure you're in the azure-sdk-for-python directory
cd c:\Projects\azure-sdk-for-python

# Activate your virtual environment
# Windows:
env\Scripts\activate
# Linux/macOS:
source env/bin/activate

# Install test dependencies
pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
# Run all deployment template tests
pytest tests/deployment_template/unittests/ --verbose

# Run with coverage reporting
pytest tests/deployment_template/unittests/ \
    --cov=azure.ai.ml.entities._deployment.deployment_template \
    --cov=azure.ai.ml.operations._deployment_template_operations \
    --cov=azure.ai.ml._schema._deployment.template.deployment_template \
    --cov-report=html --cov-report=term-missing
```

### Run Specific Test Categories

```bash
# Entity tests only
pytest tests/deployment_template/unittests/test_deployment_template.py --verbose

# Operations tests only
pytest tests/deployment_template/unittests/test_deployment_template_operations.py --verbose

# Schema tests only
pytest tests/deployment_template/unittests/test_deployment_template_schema.py --verbose

# Integration tests only
pytest tests/deployment_template/unittests/test_deployment_template_integration.py --verbose
```

### Using the Test Runner

```bash
# Run all tests with coverage
python tests/deployment_template/unittests/test_runner.py

# Run specific test categories
python tests/deployment_template/unittests/test_runner.py entity
python tests/deployment_template/unittests/test_runner.py operations
python tests/deployment_template/unittests/test_runner.py schema
python tests/deployment_template/unittests/test_runner.py integration
```

## Test Features

### Comprehensive Mocking

- REST client operations mocked for isolated testing
- File I/O operations mocked for consistent test environment
- HTTP response simulation for error handling scenarios

### Data Validation

- All supported field types and combinations tested
- Edge cases including empty values, None handling, large data sets
- Unicode and special character support validation

### Error Scenarios

- HTTP error codes (400, 404, 403, 500, 503)
- Validation errors and malformed input handling
- File system errors and authentication failures

### Performance Testing

- Large data set handling (100+ tags, 50+ properties)
- Complex nested data structures
- Memory efficiency validation

## Coverage Goals

The test suite aims for **100% code coverage** of:

- `azure.ai.ml.entities._deployment.deployment_template.DeploymentTemplate`
- `azure.ai.ml.operations._deployment_template_operations.DeploymentTemplateOperations`
- `azure.ai.ml._schema._deployment.template.deployment_template.DeploymentTemplateSchema`

### Coverage Validation

```bash
# Generate detailed coverage report
pytest tests/deployment_template/unittests/ \
    --cov=azure.ai.ml.entities._deployment.deployment_template \
    --cov=azure.ai.ml.operations._deployment_template_operations \
    --cov=azure.ai.ml._schema._deployment.template.deployment_template \
    --cov-report=html --cov-fail-under=100

# View HTML coverage report
# Open htmlcov/index.html in your browser
```

## Test Maintenance

### Adding New Tests

1. Follow existing naming conventions (`test_<functionality>_<scenario>`)
2. Include docstrings explaining test purpose
3. Use appropriate fixtures for setup/teardown
4. Mock external dependencies consistently

### Updating Tests

When modifying deployment template functionality:

1. Update corresponding test cases
2. Verify coverage remains at 100%
3. Test both success and failure scenarios
4. Validate field mapping consistency

### Best Practices

- One assertion per test when possible
- Clear test names describing the scenario
- Comprehensive error case coverage
- Mock external dependencies completely
- Test data should be realistic but minimal

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the correct directory and virtual environment is activated
2. **Missing Mocks**: All external dependencies should be mocked - check for unmocked service calls
3. **Coverage Gaps**: Use `--cov-report=html` to identify untested code paths
4. **Pylint Errors**: These may be related to test environment setup and can often be ignored for test files

### Debug Mode

```bash
# Run with debugging output
pytest tests/deployment_template/unittests/ --verbose --tb=long --pdb-trace

# Run single test for debugging
pytest tests/deployment_template/unittests/test_deployment_template.py::TestDeploymentTemplate::test_deployment_template_init --verbose --pdb
```

## Related Documentation

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
