from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["PawfectCare"]

admin = {
    "username": "admin",
    "password": "admin123",
    "security_question": "What is your favourite pet's name?",
    "security_answer": "Bruno"
}

db["admins"].insert_one(admin)

print("Admin account created successfully!")