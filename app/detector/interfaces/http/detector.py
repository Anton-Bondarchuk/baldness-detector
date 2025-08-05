import base64
import json

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Request
from fastapi.responses import StreamingResponse

from app.detector.infra.baldness_detector import BaldnessDetector
from app.detector.domain.models.shemas import BaldnessResult

router = APIRouter(
    tags=["Baldness Detection"],
)

@router.post("/detect-baldness", response_model=BaldnessResult)
async def detect_baldness(
    request: Request,
    photo: UploadFile = File(...),
):
    """
    Detect baldness from uploaded photo.
    Returns processed image with highlighted bald areas and baldness level.
    """
    try:
        # Access authenticated user info
        user = request.state.user
        
        # Log the request for auditing
        print(f"Processing baldness detection for user: {user.get('email', 'unknown')}")
        
        # Validate file type
        if not photo.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Read image data
        image_data = await photo.read()
        
        # Process with baldness detector
        result = await BaldnessDetector.process_image(image_data)
        
        return result
        
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

@router.post("/detect-baldness/stream")
async def stream_baldness_detection(
    request: Request,
    photo: UploadFile = File(...),
):
    """
    Stream baldness detection results.
    Returns a stream containing the processed image and baldness level.
    """
    try:
        # Access authenticated user info
        user = request.state.user
        
        # Validate file type
        if not photo.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Read image data
        image_data = await photo.read()
        
        # Process with baldness detector
        result = await BaldnessDetector.process_image(image_data)
        
        # Create a streaming response
        async def stream_generator():
            # First, yield the metadata as JSON
            metadata = {
                "baldnessLevel": result.baldnessLevel,
                "baldnessCategory": result.baldnessCategory,
                "baldnessAreas": [area.dict() for area in result.baldnessAreas]
            }
            metadata_json = json.dumps(metadata).encode('utf-8')
            metadata_size = len(metadata_json).to_bytes(4, byteorder='big')
            
            yield metadata_size
            yield metadata_json
            
            # Then, yield the processed image
            image_bytes = base64.b64decode(result.processedImage)
            yield len(image_bytes).to_bytes(4, byteorder='big')
            yield image_bytes
        
        return StreamingResponse(
            stream_generator(),
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )