import os
import google.generativeai as genai

# Load the API key from .env file
from dotenv import load_dotenv

import PIL.Image


# Load environment variables from .env
load_dotenv()

# Fetch the API key from the environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure the generative AI library with the API key
genai.configure(api_key=GOOGLE_API_KEY)

class LLM:
    def __init__(self, model_name = "gemini-pro"):
        self.model = genai.GenerativeModel(model_name)
        self.image_model = genai.GenerativeModel('gemini-pro-vision')

    def generate_content(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text
    
    def analyze_image(self, image):
        user_input_text = "Give short description of the image"
        response = self.image_model.generate_content([user_input_text, image], stream=True)
        return response.text
    
    def get_image_model(self):
        return self.image_model

