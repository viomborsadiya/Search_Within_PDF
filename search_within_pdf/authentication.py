import pymongo
from pymongo import MongoClient
import bcrypt

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['search_within_pdf']
users_collection = db['users']

def create_user(email, password, name, surname):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({
        "email": email,
        "password": hashed_password,
        "name": name,
        "surname": surname
    })

def verify_user(email, password):
    user = users_collection.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return True
    return False

def get_user_password(email):
    user = users_collection.find_one({"email": email})
    if user:
        return user['password'].decode('utf-8')  # Return the decoded password
    return None

def update_user_password(email, new_password):
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    users_collection.update_one(
        {"email": email},
        {"$set": {"password": hashed_password}}
    )
