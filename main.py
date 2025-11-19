import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Profile, Company, Post, Connection

app = FastAPI(title="Construction Network API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Construction Network API running"}


@app.get("/schema")
def get_schema_models():
    """Expose current Pydantic schema model names for the database viewer."""
    return {
        "models": ["profile", "company", "post", "connection"]
    }


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# Basic CRUD endpoints

@app.post("/profiles", status_code=201)
def create_profile(profile: Profile):
    inserted_id = create_document("profile", profile)
    return {"id": inserted_id}


@app.get("/profiles", response_model=List[Profile])
def list_profiles(role: Optional[str] = None, location: Optional[str] = None):
    flt = {}
    if role:
        flt["role"] = role
    if location:
        flt["location"] = location
    docs = get_documents("profile", flt, limit=100)
    # Remove Mongo _id to align with response_model
    for d in docs:
        d.pop("_id", None)
    return docs


class PostCreate(BaseModel):
    author_email: str
    content: str
    tags: Optional[List[str]] = []
    images: Optional[List[str]] = []


@app.post("/posts", status_code=201)
def create_post(post: PostCreate):
    inserted_id = create_document("post", post.model_dump())
    return {"id": inserted_id}


@app.get("/posts")
def get_posts(tag: Optional[str] = None):
    flt = {"tags": {"$in": [tag]}} if tag else {}
    docs = get_documents("post", flt, limit=100)
    for d in docs:
        d["id"] = str(d.pop("_id", ""))
    return docs


class ConnectionRequest(BaseModel):
    from_email: str
    to_email: str


@app.post("/connections/request", status_code=201)
def request_connection(req: ConnectionRequest):
    # prevent duplicate pending
    existing = get_documents("connection", {"from_email": req.from_email, "to_email": req.to_email, "status": "pending"}, limit=1)
    if existing:
        raise HTTPException(status_code=400, detail="Request already pending")
    inserted_id = create_document("connection", {**req.model_dump(), "status": "pending"})
    return {"id": inserted_id}


@app.get("/connections")
def list_connections(email: str, status: Optional[str] = None):
    flt = {"$or": [{"from_email": email}, {"to_email": email}]}
    if status:
        flt["status"] = status
    docs = get_documents("connection", flt, limit=200)
    for d in docs:
        d["id"] = str(d.pop("_id", ""))
    return docs


# Simple directory (browse profiles by role)
@app.get("/directory")
def directory(role: Optional[str] = None, q: Optional[str] = None):
    flt = {}
    if role:
        flt["role"] = role
    if q:
        flt["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"skills": {"$elemMatch": {"$regex": q, "$options": "i"}}},
            {"services": {"$elemMatch": {"$regex": q, "$options": "i"}}},
            {"company": {"$regex": q, "$options": "i"}},
        ]
    docs = get_documents("profile", flt, limit=100)
    for d in docs:
        d.pop("_id", None)
    return docs


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
