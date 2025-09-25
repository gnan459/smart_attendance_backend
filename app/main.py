from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, teacher, student, session
from app.core.config import settings
from app.db.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(teacher.router, prefix=settings.API_V1_STR)
app.include_router(student.router, prefix=settings.API_V1_STR)
app.include_router(session.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Smart Attendance System API with BLE Token Support", 
        "docs": f"{settings.API_V1_STR}/docs"
    }
