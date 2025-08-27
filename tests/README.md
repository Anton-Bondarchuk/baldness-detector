# Baldness Detector Tests

This directory contains comprehensive tests for the baldness detector API, including both the authentication system and the detector endpoints.

## Test Structure

### 1. Integration Tests
These tests require a running server and test the complete API flow:

- **`test_auth_api.py`** - Tests authentication endpoints (`/api/v1/auth/*`)
- **`test_detector_api.py`** - Tests detector endpoints (`/detect-baldness`, `/detect-baldness/stream`)

### 2. Unit Tests
These tests mock dependencies and test individual components in isolation:

- **`test_detector_unit.py`** - Unit tests for detector router logic using pytest

## Quick Start

### Option 1: Use the Test Runner (Recommended)
```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run all tests (requires server to be running for integration tests)
python tests/run_tests.py

# Run only unit tests (no server required)
python tests/run_tests.py --unit

# Run only integration tests (requires server)
python tests/run_tests.py --integration
```

### Option 2: Run Tests Individually

#### Integration Tests (Require Running Server)
1. Start the server:
   ```bash
   python -m app
   ```

2. In another terminal, run integration tests:
   ```bash
   # Test authentication
   python tests/test_auth_api.py
   
   # Test detector endpoints
   python tests/test_detector_api.py
   ```

#### Unit Tests (No Server Required)
```bash
# Install test dependencies if not already installed
pip install -r test-requirements.txt

# Run unit tests with pytest
pytest tests/test_detector_unit.py -v
```

## Test Coverage

### Authentication Tests (`test_auth_api.py`)
- ✅ Health check endpoint
- ✅ Email authentication
- ✅ Protected endpoint access with JWT
- ✅ Error handling

### Detector Integration Tests (`test_detector_api.py`)
- ✅ `/detect-baldness` endpoint success case
- ✅ `/detect-baldness` without authentication (401)
- ✅ `/detect-baldness` with invalid file type (400)
- ✅ `/detect-baldness` with missing file (422)
- ✅ `/detect-baldness/stream` endpoint success case
- ✅ `/detect-baldness/stream` without authentication (401)
- ✅ Different image formats support
- ✅ Large image processing

### Detector Unit Tests (`test_detector_unit.py`)
- ✅ Router endpoint logic (mocked)
- ✅ File upload validation
- ✅ Error handling and HTTP status codes
- ✅ Response schema validation
- ✅ Content type validation
- ✅ BaldnessDetector integration
- ✅ Concurrent request handling

## Test Data

The tests use minimal PNG images created programmatically:
- **1x1 pixel PNG** for basic testing (doesn't require PIL/Pillow)
- **Base64 encoded images** for consistent test data
- **Various content types** to test validation

## Dependencies

### Required for Integration Tests:
- `httpx` - HTTP client for API calls
- Running baldness detector server on `localhost:8000`

### Required for Unit Tests:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pillow` - Image processing (optional, fallback provided)

### Install All Dependencies:
```bash
pip install -r test-requirements.txt
```

## Environment Setup

1. **Database**: Tests require the database to be set up for authentication
2. **Environment Variables**: Ensure `.env` file is properly configured
3. **Server**: Integration tests require the server to be running

## Running in CI/CD

For automated testing in CI/CD pipelines:

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r test-requirements.txt

# Run unit tests (no server required)
pytest tests/test_detector_unit.py -v

# For integration tests, start server in background
python -m app &
sleep 10  # Wait for server to start

# Run integration tests
python tests/test_auth_api.py
python tests/test_detector_api.py

# Kill background server
pkill -f "python -m app"
```

## Expected Output

### Successful Test Run:
```
✅ Health Check - PASS
✅ Email Authentication - PASS
✅ Protected Endpoint - PASS
✅ Detect Baldness Success - PASS
✅ Detect Baldness No Auth - PASS
✅ Stream Detection Success - PASS
... (more tests)

Total: 15/15 tests passed
🎉 All tests passed!
```

### Test Failure Example:
```
❌ Detect Baldness Success - FAIL
Error: Server returned 500: Processing error

Total: 14/15 tests passed
⚠️ 1 test(s) failed
```

## Troubleshooting

### Common Issues:

1. **Server not running**: 
   ```
   ❌ Server is not running on localhost:8000
   ```
   **Solution**: Start the server with `python -m app`

2. **Authentication failures**:
   ```
   ❌ Failed to get auth token
   ```
   **Solution**: Check database connection and environment variables

3. **Import errors**:
   ```
   ModuleNotFoundError: No module named 'pytest'
   ```
   **Solution**: Install test dependencies with `pip install -r test-requirements.txt`

4. **Database connection errors**:
   **Solution**: Ensure PostgreSQL is running and environment variables are set

## Adding New Tests

### For Integration Tests:
1. Add test functions to `test_detector_api.py` or `test_auth_api.py`
2. Use `async def` for async test functions
3. Follow the existing pattern for authentication and assertions

### For Unit Tests:
1. Add test classes/methods to `test_detector_unit.py`
2. Use pytest fixtures for common setup
3. Mock external dependencies with `@patch`
4. Follow pytest conventions

Example:
```python
@pytest.mark.asyncio
@patch('app.detector.interfaces.http.detector.BaldnessDetector.process_image')
async def test_new_feature(mock_process_image, client, sample_data):
    # Test implementation
    pass
```
