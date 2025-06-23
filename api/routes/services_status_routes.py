from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(
    prefix="/services",
    tags=["services"]
)

STATUS_API_URL = "http://services-manager:9000"  # Nome do serviço docker-compose

@router.get("/status")
def get_all_services_status():
    try:
        resp = requests.get(f"{STATUS_API_URL}/status")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch services status: {str(e)}")

@router.get("/status/{service_name}")
def get_service_status(service_name: str):
    try:
        resp = requests.get(f"{STATUS_API_URL}/status/{service_name}")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Service not found")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch service status: {str(e)}") 