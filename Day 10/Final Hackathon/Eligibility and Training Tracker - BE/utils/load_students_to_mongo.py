# utils/load_students_to_mongo.py
import json
from pymongo import MongoClient

def load_students():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["eligibility_tracker"]
    students_col = db["students"]

    # Clear existing student data (optional for dev)
    students_col.delete_many({})

    # Load from local JSON
    with open("sample_student_profiles.json", "r") as f:
        students = json.load(f)

    students_col.insert_many(students)
    print("✅ Inserted student profiles into MongoDB")

if __name__ == "__main__":
    load_students()
