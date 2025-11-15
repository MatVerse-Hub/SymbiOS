# API Reference: SymbiOS

## Base URL
```
http://localhost:5000/api
```

## Authentication

All protected endpoints require JWT token in header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### **Auth**

#### POST `/auth/signup`
Create new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "John Doe",
  "organization": "ACME Corp"
}
```

**Response:** `201 Created`
```json
{
  "token": "eyJhbGc...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "omega_score": 0,
    "decisions_count": 0
  }
}
```

---

#### POST `/auth/login`
Authenticate user and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:** `200 OK`
```json
{
  "token": "eyJhbGc...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "omega_score": 0.87
  }
}
```

---

### **Decisions**

#### POST `/decisions`
Submit decision for AI calibration.

**Request:**
```json
{
  "title": "Launch Product X",
  "context": "Market analysis shows strong demand. Competitors entering in Q3.",
  "human_confidence": 0.85,
  "risk_tolerance": 0.6
}
```

**Processing Flow:**
1. Backend receives decision
2. Calls AI service: `POST http://localhost:8001/calibrate`
3. AI runs 10,000 Monte Carlo simulations
4. Returns Ω-Score, CVaR-95, recommendation
5. Stores in MongoDB
6. (Optional) Mints ERC-721 Evidence Note on Polygon Amoy

**Response:** `201 Created`
```json
{
  "id": "507f1f77bcf86cd799439012",
  "user_id": "507f1f77bcf86cd799439011",
  "title": "Launch Product X",
  "omega_score": 0.87,
  "cvar_95": 0.015,
  "recommendation": "ACCELERATE",
  "status": "completed",
  "blockchain_proof": "0x742d35Cc6634C0532925a3b844Bc9e7595f42e1E",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### GET `/decisions/:id`
Retrieve specific decision with all metrics.

**Response:** `200 OK`
```json
{
  "id": "507f1f77bcf86cd799439012",
  "title": "Launch Product X",
  "context": "Market analysis shows strong demand...",
  "omega_score": 0.87,
  "cvar_95": 0.015,
  "recommendation": "ACCELERATE",
  "confidence": 0.85,
  "risk_tolerance": 0.6,
  "blockchain_proof": "0x742d35Cc6634C0532925a3b844Bc9e7595f42e1E",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

#### GET `/decisions`
List user's decisions with pagination.

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20, max: 100)

**Example:** `GET /decisions?page=1&limit=10`

**Response:** `200 OK`
```json
{
  "decisions": [
    {
      "id": "507f1f77bcf86cd799439012",
      "title": "Launch Product X",
      "omega_score": 0.87,
      "cvar_95": 0.015,
      "recommendation": "ACCELERATE",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 45
  }
}
```

---

### **Metrics**

#### GET `/metrics/omega`
Dashboard overview: user's Ω-Score, decision count, recommendations breakdown.

**Response:** `200 OK`
```json
{
  "user_omega_score": 0.87,
  "decisions_count": 12,
  "decisions_omega_avg": 0.81,
  "recommendations": {
    "ACCELERATE": 6,
    "MONITOR": 4,
    "PAUSE": 2
  },
  "antifragile": "✅ System is Antifrágil"
}
```

---

#### GET `/metrics/history`
30-day historical trend for charts.

**Response:** `200 OK`
```json
{
  "history": [
    {
      "date": "2024-01-01",
      "omega_score": 0.75,
      "cvar_95": 0.025,
      "decision_count": 2
    },
    {
      "date": "2024-01-02",
      "omega_score": 0.78,
      "cvar_95": 0.022,
      "decision_count": 3
    }
  ]
}
```

---

## Error Responses

### `400 Bad Request`
```json
{
  "error": "Invalid email format"
}
```

### `401 Unauthorized`
```json
{
  "error": "Invalid credentials"
}
```

### `500 Internal Server Error`
```json
{
  "error": "Failed to process decision"
}
```

---

## Rate Limiting

- **Auth endpoints:** 10 requests/minute
- **Decision endpoints:** 50 requests/minute
- **Metrics endpoints:** 100 requests/minute

---

## Example Workflow

```bash
# 1. Sign up
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure123",
    "name": "John",
    "organization": "ACME"
  }'

# 2. Submit decision
curl -X POST http://localhost:5000/api/decisions \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Launch Product",
    "context": "Strong market demand",
    "human_confidence": 0.85,
    "risk_tolerance": 0.6
  }'

# 3. Get metrics
curl -X GET http://localhost:5000/api/metrics/omega \
  -H "Authorization: Bearer eyJhbGc..."
```
