from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.db.session import engine, Base 
from app.api.routes import auth , meals, insights
import logging

# Setup logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)

# TODO
# Import routers 
# from app.api.routes import auth, meals, insights, chat, health 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import models so Base knows about all tables
    from app.models import user, meal
    
    # Startup - create tables if they dont exist 

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database connected")
    yield
    # Shutdown 
    await engine.dispose()
    print("Database disconnected")


# Creating FastAPI app 
app = FastAPI(
    title="MakanAI",
    description="AI-powered mindful eating journey",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - allows React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", # React dev server
        "http://localhost:5173"  # Vite dev server 
    ],
    allow_credentials=True,  # allow cookies / auth headers to be sent
    allow_methods=["*"],  # allow GET, POST, PUT, DELETE etc.. 
    allow_headers=["*"],  # Alows any custom header 
)

# TODO
# Routers - uncomment once build 
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(meals.router, prefix="/api/meals", tags=["Meals"])
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
# app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Health Check 
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status" : "ok",
        "app" : "MakanAI",
        "env" : settings.APP_ENV
    }