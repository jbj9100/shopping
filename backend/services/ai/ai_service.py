import google.generativeai as genai
from .config import get_settings

settings = get_settings()

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp') 
            except Exception as e:
                print(f"Failed to configure Gemini: {e}")
                self.model = None
        else:
            print("GEMINI_API_KEY not found in settings.")
            self.model = None

    async def generate_product_description(self, product_name: str, category: str) -> str:
        if not self.model:
            return "AI Service is not configured (Missing API Key)."
        
        prompt = f"""
        Act as a professional e-commerce copywriter.
        Write a compelling and SEO-friendly product description for the following item:
        Product Name: {product_name}
        Category: {category}
        
        The description should be attractive to customers and highlight potential benefits.
        Output in Korean.
        """
        
        try:
            # generate_content_async is the correct async method
            response = await self.model.generate_content_async(prompt)
            if response.text:
                return response.text
            else:
                return "Failed to generate description (No text returned)."
        except Exception as e:
            print(f"Error generating content: {e}")
            return f"Error occurred during generation: {str(e)}"

ai_service = AIService()
