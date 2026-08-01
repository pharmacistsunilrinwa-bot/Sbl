import os
import google.generativeai as genai
from dotenv import load_dotenv
from sqlalchemy.future import select
from models import ChatHistory
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

class GeminiLogicService:
    def __init__(self):
        # Support both GEMINI_KEYS (comma-separated) and GEMINI_API_KEY
        keys_str = os.getenv("GEMINI_KEYS") or os.getenv("GEMINI_API_KEY") or ""
        self.keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        self.current_key_index = 0
        self.model = None
        self.system_instruction = (
            "You are a highly logical Personal AI Assistant. "
            "You excel at pattern recognition, logical reasoning, and step-by-step problem solving. "
            "When presented with data, look for underlying trends. "
            "Always maintain a professional and efficient tone."
        )
        if self.keys:
            self._configure_genai()

    def _configure_genai(self):
        if not self.keys:
            return
            
        key = self.keys[self.current_key_index]
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=self.system_instruction
        )
        
    def rotate_key(self):
        if len(self.keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.keys)
            self._configure_genai()

    async def get_context(self, db: AsyncSession, user_id: str, limit: int = 5):
        result = await db.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.timestamp.desc())
            .limit(limit)
        )
        history = result.scalars().all()
        context = ""
        for entry in reversed(history):
            context += f"User: {entry.message}\nAssistant: {entry.response}\n"
        return context

    async def reasoned_chat(self, prompt: str, context: str = ""):
        if not self.model:
            return "Error: Gemini API key not configured."
            
        full_prompt = f"Previous conversation:\n{context}\n\nCurrent message: {prompt}" if context else prompt
        try:
            response = await self.model.generate_content_async(full_prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) and len(self.keys) > 1:
                print(f"Logic Rate Limited. Rotating...")
                self.rotate_key()
                return await self.reasoned_chat(prompt, context)
            print(f"Logic Error with key {self.current_key_index}: {e}")
            return f"Error in reasoning: {str(e)}"

gemini_logic_service = GeminiLogicService()
