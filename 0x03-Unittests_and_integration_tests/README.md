# 0x03. Unittests and Integration Tests

This project focuses on implementing comprehensive unit tests and integration tests for Python applications, emphasizing the difference between unit tests and integration tests, and demonstrating various testing patterns and mocking techniques.

## Learning Objectives

By the end of this project, you should be able to:

- Understand the difference between unit and integration tests
- Implement common testing patterns such as mocking, parametrizations, and fixtures
- Use the `unittest` framework effectively
- Apply mocking to isolate units of code during testing
- Use parameterized tests to test multiple scenarios efficiently
- Implement integration tests with proper setup and teardown

## Requirements

- All files will be interpreted/compiled on Ubuntu 18.04 LTS using Python 3.7
- All files should end with a new line
- The first line of all files should be exactly `#!/usr/bin/env python3`
- A `README.md` file at the root of the project folder is mandatory
- Code should use the `pycodestyle` style (version 2.5)
- All files must be executable
- All modules should have documentation
- All classes should have documentation
- All functions (inside and outside a class) should have documentation
- Documentation should be a real sentence explaining the purpose of the module, class, or method

## Dependencies

Install the required packages:

```bash
pip install parameterized
```

## Project Structure

```
0x03-Unittests_and_integration_tests/
├── README.md
├── utils.py                 # Utility functions to be tested
├── client.py               # GitHub API client to be tested
├── fixtures.py             # Test fixtures for integration tests
├── test_utils.py           # Unit tests for utils module
└── test_client.py          # Unit and integration tests for client module
```

## Files Description

### Core Files (Provided)

- **`utils.py`**: Contains utility functions including `access_nested_map`, `get_json`, and `memoize` decorator
- **`client.py`**: Contains the `GithubOrgClient` class for interacting with GitHub API
- **`fixtures.py`**: Contains test fixtures and payload data for integration tests

### Test Files (Implemented)

- **`test_utils.py`**: Unit tests for utility functions
- **`test_client.py`**: Unit and integration tests for the GitHub client

## Tasks Overview

### Task 0: Parameterize a unit test
- Test the `utils.access_nested_map` function
- Use `@parameterized.expand` to test multiple input scenarios
- Verify the function returns expected results

### Task 1: Parameterize a unit test - Exception handling
- Test that `utils.access_nested_map` raises `KeyError` for invalid paths
- Use `assertRaises` context manager
- Verify exception messages are correct

### Task 2: Mock HTTP calls
- Test the `utils.get_json` function
- Mock `requests.get` to avoid actual HTTP calls
- Verify mocked methods are called correctly

### Task 3: Parameterize and patch
- Test the `utils.memoize` decorator
- Use `unittest.mock.patch` to mock methods
- Verify memoization works correctly (method called only once)

### Task 4: Parameterize and patch as decorators
- Test `client.GithubOrgClient.org` property
- Use `@patch` decorator to mock `get_json`
- Parameterize tests for multiple organizations

### Task 5: Mocking a property
- Test `client.GithubOrgClient._public_repos_url` property
- Use `patch` as context manager to mock the `org` property
- Verify the URL is constructed correctly

### Task 6: More patching
- Test `client.GithubOrgClient.public_repos` method
- Mock both `get_json` and `_public_repos_url`
- Verify the list of repositories is returned correctly

### Task 7: Parameterize
- Test `client.GithubOrgClient.has_license` method
- Parameterize tests for different license scenarios
- Test both positive and negative cases

### Task 8: Integration test with fixtures
- Create integration tests for `GithubOrgClient.public_repos`
- Use `@parameterized_class` with fixtures
- Implement proper `setUpClass` and `tearDownClass` methods
- Mock only external requests, not internal methods

## Running the Tests

### Run all tests:
```bash
python -m unittest discover
```

### Run specific test file:
```bash
python -m unittest test_utils.py
python -m unittest test_client.py
```

### Run specific test class:
```bash
python -m unittest test_utils.TestAccessNestedMap
python -m unittest test_client.TestGithubOrgClient
```

### Run specific test method:
```bash
python -m unittest test_utils.TestAccessNestedMap.test_access_nested_map
python -m unittest test_client.TestGithubOrgClient.test_org
```

### Run tests with verbose output:
```bash
python -m unittest -v test_utils.py
python -m unittest -v test_client.py
```

## Key Testing Concepts Demonstrated

### 1. Unit Testing vs Integration Testing
- **Unit Tests**: Test individual functions/methods in isolation
- **Integration Tests**: Test the interaction between multiple components

### 2. Mocking Strategies
- **`unittest.mock.patch`**: Temporarily replace objects during testing
- **`Mock` objects**: Create fake objects that simulate real behavior
- **`PropertyMock`**: Mock properties specifically
- **Context managers**: Use `with patch()` for temporary mocking

### 3. Parameterized Testing
- **`@parameterized.expand`**: Run the same test with different inputs
- **`@parameterized_class`**: Parameterize entire test classes
- Reduces code duplication and improves test coverage

### 4. Fixtures and Test Data
- **`setUpClass`/`tearDownClass`**: Class-level setup and cleanup
- **`setUp`/`tearDown`**: Method-level setup and cleanup
- **Fixtures**: Predefined test data for consistent testing

### 5. Assertion Methods
- **`assertEqual`**: Test equality
- **`assertRaises`**: Test exception handling
- **`assert_called_once`**: Verify mock methods are called correctly
- **`assert_called_with`**: Verify mock methods are called with specific arguments

## Best Practices Implemented

1. **Test Isolation**: Each test is independent and doesn't affect others
2. **No External Dependencies**: All external calls are mocked
3. **Clear Test Names**: Test method names clearly describe what they test
4. **Comprehensive Coverage**: Tests cover both success and failure scenarios
5. **Proper Setup/Teardown**: Resources are properly managed
6. **Documentation**: All test classes and methods are documented

## Common Testing Patterns

### Mocking HTTP Requests
```python
@patch('requests.get')
def test_get_json(self, mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"key": "value"}
    mock_get.return_value = mock_response
    
    result = get_json("http://example.com")
    
    mock_get.assert_called_once_with("http://example.com")
    self.assertEqual(result, {"key": "value"})
```

### Parameterized Testing
```python
@parameterized.expand([
    (input1, expected1),
    (input2, expected2),
    (input3, expected3),
])
def test_function(self, test_input, expected):
    result = function_to_test(test_input)
    self.assertEqual(result, expected)
```

### Mocking Properties
```python
with patch.object(MyClass, 'property_name', new_callable=PropertyMock) as mock_prop:
    mock_prop.return_value = "mocked_value"
    instance = MyClass()
    result = instance.property_name
    self.assertEqual(result, "mocked_value")
```

## Repository Information

- **GitHub repository**: `alx-backend-python`
- **Directory**: `0x03-Unittests_and_integration_tests`
- **Files**: `test_utils.py`, `test_client.py`, `README.md`

## Author

This project is part of the ALX Backend Python curriculum, focusing on advanced testing techniques and best practices in Python development.