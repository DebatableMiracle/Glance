from google import genai
from google.genai import types
import requests
import os
from typing import Optional, Tuple
from enum import Enum
import imghdr
from io import BytesIO
from PIL import Image
import logging

class GeminiModel(Enum):
    """Available Gemini models"""
    GEMINI_2_FLASH = "gemini-2.0-flash-exp"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_PRO_VISION = "gemini-1.0-pro-vision"

class GeminiAPI:
    def __init__(self, api_key: Optional[str] = None, debug: bool = False):
        """Initialize Gemini API client"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY environment variable or pass it directly.")
        # Enable debug logging if requested
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            
        self.client = genai.Client(api_key=self.api_key)
        self.model = GeminiModel.GEMINI_2_FLASH.value  # Default model

    def set_model(self, model: GeminiModel) -> None:
        """Set the Gemini model to use
        
        Args:
            model: GeminiModel enum value
        """
        self.model = model.value

    def _scale_image(self, image: Image.Image, max_dimension: int = 1024) -> Image.Image:
        """Scale image while maintaining aspect ratio
        
        Args:
            image: PIL Image object
            max_dimension: Maximum width or height
            
        Returns:
            PIL Image: Scaled image
        """
        # Get current size
        width, height = image.size
        
        # Calculate scaling factor
        scale = min(max_dimension / width, max_dimension / height)
        
        # Only scale down, never up
        if scale >= 1:
            return image
            
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def _validate_image(self, image_data: bytes, scale: bool = True) -> Tuple[bytes, str]:
        """Validate image size and format
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Tuple[bytes, str]: Processed image bytes and MIME type
            
        Raises:
            ValueError: If image is invalid or too large
        """
        # Detect image format
        img_format = imghdr.what(None, image_data)
        if not img_format:
            raise ValueError("Invalid image format")
            
        # Convert MIME type
        mime_type = f"image/{img_format.lower()}"
        
        # Open image
        img = Image.open(BytesIO(image_data))
        
        # Scale down large images (recommended for screenshots)
        if scale:
            img = self._scale_image(img)
        
        # Check size and resize if still needed (Gemini's limit is 4MB)
        max_size = 4 * 1024 * 1024  # 4MB
        
        if len(image_data) > max_size:
            # Resize while maintaining aspect ratio
            factor = (max_size / len(image_data)) ** 0.5
            new_size = tuple(int(dim * factor) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            buffer = BytesIO()
            img.save(buffer, format=img_format)
            image_data = buffer.getvalue()
            
        return image_data, mime_type

    def analyze_image(self, image_data: bytes, query: str = "What is in this image?", scale: bool = True) -> str:
        """
        Analyze an image using Gemini Vision API
        
        Args:
            image_data: Raw image bytes
            query: Question to ask about the image
            
        Returns:
            str: Gemini's response about the image
        """
        try:
            # Validate and process image
            processed_image, mime_type = self._validate_image(image_data, scale=scale)
            
            # Send to Gemini
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    query,
                    types.Part.from_bytes(data=processed_image, mime_type=mime_type)
                ]
            )
            return response.text
        except ValueError as e:
            return f"Image validation error: {str(e)}"
        except genai.types.generation_types.GenerationError as e:
            return f"Gemini API error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    def analyze_image_from_url(self, image_url: str, query: str = "What is in this image?", scale: bool = True) -> str:
        """
        Analyze an image from a URL using Gemini Vision API
        
        Args:
            image_url: URL of the image to analyze
            query: Question to ask about the image
            
        Returns:
            str: Gemini's response about the image
        """
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            return self.analyze_image(response.content, query, scale=scale)
        except requests.RequestException as e:
            return f"Error fetching image: {str(e)}"
