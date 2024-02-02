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


router = APIRouter(
    prefix='/student',
    tags=['Student'],
)



@router.post("/add_student/")
def add_student(student: dict):
    try:
        student_dict = student
        student_dict["created_at"] = datetime.utcnow()
        student_dict["updated_at"] = datetime.utcnow()
        student_dict['study_plan'] = {} 

        # Insert the student document into the students sub-collection
        result = db_student.insert_one(student_dict)
        student_dict["_id"] = str(result.inserted_id)

        # Update the corresponding teacher's document with the new student ID
        teacher_id = student_dict.get("teacher_id")  # Assuming you have a field "teacher_id" in the student document
        if teacher_id:
            teacher_query = {"_id": ObjectId(teacher_id)}
            teacher_update = {"$addToSet": {"students": result.inserted_id}}
            db_teacher.update_one(teacher_query, teacher_update)

        return student_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_student/{student_id}")
def get_student(student_id: str):
    try:
        student = db_student.find_one({"_id": ObjectId(student_id)})
        logger.info(student)
        if student:
            student["_id"] = str(student["_id"])
            del student['study_plan']
            return student
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/{student_id}/classes/")
def get_classes_of_student(student_id: str):
    try:
        # Find the student's document by ID
        student_query = {"_id": ObjectId(student_id)}
        student = db_student.find_one(student_query)

        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Extract the list of class IDs from the student's document
        class_ids = student.get("class_list", [])
        logger.info(f"Student: {student}")
        
        logger.info(f"class_ids: {class_ids}")
        return class_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))