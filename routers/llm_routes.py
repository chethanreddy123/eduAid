from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from services.llm import LLM
from schemas.llm_routes import LLMGenerateRequest, LLMGenerateResponse
from loguru import logger
from database.mongo_connection import MongoDBConnection
from services.llm_design import get_llm_chain_response
from services.templates import * 
from bson.objectid import ObjectId
import os
import PIL.Image
import io
import json

router = APIRouter(
    prefix='/llm',
    tags=['LLM'],
)

mongo_connection_student = MongoDBConnection(sub_collection="Students")
db_student = mongo_connection_student.connect()

mongo_connection_teacher = MongoDBConnection(sub_collection="Teachers")
db_teacher = mongo_connection_teacher.connect()

mongo_connection_classes = MongoDBConnection(sub_collection="Classes")
db_classes = mongo_connection_classes.connect()



@router.post('/generate/', response_model=LLMGenerateResponse)
def generate_content(request : LLMGenerateRequest):

    logger.debug(f'Generating content for model {request.model} with prompt {request.prompt}')

    llm = LLM(request.model)
    content = llm.generate_content(request.prompt)

    logger.debug("Got the response from the model")

    return LLMGenerateResponse(content=content)


from fastapi import HTTPException, UploadFile, File

@router.post("/generate_study_plan/{student_id}")
async def generate_summary_class(student_id: str, transcript: UploadFile = File(...)):
    try:
        student = db_student.find_one({"_id": ObjectId(student_id)})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        save_path = os.path.join("uploads", "sample.txt")  # Adjust the save path as needed
        with open(save_path, "wb") as file:
            file.write(await transcript.read())

        output_format = "class_plan"
        teacher_name = "Jack"
        school_name = "ABC School"
        prompt_template = CLASS_PLAN_PROMPT
        prompt_output_template = CLASS_PLAN_PROMPT_OUTPUT

        final_result = get_llm_chain_response("uploads/sample.txt" ,
                                              output_format, teacher_name, school_name,
                                              prompt_template, prompt_output_template)

        # Assuming there's a field named 'study_plan' in the student document
        study_plan = student.get("study_plan", {})
        study_plan["description"] = final_result

        # Update the student document with the new study plan description
        db_student.update_one({"_id": ObjectId(student_id)},
                              {"$set": {"study_plan": study_plan}})

        return {"message": "Study plan description added successfully",
                "study_plan": study_plan}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/generate_class_insights/{class_id}")
async def generate_class_insights(class_id: str, transcript: UploadFile = File(...)):
    try:
        current_class = db_classes.find_one({"_id": ObjectId(class_id)})
        if not current_class:
            return {"message": "Class not found"}
        
        if current_class.get("class_insights") != {}:
            return {"message": "Class insights already exists",
                    "class_insights": current_class.get("class_insights")}


        save_path = os.path.join("uploads", "sample.txt")  # Adjust the save path as needed
        with open(save_path, "wb") as file:
            file.write(await transcript.read())

        class_insights = current_class.get("class_insights", {})

        summary = get_llm_chain_response("uploads/sample.txt" ,
                                              'long', "Chethan", "Edvi",
                                              CLASS_SUMMARY_SHORT_PROMPT, CLASS_SUMMARY_SHORT_PROMPT_OUTPUT)
        
        objective = get_llm_chain_response("uploads/sample.txt" ,
                                              'bullet_points', "Chethan", "Edvi",
                                              OBJECTIVE_PROMPT, OBJECTIVE_PROMPT_OUTPUT)
        
        concepts_taught = get_llm_chain_response("uploads/sample.txt" ,
                                              'bullet_points', "Chethan", "Edvi",
                                              CONCEPTS_TAUGHT_PROMPT, CONCEPTS_TAUGHT_PROMPT_OUTPUT)
        
        student_understanding_level = get_llm_chain_response("uploads/sample.txt" ,
                                              'one_sentence', "Chethan", "Edvi",
                                              STUDENT_UNDERSTANDING_LEVEL_PROMPT, STUDENT_UNDERSTANDING_LEVEL_PROMPT_OUTPUT)
        
        gaps_identified = get_llm_chain_response("uploads/sample.txt" ,
                                              'bullet_points', "Chethan", "Edvi",
                                              GAPS_IDENTIFIED_PROMPT, GAPS_IDENTIFIED_PROMPT_OUTPUT)
        
        teacher_imporvement_suggestions = get_llm_chain_response("uploads/sample.txt" ,
                                                'short', "Chethan", "Edvi",
                                                TEACHER_IMPROVEMENT_SUGGESTIONS_PROMPT, TEACHER_IMPROVEMENT_SUGGESTIONS_PROMPT_OUTPUT)
        

        # Assuming there's a field named 'class_insights' in the student document:
        class_insights["summary"] = summary
        class_insights["objective"] = objective
        class_insights['concepts_taught'] = concepts_taught
        class_insights['student_understanding_level'] = student_understanding_level
        class_insights['gaps_identified'] = gaps_identified
        class_insights['teacher_imporvement_suggestions'] = teacher_imporvement_suggestions

        

        # Update the student document with the new class insights description
        db_classes.update_one({"_id": ObjectId(class_id)},
                              {"$set": {"class_insights": class_insights}})

        return {"message": "Class insights description added successfully",
                "class_insights": class_insights}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/analyze_image_notes/")
async def image_analysis(file: UploadFile = File(...), text: str = Form(...)):

    print("Image analysis request received")
    # Read image file
    image_content = await file.read()
    image = PIL.Image.open(io.BytesIO(image_content))

    # Process with Google Gemini Vision Pro
    llm = LLM()

    model_image = llm.get_image_model()

    response = model_image.generate_content([text, image])
    response.resolve()

    return {
        "response" : str(response.text)
    }


@router.post("/generate_study_plan_json/{student_id}")
async def generate_study_plan_json(student_id: str, transcript: UploadFile = File(...)):
    try:
        student_curr = db_student.find_one({"_id": ObjectId(student_id)})

        if not student_curr:
            return {"message": "Student not found"}
        
        study_plan = student_curr.get("study_plan", {})
        if study_plan != []:
            return {"message": "Study plan already exists",
                    "study_plan": study_plan}

        save_path = os.path.join("uploads", "sample.txt")  # Adjust the save path as needed
        with open(save_path, "wb") as file:
            file.write(await transcript.read())

        output_format = "class_json"
        teacher_name = "Jack"
        school_name = "ABC School"
        prompt_template = STUDY_PLAN_PROMPT
        prompt_output_template = STUDY_PLAN_PROMPT_OUTPUT


        max_retries = 5
        current_retry = 0
        result = None

        while current_retry < max_retries:
            try:
                # Replace with your actual function call
                result = get_llm_chain_response("uploads/sample.txt",
                                            output_format, teacher_name, school_name,
                                            prompt_template, prompt_output_template)
                logger.info(f"Result: {result}")
                result = result.replace('`', "").replace("json", "").strip()
                logger.info(f"Result Cleaned: {result}")
                result = json.loads(result)
                break  # If successful, exit the loop
            except Exception as e:
                print(f"Error fetching response: {e}")
                current_retry += 1
                print(f"Retrying... Attempt {current_retry}")



        # Assuming there's a field named 'study_plan' in the student document
    
        study_plan = result['study_plan']

        
        db_student.update_one({"_id": ObjectId(student_id)},
                              {"$set": {"study_plan": study_plan}})

        return {"message": "Study plan description added successfully",
                "study_plan": study_plan}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
