# Mobile Authentication API Documentation

This API provides authentication endpoints for mobile applications supporting both Google OAuth and direct email registration.

## Base URL
```
http://localhost:8000/api/v1/auth
```

## Endpoints

### 1. Google OAuth Authentication
**POST** `/google`

Authenticate users with Google OAuth access token.

**Request Body:**
```json
{
  "access_token": "google_access_token_here",
  "id_token": "optional_google_id_token"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://example.com/avatar.jpg",
    "google_id": "google_user_id",
    "created_at": "2025-08-27T10:00:00Z"
  }
}
```

### 2. Email Authentication
**POST** `/email`

Register/authenticate users with email and name.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://example.com/avatar.jpg"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://example.com/avatar.jpg",
    "google_id": null,
    "created_at": "2025-08-27T10:00:00Z"
  }
}
```

### 3. Get Current User
**GET** `/me`

Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer jwt_token_here
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://example.com/avatar.jpg",
  "google_id": "google_user_id",
  "created_at": "2025-08-27T10:00:00Z"
}
```

### 4. Health Check
**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "authentication"
}
```

## Error Responses

All endpoints return standardized error responses:

```json
{
  "error": {
    "code": 400,
    "message": "Error description",
    "type": "error_type",
    "details": []
  }
}
```

Common error codes:
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid token)
- `422`: Validation Error
- `500`: Internal Server Error

## Authentication Flow

### For Google OAuth:
1. Mobile app obtains Google OAuth access token
2. App sends access token to `/google` endpoint
3. API validates token with Google
4. API creates/updates user in database
5. API returns JWT token for future requests

### For Email Registration:
1. Mobile app collects user email and name
2. App sends data to `/email` endpoint
3. API creates/updates user in database
4. API returns JWT token for future requests

### Using JWT Token:
Include the JWT token in the Authorization header for protected endpoints:
```
Authorization: Bearer your_jwt_token_here
```

## Database Schema

The API uses the following user table schema:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    picture VARCHAR(1024),
    google_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
```

## Environment Variables

Required environment variables (see `.env.example`):

```
APP_SECRET_KEY=your-app-secret-key
APP_JWT_SECRET_KEY=your-jwt-secret-key
APP_JWT_EXPIRATION_HOURS=24
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_DATABASE=baldness_detector
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
```
