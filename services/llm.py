import os
import google.generativeai as genai

# Load the API key from .env file
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch the API key from the environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure the generative AI library with the API key
genai.configure(api_key=GOOGLE_API_KEY)

class LLM:
    def __init__(self, model_name):
        self.model = genai.GenerativeModel(model_name)

    def generate_content(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text

