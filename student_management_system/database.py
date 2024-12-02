import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

MONGO_URI = os.getenv("MONGO_URI")

# MongoDB Atlas connection using Motor (asynchronous)
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("student_management")
students_collection = db.get_collection("students")
