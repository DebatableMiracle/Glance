import base64
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Optional, Literal
from .geminiapi import GeminiAPI

class ApiWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, api_endpoint, api_key, image_path, prompt, model_provider: Literal['openai', 'gemini'] = 'openai'):
        super().__init__()
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.image_path = image_path
        self.prompt = prompt
        self.model_provider = model_provider
        
        # Initialize Gemini API if selected
        self.gemini = None
        if model_provider == 'gemini':
            self.gemini = GeminiAPI(api_key)

    def run(self):
        try:
            # Read image data
            try:
                with open(self.image_path, "rb") as f:
                    image_data = f.read()
            except IOError as e:
                self.error.emit(f"Failed to read screenshot: {str(e)}")
                return

            if self.model_provider == 'gemini':
                try:
                    # Use Gemini API
                    response_text = self.gemini.analyze_image(image_data, self.prompt)
                    response_data = {
                        'choices': [{
                            'message': {
                                'content': response_text
                            }
                        }]
                    }
                    self.finished.emit(response_data)
                except Exception as e:
                    self.error.emit(f"Gemini API error: {str(e)}")
                    return
            else:
                # Validate OpenAI endpoint
                if not self.api_endpoint or not self.api_endpoint.startswith('http'):
                    self.error.emit("Invalid OpenAI API endpoint")
                    return

                # Use OpenAI API
                try:
                    # Detect image format
                    import imghdr
                    img_format = imghdr.what(None, image_data) or 'png'
                    base64_image = base64.b64encode(image_data).decode("utf-8")
                    
                    payload = {
                        "model": "gpt-4-vision-preview",
                        "messages": [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": self.prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/{img_format};base64,{base64_image}"}}
                            ]
                        }],
                        "max_tokens": 300
                    }

                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }

                    # Make request with timeout
                    response = requests.post(self.api_endpoint, headers=headers, json=payload, timeout=30)
                    response.raise_for_status()
                    self.finished.emit(response.json())
                except requests.Timeout:
                    self.error.emit("Request timed out. Please try again.")
                except requests.RequestException as e:
                    self.error.emit(f"API request failed: {str(e)}")
                except Exception as e:
                    self.error.emit(f"Unexpected error: {str(e)}")

        except Exception as e:
            self.error.emit(f"Unexpected error: {str(e)}")
