# Intao Services API

This is a FastAPI-based REST API for Intao Services.

## Project Structure

```
.
├── api/
│   ├── main.py
│   ├── models/
│   │   ├── base.py
│   │   └── user.py
│   └── routes/
│   │   └── user_routes.py
│   ├── requirements.txt
├── services/

└── README.md
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

To run the API in development mode:

```bash
uvicorn api.main:app --reload
```

The API will be available at http://localhost:8000

API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 