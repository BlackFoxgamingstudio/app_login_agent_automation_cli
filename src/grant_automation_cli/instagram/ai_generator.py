"""
Instagram AI Generator

DEVELOPER GUIDELINE: LLM Integration & Prompting
Handles generation of captions and image prompts using the Gemini API.
Always treat LLM output as untrusted and variable. Implement thorough error 
handling for API timeouts or quota limits and provide sensible fallback values.
"""

import logging
import os

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InstagramAIGenerator:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if HAS_GEMINI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            if not HAS_GEMINI:
                logger.warning("google-generativeai package not found. Falling back to mock generator.")
            elif not self.api_key:
                logger.warning("GEMINI_API_KEY environment variable not found. Falling back to mock generator.")
            self.model = None

    def generate_caption(self, topic: str, tone: str = "luxury", hashtags: int = 5) -> str:
        """
        Generates an Instagram caption using Gemini given a topic and tone.
        """
        if not self.model:
            return f"Mock caption for '{topic}' in a {tone} tone. \n\n#seattle #culinary #mock"
            
        prompt = f"""
        Write an engaging Instagram caption for a luxury culinary tour in Seattle.
        Topic: {topic}
        Tone: {tone}
        Include exactly {hashtags} relevant hashtags at the end.
        Keep it under 100 words.
        """
        try:
            logger.info(f"Requesting caption for topic: {topic}")
            response = self.model.generate_content(prompt)
            # Remove markdown formatting like bolding occasionally output by Gemini
            text = response.text.replace('**', '')
            return text.strip()
        except RuntimeError as e:
            logger.error(f"Error generating caption: {e}")
            return f"Failed to generate caption. Error: {e}"

    def suggest_image_prompt(self, caption: str) -> str:
        """
        Generates an image generation prompt (e.g. for Midjourney/DALL-E) based on a caption.
        """
        if not self.model:
            return "A beautiful high-resolution photo of a fancy meal in Seattle, cinematic lighting."
            
        prompt = f"""
        Based on the following Instagram caption, write a detailed image generation prompt (e.g., for DALL-E or Midjourney) to create the perfect companion image.
        The image should look like a highly professional, cinematic, food or lifestyle photography shot.
        
        Caption: "{caption}"
        
        Output ONLY the image generation prompt text, no extra conversational filler.
        """
        try:
            logger.info("Requesting image prompt generation.")
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except RuntimeError as e:
            logger.error(f"Error generating image prompt: {e}")
            return "A high quality photo of a gourmet dish."

def demo_generation():
    generator = InstagramAIGenerator()
    caption = generator.generate_caption("Behind the scenes with Sous-Chef Marcus preparing King Salmon", "exclusive")
    print(f"Generated Caption:\n{caption}\n")
    
    img_prompt = generator.suggest_image_prompt(caption)
    print(f"Suggested Image Prompt:\n{img_prompt}\n")

if __name__ == "__main__":
    demo_generation()
