import os
import random
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        # Support both GEMINI_KEYS (comma-separated) and GEMINI_API_KEY
        keys_str = os.getenv("GEMINI_KEYS") or os.getenv("GEMINI_API_KEY") or ""
        self.keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        self.current_key_index = 0
        self.model = None
        if self.keys:
            self._configure_genai()

    def _configure_genai(self):
        if not self.keys:
            return
        
        key = self.keys[self.current_key_index]
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def rotate_key(self):
        if len(self.keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.keys)
            self._configure_genai()

    async def generate_content(self, prompt: str):
        if not self.model:
            return "Error: Gemini API key not configured. Please set GEMINI_API_KEY in your .env file."
            
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) and len(self.keys) > 1:
                print(f"Rate limited with key {self.current_key_index}. Rotating...")
                self.rotate_key()
                return await self.generate_content(prompt)
            print(f"Gemini API Error: {e}")
            return f"Error generating content: {str(e)}"

gemini_service = GeminiService()
