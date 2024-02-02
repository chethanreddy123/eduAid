from fastapi import APIRouter, HTTPException
from services.llm import LLM
from schemas.llm_routes import LLMGenerateRequest, LLMGenerateResponse
from loguru import logger
from database.mongo_connection import MongoDBConnection
from services.llm_design import get_llm_chain_response
from services.templates import * 


router = APIRouter(
    prefix='/llm',
    tags=['LLM'],
)


@router.post('/generate/', response_model=LLMGenerateResponse)
def generate_content(request : LLMGenerateRequest):

    logger.debug(f'Generating content for model {request.model} with prompt {request.prompt}')

    llm = LLM(request.model)
    content = llm.generate_content(request.prompt)

    logger.debug("Got the response from the model")

    return LLMGenerateResponse(content=content)


@router.post("/generate_summary_class/")
def generate_summary_class(class_id: str):
    try:
        
       pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



