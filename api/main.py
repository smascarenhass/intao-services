from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import teams_routes, membership_pro_routes, email_routes, sparks_app_routes

app = FastAPI(
    title="Intao Services API",
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
app.include_router(membership_pro_routes.router)
app.include_router(email_routes.router)
app.include_router(sparks_app_routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Intao API"} 