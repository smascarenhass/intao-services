from fastapi import FastAPI, HTTPException
from routines.service_manager import ServiceManager
import uvicorn

app = FastAPI()

# ATENÇÃO: Certifique-se de usar a mesma instância do ServiceManager usada em run_services.py
# Aqui, para exemplo, criamos uma nova. No deploy real, compartilhe a instância!
manager = ServiceManager()

@app.get("/status")
def status():
    return manager.get_service_status()

@app.get("/status/{service_name}")
def status_service(service_name: str):
    status = manager.get_service_status(service_name)
    if not status:
        raise HTTPException(status_code=404, detail="Service not found")
    return status

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000) 