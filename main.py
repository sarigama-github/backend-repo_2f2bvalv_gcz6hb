import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

app = FastAPI(title="Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

# ---- Portfolio API ----
try:
    from database import create_document, db
    from schemas import ContactMessage
except Exception:
    create_document = None
    db = None
    ContactMessage = None

@app.get("/api/projects")
def list_projects():
    """Return a curated list of portfolio projects (static sample data)."""
    projects = [
        {
            "id": "p1",
            "title": "Interactive Data Dashboard",
            "description": "A responsive dashboard with real-time charts and dark mode.",
            "tags": ["React", "Tailwind", "Charts"],
            "link": "https://example.com/dashboard",
            "github": "https://github.com/example/dashboard",
            "image": "https://images.unsplash.com/photo-1556157382-97eda2d62296?q=80&w=1200&auto=format&fit=crop"
        },
        {
            "id": "p2",
            "title": "Creative Portfolio Site",
            "description": "Smooth scroll sections, parallax hero, and animated cards.",
            "tags": ["React", "UX", "Animation"],
            "link": "https://example.com/portfolio",
            "github": "https://github.com/example/portfolio",
            "image": "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1200&auto=format&fit=crop"
        },
        {
            "id": "p3",
            "title": "API Microservice Boilerplate",
            "description": "Production-ready FastAPI service with auth and testing.",
            "tags": ["FastAPI", "Python", "DevOps"],
            "link": "https://example.com/api",
            "github": "https://github.com/example/fastapi",
            "image": "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1200&auto=format&fit=crop"
        }
    ]
    return {"projects": projects}

@app.post("/api/contact")
def submit_contact(payload: dict):
    """Accept contact form submissions and store them in MongoDB."""
    if ContactMessage is None or create_document is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    try:
        data = ContactMessage(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    # add received_at timestamp
    data.received_at = datetime.now(timezone.utc)

    try:
        inserted_id = create_document("contactmessage", data)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db as _db
        
        if _db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = _db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
