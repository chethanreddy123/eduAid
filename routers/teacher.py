from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import APIRouter, Response, status, Depends, HTTPException
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.mongo_connection import MongoDBConnection
from dotenv import load_dotenv
import os
from fastapi import APIRouter, HTTPException, Query
from loguru import logger


mongo_connection_student = MongoDBConnection(sub_collection="Students")
db_student = mongo_connection_student.connect()

mongo_connection_teacher = MongoDBConnection(sub_collection="Teachers")
db_teacher = mongo_connection_teacher.connect()

router = APIRouter(
    prefix='/teacher',
    tags=['Teacher'],
)



@router.post("/add_teacher/")
def add_teacher(teacher: dict):
    try:
        teacher_dict = teacher
        teacher_dict["created_at"] = datetime.utcnow()
        teacher_dict["updated_at"] = datetime.utcnow()
        teacher_dict['students'] = []

        result = db_teacher.insert_one(teacher_dict)
        teacher_dict["_id"] = str(result.inserted_id)

        return teacher_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_teacher/{teacher_id}")
def get_teacher(teacher_id: str):
    try:
        teacher = db_teacher.find_one({"_id": ObjectId(teacher_id)})
        if teacher:
            teacher["_id"] = str(teacher["_id"])
            del teacher['students']
            return teacher
        else:
            raise HTTPException(status_code=404, detail="Teacher not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{teacher_id}/students/")
def get_students_under_teacher(teacher_id: str):
    try:
     
        teacher_query = {"_id": ObjectId(teacher_id)}
        teacher = db_teacher.find_one(teacher_query)
        print(teacher)
 

        if teacher == None:
            return {"message": "Teacher not found"}
        
   

        # Extract the list of student IDs from the teacher's document
        student_ids = teacher.get("students", [])
        logger.info(f"Teacher: {teacher}")

        
        logger.info(f"student_ids: {student_ids}")

        # Find the student documents using the list of student IDs
        students_query = {"_id": {"$in": student_ids}}
        logger.info(f"students_query: {students_query}")

        students = db_student.find(students_query)

        final_students = []

        logger.info(f"students: {students}")


        for student in students:
            student["_id"] = str(student["_id"])
            del student['study_plan']
            final_students.append(student)

        logger.info(f"students: {final_students}")
        return final_students
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/get_latest_teacher/")
def get_latest_teacher():
    try:
        teacher = db_teacher.find_one(sort=[("created_at", -1)])
        if teacher:
            teacher["_id"] = str(teacher["_id"])
            return teacher
        else:
            raise HTTPException(status_code=404, detail="Teacher not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))