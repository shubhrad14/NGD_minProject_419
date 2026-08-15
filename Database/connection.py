from pymongo import MongoClient


# MongoDB Connection
client = MongoClient(
    "mongodb://localhost:27017/"
)

# Database
db = client["PawfectCare"]


# Collections
admins = db["admins"]
pets = db["pets"]
customers = db["customers"]
appointments = db["appointments"]
services = db["services"]
products = db["products"]