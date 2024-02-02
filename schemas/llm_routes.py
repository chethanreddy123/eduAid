from pydantic import BaseModel

class LLMGenerateRequest(BaseModel):
    prompt : str
    model : str

class LLMGenerateResponse(BaseModel):
    content : str

