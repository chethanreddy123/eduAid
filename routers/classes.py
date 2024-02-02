from datetime import datetime
from fastapi import APIRouter, HTTPException
from database.mongo_connection import MongoDBConnection
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

# Assuming MongoDBConnection is modified to accept sub-collection during initialization
mongo_connection_student = MongoDBConnection(sub_collection="Students")
db_student = mongo_connection_student.connect()

mongo_connection_teacher = MongoDBConnection(sub_collection="Teachers")
db_teacher = mongo_connection_teacher.connect()


mongo_connection_classes = MongoDBConnection(sub_collection="Classes")
db_classes = mongo_connection_classes.connect()

router = APIRouter(
    prefix='/classes',
    tags=['Classes'],
)


@router.post("/add_class/")
def add_class(class_data: dict):
    try:
        class_dict = class_data
        class_dict["created_at"] = datetime.utcnow()
        class_dict["updated_at"] = datetime.utcnow()
        class_dict['study_plan'] = {}

        result = db_classes.insert_one(class_dict)
        class_dict["_id"] = str(result.inserted_id)

        return class_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/get_classes/{student_id}")
def get_class(student_id: str):
    try:
        class_curr = db_classes.find({"student_id": student_id})
        if class_curr:
            final_result = []
            for i in class_curr:
                logger.info(i)
                i["_id"] = str(i["_id"])
                final_result.append(i)
            return final_result
        else:
            raise HTTPException(status_code=404, detail="Class not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    