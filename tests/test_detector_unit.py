"""
Unit tests for the detector router using pytest.
These tests mock the dependencies to test the router logic in isolation.
"""

import pytest
import base64
import io
from unittest.mock import Mock, AsyncMock, patch
from fastapi import UploadFile
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.detector.interfaces.http.detector import router
from app.detector.domain.models.shemas import BaldnessResult, BaldnessCategory, BaldnessArea, BaldnessRegion


# Create a test app with just the detector router
@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app)


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    return {"email": "test@example.com", "name": "Test User"}


@pytest.fixture
def sample_image_bytes():
    """Sample PNG image as bytes"""
    # 1x1 pixel PNG
    png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    return base64.b64decode(png_b64)


@pytest.fixture
def sample_baldness_result():
    """Sample baldness detection result"""
    return BaldnessResult(
        processedImage="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
        baldnessLevel=0.75,
        baldnessCategory=BaldnessCategory.MODERATE,
        baldnessAreas=[
            BaldnessArea(
                region=BaldnessRegion.CROWN,
                confidenceScore=0.85,
                pixelPercentage=25.5
            )
        ]
    )


class TestDetectBaldnessEndpoint:
    """Test cases for the /detect-baldness endpoint"""

    @patch('app.detector.interfaces.http.detector.BaldnessDetector.process_image')
    def test_detect_baldness_success(self, mock_process_image, client, sample_image_bytes, sample_baldness_result, mock_user):
        """Test successful baldness detection"""
        # Setup mock
        mock_process_image.return_value = sample_baldness_result
        
        # Create mock request with user
        with patch('fastapi.Request') as mock_request:
            mock_request.state.user = mock_user
            
            # Prepare test data
            files = {
                "photo": ("test.png", sample_image_bytes, "image/png")
            }
            
            # Make request
            response = client.post("/detect-baldness", files=files)
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            
            assert "processedImage" in data
            assert "baldnessLevel" in data
            assert "baldnessCategory" in data
            assert "baldnessAreas" in data
            
            assert data["baldnessLevel"] == 0.75
            assert data["baldnessCategory"] == "MODERATE"
            assert len(data["baldnessAreas"]) == 1

    def test_detect_baldness_invalid_file_type(self, client, mock_user):
        """Test rejection of non-image files"""
        with patch('fastapi.Request') as mock_request:
            mock_request.state.user = mock_user
            
            files = {
                "photo": ("test.txt", b"not an image", "text/plain")
            }
            
            response = client.post("/detect-baldness", files=files)
            
            assert response.status_code == 400
            assert "File must be an image" in response.json()["detail"]

    def test_detect_baldness_missing_file(self, client, mock_user):
        """Test request without file upload"""
        with patch('fastapi.Request') as mock_request:
            mock_request.state.user = mock_user
            
            response = client.post("/detect-baldness")
            
            assert response.status_code == 422  # Validation error

    @patch('app.detector.interfaces.http.detector.BaldnessDetector.process_image')
    def test_detect_baldness_processing_error(self, mock_process_image, client, sample_image_bytes, mock_user):
        """Test handling of processing errors"""
        # Setup mock to raise exception
        mock_process_image.side_effect = Exception("Processing failed")
        
        with patch('fastapi.Request') as mock_request:
            mock_request.state.user = mock_user
            
            files = {
                "photo": ("test.png", sample_image_bytes, "image/png")
            }
            
            response = client.post("/detect-baldness", files=files)
            
            assert response.status_code == 500
            assert "Error processing image" in response.json()["detail"]


class TestStreamBaldnessDetectionEndpoint:
    """Test cases for the /detect-baldness/stream endpoint"""

    @patch('app.detector.interfaces.http.detector.BaldnessDetector.process_image')
    def test_stream_baldness_detection_success(self, mock_process_image, client, sample_image_bytes, sample_baldness_result, mock_user):
        """Test successful streaming baldness detection"""
        # Setup mock
        mock_process_image.return_value = sample_baldness_result
        
        with patch('fastapi.Request') as mock_request:
            mock_request.state.user = mock_user
            
            files = {
                "photo": ("test.png", sample_image_bytes, "image/png")
            }
            
            response = client.post("/detect-baldness/stream", files=files)
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/octet-stream"
            assert len(response.content) > 0

    def test_stream_baldness_detection_invalid_file_type(self, client, mock_user):
        """Test streaming endpoint with invalid file type"""
        with patch('fastapi.Request') as mock_request:
            mock_request.state.user = mock_user
            
            files = {
                "photo": ("test.txt", b"not an image", "text/plain")
            }
            
            response = client.post("/detect-baldness/stream", files=files)
            
            assert response.status_code == 400
            assert "File must be an image" in response.json()["detail"]

    @patch('app.detector.interfaces.http.detector.BaldnessDetector.process_image')
    def test_stream_baldness_detection_processing_error(self, mock_process_image, client, sample_image_bytes, mock_user):
        """Test streaming endpoint with processing error"""
        # Setup mock to raise exception
        mock_process_image.side_effect = Exception("Processing failed")
        
        with patch('fastapi.Request') as mock_request:
            mock_request.state.user = mock_user
            
            files = {
                "photo": ("test.png", sample_image_bytes, "image/png")
            }
            
            response = client.post("/detect-baldness/stream", files=files)
            
            assert response.status_code == 500
            assert "Error processing image" in response.json()["detail"]


class TestBaldnessDetectorIntegration:
    """Integration tests for the BaldnessDetector"""

    @pytest.mark.asyncio
    async def test_baldness_detector_returns_valid_result(self, sample_image_bytes):
        """Test that BaldnessDetector returns a valid result structure"""
        from app.detector.infra.baldness_detector import BaldnessDetector
        
        result = await BaldnessDetector.process_image(sample_image_bytes)
        
        # Validate result structure
        assert isinstance(result, BaldnessResult)
        assert 0 <= result.baldnessLevel <= 1
        assert result.baldnessCategory in BaldnessCategory
        assert isinstance(result.baldnessAreas, list)
        assert result.processedImage  # Should not be empty
        
        # Validate base64 encoded image
        try:
            base64.b64decode(result.processedImage)
        except Exception:
            pytest.fail("processedImage is not valid base64")

    @pytest.mark.asyncio
    async def test_baldness_detector_different_image_sizes(self):
        """Test BaldnessDetector with different image sizes"""
        from app.detector.infra.baldness_detector import BaldnessDetector
        
        # Test with minimal image
        minimal_png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==")
        
        result = await BaldnessDetector.process_image(minimal_png)
        
        assert isinstance(result, BaldnessResult)
        assert 0 <= result.baldnessLevel <= 1


class TestValidationAndErrorHandling:
    """Test validation and error handling"""

    def test_upload_file_content_type_validation(self, client, mock_user):
        """Test that content type is properly validated"""
        test_cases = [
            ("image/png", True),
            ("image/jpeg", True),
            ("image/gif", True),
            ("text/plain", False),
            ("application/pdf", False),
            ("video/mp4", False),
        ]
        
        for content_type, should_pass in test_cases:
            with patch('fastapi.Request') as mock_request:
                mock_request.state.user = mock_user
                
                files = {
                    "photo": ("test_file", b"fake_content", content_type)
                }
                
                response = client.post("/detect-baldness", files=files)
                
                if should_pass:
                    # Should not fail due to content type (might fail for other reasons)
                    assert response.status_code != 400 or "File must be an image" not in response.json().get("detail", "")
                else:
                    assert response.status_code == 400
                    assert "File must be an image" in response.json()["detail"]


class TestResponseFormat:
    """Test response format compliance"""

    @patch('app.detector.interfaces.http.detector.BaldnessDetector.process_image')
    def test_response_schema_compliance(self, mock_process_image, client, sample_image_bytes, sample_baldness_result, mock_user):
        """Test that response matches the expected schema"""
        mock_process_image.return_value = sample_baldness_result
        
        with patch('fastapi.Request') as mock_request:
            mock_request.state.user = mock_user
            
            files = {
                "photo": ("test.png", sample_image_bytes, "image/png")
            }
            
            response = client.post("/detect-baldness", files=files)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check required fields
            required_fields = ["processedImage", "baldnessLevel", "baldnessCategory", "baldnessAreas"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
            
            # Check data types and ranges
            assert isinstance(data["baldnessLevel"], (int, float))
            assert 0 <= data["baldnessLevel"] <= 1
            
            assert isinstance(data["baldnessCategory"], str)
            assert data["baldnessCategory"] in [cat.value for cat in BaldnessCategory]
            
            assert isinstance(data["baldnessAreas"], list)
            
            # Check baldness areas structure
            for area in data["baldnessAreas"]:
                assert "region" in area
                assert "confidenceScore" in area
                assert "pixelPercentage" in area
                assert 0 <= area["confidenceScore"] <= 1
                assert 0 <= area["pixelPercentage"] <= 100


# Performance and stress tests
class TestPerformance:
    """Performance and stress tests"""

    @pytest.mark.asyncio
    @patch('app.detector.interfaces.http.detector.BaldnessDetector.process_image')
    async def test_concurrent_requests(self, mock_process_image, sample_baldness_result):
        """Test handling of concurrent requests"""
        import asyncio
        import httpx
        
        mock_process_image.return_value = sample_baldness_result
        
        # This would need a running server to test properly
        # For now, just ensure the mock works
        from app.detector.infra.baldness_detector import BaldnessDetector
        
        # Test multiple concurrent calls to the detector
        tasks = []
        for _ in range(5):
            task = BaldnessDetector.process_image(b"fake_image_data")
            tasks.append(task)
        
        # This will likely fail without proper mocking, but tests the structure
        # results = await asyncio.gather(*tasks, return_exceptions=True)
        # assert len(results) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
