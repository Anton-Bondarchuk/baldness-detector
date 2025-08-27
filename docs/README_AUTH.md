# Baldness Detector Authentication API

A FastAPI-based authentication service for mobile applications supporting both Google OAuth and direct email registration.

## Features

- ✅ Google OAuth authentication
- ✅ Email-based user registration
- ✅ JWT token generation and validation
- ✅ SQLAlchemy async database operations
- ✅ Comprehensive error handling
- ✅ Mobile-first API design
- ✅ Database migrations with Alembic

## Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to project
cd /home/user/projects/baldness-detector

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
```

Required variables:
- `APP_SECRET_KEY`: Secret key for session middleware
- `APP_JWT_SECRET_KEY`: Secret key for JWT tokens (make it strong!)
- `DB_*`: Database connection settings
- `GOOGLE_OAUTH_*`: Google OAuth credentials

### 3. Database Setup

```bash
# Run database migrations
alembic upgrade head
```

### 4. Run the API

```bash
# Development server
python -m app

# Or with uvicorn directly
uvicorn app.__main__:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Test the API

```bash
# Run the test script
python test_api.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/google` | POST | Authenticate with Google OAuth |
| `/api/v1/auth/email` | POST | Authenticate with email/name |
| `/api/v1/auth/me` | GET | Get current user (protected) |
| `/api/v1/auth/health` | GET | Health check |

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for detailed usage.

## Project Structure

```
app/
├── __main__.py                 # FastAPI application entry point
├── config.py                   # Configuration settings
└── oauth/
    ├── domain/
    │   ├── models/
    │   │   └── user.py         # User SQLAlchemy model
    │   └── services/
    │       └── auth_service.py # Authentication business logic
    ├── infra/
    │   ├── connection.py       # Database connection
    │   ├── get_db.py          # Database dependency
    │   ├── jwt_auth.py        # JWT utilities
    │   ├── pg_user_repository.py # User repository
    │   └── get_current_user.py # Auth dependency
    └── interfaces/
        ├── dto/
        │   ├── auth.py        # Authentication DTOs
        │   └── user.py        # User DTOs
        └── http/
            ├── google.py      # Authentication endpoints
            └── error_handlers.py # Error handling
```

## Mobile Integration

### Google OAuth Flow

1. Mobile app obtains Google OAuth access token
2. Send token to `/api/v1/auth/google`
3. Receive JWT token for API access

```javascript
// Example mobile app code
const googleToken = await GoogleSignin.getTokens();
const response = await fetch('/api/v1/auth/google', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ access_token: googleToken.accessToken })
});
const { access_token } = await response.json();
```

### Email Registration Flow

1. Collect user email and name
2. Send to `/api/v1/auth/email`
3. Receive JWT token for API access

```javascript
// Example mobile app code
const response = await fetch('/api/v1/auth/email', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    name: 'John Doe',
    picture: 'https://example.com/avatar.jpg'
  })
});
const { access_token } = await response.json();
```

### Using JWT Tokens

Include the JWT token in all subsequent API calls:

```javascript
const response = await fetch('/api/v1/auth/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  }
});
```

## Database Schema

The API uses the following user table:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    picture VARCHAR(1024),
    google_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Security Features

- JWT tokens with configurable expiration
- Password-less authentication
- Google OAuth token validation
- Email uniqueness enforcement
- Input validation with Pydantic
- CORS configuration for mobile apps

## Development

```bash
# Run with auto-reload
uvicorn app.__main__:app --reload

# Run tests
python test_api.py

# Check database migrations
alembic current
alembic history
```

## Production Deployment

1. Set `APP_DEBUG=false`
2. Configure proper CORS origins
3. Use environment variables for secrets
4. Set up PostgreSQL database
5. Configure reverse proxy (nginx)
6. Use proper SSL certificates

## License

[Your License Here]
