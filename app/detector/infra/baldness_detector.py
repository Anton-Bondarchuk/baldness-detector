import base64
from io import BytesIO
from PIL import Image, ImageDraw
import numpy as np
import random
from typing import Tuple, List
from app.detector.domain.models.shemas import BaldnessResult, BaldnessCategory, BaldnessArea, BaldnessRegion

class BaldnessDetector:
    """Stub for baldness detection ML model"""
    
    @staticmethod
    async def process_image(image_data: bytes) -> BaldnessResult:
        """
        Process the uploaded image and detect baldness.
        This is a stub that simulates ML processing.
        
        Args:
            image_data: Raw bytes of the uploaded image
            
        Returns:
            BaldnessResult with processed image and baldness metrics
        """
        # Open image
        img = Image.open(BytesIO(image_data))
        
        # Simulate processing time
        import asyncio
        await asyncio.sleep(1)
        
        # Generate a random baldness level (stub)
        baldness_level = round(random.uniform(0, 1), 2)
        
        # Determine baldness category based on level
        category = BaldnessDetector._get_baldness_category(baldness_level)
        
        # Create processed image with highlighted "bald" areas (stub)
        processed_img = BaldnessDetector._highlight_bald_areas(img, baldness_level)
        
        # Convert processed image to base64
        buffered = BytesIO()
        processed_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Generate baldness areas (stub)
        baldness_areas = BaldnessDetector._generate_baldness_areas(baldness_level)
        
        return BaldnessResult(
            processedImage=img_str,
            baldnessLevel=baldness_level,
            baldnessCategory=category,
            baldnessAreas=baldness_areas
        )
    
    @staticmethod
    def _get_baldness_category(level: float) -> BaldnessCategory:
        """Map baldness level to category"""
        if level < 0.1:
            return BaldnessCategory.NONE
        elif level < 0.3:
            return BaldnessCategory.SLIGHT
        elif level < 0.5:
            return BaldnessCategory.MODERATE
        elif level < 0.7:
            return BaldnessCategory.SIGNIFICANT
        elif level < 0.9:
            return BaldnessCategory.SEVERE
        else:
            return BaldnessCategory.COMPLETE
    
    @staticmethod
    def _highlight_bald_areas(img: Image.Image, baldness_level: float) -> Image.Image:
        """Add simulated highlighted bald areas to the image"""
        # Create a copy of the image
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        
        # Image dimensions
        width, height = img_copy.size
        
        # Simulate bald spots based on baldness level
        # Higher baldness level = more/larger highlighted areas
        num_spots = int(baldness_level * 10) + 1
        
        for _ in range(num_spots):
            # Random position near the top of the head
            x = random.randint(width//4, 3*width//4)
            y = random.randint(height//8, height//3)
            
            # Size based on baldness level
            size = int(baldness_level * 50) + 10
            
            # Draw a semi-transparent red circle
            draw.ellipse(
                [(x-size, y-size), (x+size, y+size)],
                outline=(255, 0, 0, 128),
                fill=(255, 0, 0, 64)
            )
        
        return img_copy
    
    @staticmethod
    def _generate_baldness_areas(baldness_level: float) -> List[BaldnessArea]:
        """Generate simulated baldness areas data"""
        areas = []
        
        # Add varying levels of baldness to different regions
        regions = list(BaldnessRegion)
        for region in regions:
            # Skip some regions randomly for lower baldness levels
            if baldness_level < 0.5 and random.random() > baldness_level*2:
                continue
                
            # Generate confidence score with some randomness but correlated to overall level
            confidence = min(1.0, max(0.1, baldness_level * random.uniform(0.8, 1.2)))
            
            # Generate pixel percentage
            pixel_pct = confidence * 100 * random.uniform(0.7, 1.0)
            
            areas.append(BaldnessArea(
                region=region,
                confidenceScore=round(confidence, 2),
                pixelPercentage=round(pixel_pct, 1)
            ))
            
        return areas