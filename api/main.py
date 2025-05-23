from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import teams_routes

app = FastAPI(
    title="Intao API",
    description="REST API for Intao Services",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(teams_routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Intao API"} 