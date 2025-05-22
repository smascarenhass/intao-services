# Intao Services API

This is a FastAPI-based REST API for Intao Services.

## Project Structure

```
.
├── api/
│   ├── main.py
│   ├── Dockerfile
│   ├── models/
│   │   ├── base.py
│   │   └── user.py
│   └── routes/
│       └── user_routes.py
├── services/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API:
```bash
uvicorn api.main:app --reload
```

### Docker Setup

1. Build and start the containers:
```bash
docker-compose up --build
```

2. To run in detached mode:
```bash
docker-compose up -d
```

3. To stop the containers:
```bash
docker-compose down
```

The API will be available at http://localhost:8003

API documentation will be available at:
- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

## Data Storage

The project uses Redis for data storage, connecting to the external Redis instance at:
- Host: database.intao.app
- Port: 6379 