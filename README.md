# Intao Services API

This is a FastAPI-based REST API for Intao Services.

## Project Structure```
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

## Membership Pro User Management (Intao WordPress)

The API allows management of Membership Pro users directly in the WordPress database, including listing and creating users.

### List Users
- Endpoint: `GET /api/membership-pro/users`
- Returns all users registered in the WordPress `xwh_users` table, with all relevant fields.

### Create User
- Endpoint: `POST /api/membership-pro/users`
- Allows creating a new WordPress user by sending a JSON with the required fields, for example:

```json
{
  "user_login": "mascarenhas",
  "user_pass": "Smascarenhas3862",
  "user_nicename": "otavio_mascarenhas",
  "user_email": "otaviomascarenhaspessoal@gmail.com",
  "user_url": "",
  "user_registered": "2025-05-26T23:45:16.497Z",
  "user_activation_key": "",
  "user_status": 0,
  "display_name": "Otávio Mascarenhas"
}
```

#### Password Encryption
- **The password sent in `user_pass` can be in plain text.**
- **The API automatically encrypts the password using the `phpass` algorithm (WordPress compatible) before saving to the database.**
- This allows the user to login normally to WordPress with the provided password.

### Notes
- User activation/deactivation control can be done through the activation/deactivation endpoints, which can be customized according to business logic.
- The user model follows the standard WordPress table structure (`xwh_users`).

For usage examples or details of other endpoints, check the Swagger documentation at `/docs` after starting the project.

