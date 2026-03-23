from fastapi import APIRouter, HTTPException
from app.database.db import db

router = APIRouter()

users_collection = db["users"]


# 🔥 SIGNUP
@router.post("/signup")
def signup(user: dict):
    existing = users_collection.find_one({"email": user["email"]})

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    users_collection.insert_one(user)

    return {"message": "User created"}


# 🔥 LOGIN
@router.post("/login")
def login(user: dict):
    existing = users_collection.find_one({
        "email": user["email"],
        "password": user["password"]
    })

    if not existing:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful"}