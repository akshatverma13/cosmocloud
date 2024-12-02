from fastapi import FastAPI, HTTPException, Body, Path
from models import StudentCreate, StudentUpdate, StudentResponse
from database import students_collection
from bson import ObjectId
from typing import List, Optional

app = FastAPI()

# Helper function to parse MongoDB ObjectId to string
def parse_object_id(obj):
    obj['id'] = str(obj['_id'])
    del obj['_id']
    return obj

# POST /students - Create a student
@app.post("/students", response_model=StudentResponse, status_code=201)
async def create_student(student: StudentCreate):
    student_dict = student.dict()
    student_dict['address'] = student.address.dict()  # Convert address to dict
    result = await students_collection.insert_one(student_dict)  # Insert into MongoDB
    student_data = {"id": str(result.inserted_id), **student_dict}
    return student_data

# GET /students - List students with optional filters
@app.get("/students", response_model=dict)
async def list_students(country: Optional[str] = None, age: Optional[int] = None):
    filter_query = {}
    if country:
        filter_query['address.country'] = country
    if age:
        filter_query['age'] = {"$gte": age}
    
    students_cursor = students_collection.find(filter_query)  # Query MongoDB
    students_data = [parse_object_id(student) for student in await students_cursor.to_list(length=100)]
    return {"data": students_data}

# GET /students/{id} - Fetch student by ID
@app.get("/students/{id}", response_model=StudentResponse)
async def get_student(id: str):
    student = await students_collection.find_one({"_id": ObjectId(id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return parse_object_id(student)

# PATCH /students/{id} - Update student details
@app.patch("/students/{id}", status_code=204)
async def update_student(id: str, student_update: StudentUpdate):
    update_data = {k: v for k, v in student_update.dict(exclude_none=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    
    result = await students_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {}

# DELETE /students/{id} - Delete student
@app.delete("/students/{id}", status_code=200)
async def delete_student(id: str):
    result = await students_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}
