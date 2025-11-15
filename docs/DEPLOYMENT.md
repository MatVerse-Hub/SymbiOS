# Deployment Guide: SymbiOS

## Prerequisites

- Node.js 18+
- Python 3.10+
- MongoDB 5.0+
- Docker & Docker Compose
- Git

---

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/symbios.git
cd symbios
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your values:
# - MONGODB_URI: mongodb://localhost:27017/symbios
# - JWT_SECRET: your_secret_key
# - POLYGON_RPC_URL: https://rpc-amoy.maticvigil.com
# - POLYGON_PRIVATE_KEY: your_private_key_here
```

### 3. Backend Setup
```bash
cd backend

# Install dependencies
npm install

# Start MongoDB (if local)
docker run -d -p 27017:27017 --name mongodb mongo:5.0

# Start backend server (port 5000)
npm run dev
```

### 4. AI Service Setup
```bash
cd backend/ai

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start AI service (port 8001)
python -m uvicorn core:app --port 8001 --reload
```

### 5. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server (port 5173)
npm run dev
```

### 6. Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000/api
- AI Service: http://localhost:8001
- Swagger UI: http://localhost:8001/docs

---

## Docker Deployment

### Build Images
```bash
# Backend
docker build -t symbios-backend ./backend

# AI Service
docker build -t symbios-ai ./backend/ai

# Frontend
docker build -t symbios-frontend ./frontend
```

### Run with Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  mongodb:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      MONGODB_URI: mongodb://mongodb:27017/symbios
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      - mongodb

  ai:
    build: ./backend/ai
    ports:
      - "8001:8001"

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_BASE_URL: http://localhost:5000

volumes:
  mongodb_data:
```

```bash
docker-compose up -d
```

---

## Polygon Amoy Testnet Deployment

### 1. Get Test ETH
Visit [Amoy Faucet](https://faucet.polygon.technology/)

### 2. Deploy Contracts
```bash
cd contracts

# Compile
npx hardhat compile

# Deploy to Amoy
npx hardhat run scripts/deploy.js --network amoy
```

**Output:**
```
✅ EvidenceNote deployed to: 0x742d35Cc6634C0532925a3b844Bc9e7595f42e1E
✅ OmegaGate deployed to: 0x8f3Cf7ad23Cd3CaDbD9735AFf958023D60C95Db6
✅ Deployer: 0x1234...abcd
```

### 3. Update Backend .env
```
EVIDENCE_NOTE_CONTRACT=0x742d35Cc6634C0532925a3b844Bc9e7595f42e1E
OMEGA_GATE_CONTRACT=0x8f3Cf7ad23Cd3CaDbD9735AFf958023D60C95Db6
```

---

## AWS EC2 Deployment

### 1. Launch EC2 Instance
```bash
# Ubuntu 22.04 LTS, t3.medium (2 vCPU, 4GB RAM)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key \
  --security-groups default
```

### 2. Connect & Setup
```bash
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js, Python, Docker
sudo apt install -y nodejs npm python3-pip docker.io docker-compose
```

### 3. Deploy Application
```bash
git clone https://github.com/your-org/symbios.git
cd symbios

# Copy environment configuration
scp -i your-key.pem .env ubuntu@your-instance-ip:/home/ubuntu/symbios/

# Start with Docker Compose
docker-compose up -d
```

### 4. Configure Domain & HTTPS
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Update nginx config (if using reverse proxy)
# Configure to forward http/https to localhost ports
```

---

## Production Checklist

- [ ] Enable HTTPS with valid SSL certificate
- [ ] Set strong JWT_SECRET (min 32 chars)
- [ ] Use bcrypt for password hashing (update User model)
- [ ] Enable MongoDB authentication
- [ ] Configure rate limiting
- [ ] Setup MongoDB backups
- [ ] Enable blockchain gas optimization
- [ ] Setup monitoring (PM2, CloudWatch)
- [ ] Configure logging aggregation
- [ ] Add API key authentication
- [ ] Setup CI/CD pipeline
- [ ] Test disaster recovery procedures

---

## Monitoring & Troubleshooting

### View Logs
```bash
# Backend
docker logs symbios-backend

# AI Service
docker logs symbios-ai

# Frontend
docker logs symbios-frontend
```

### Common Issues

**MongoDB Connection Error**
```
Error: connect ECONNREFUSED 127.0.0.1:27017
```
Solution: Ensure MongoDB is running on correct port

**AI Service Not Responding**
```
Error: ECONNREFUSED http://localhost:8001/calibrate
```
Solution: Check AI service is running on port 8001

**Blockchain Transaction Failed**
```
Error: insufficient funds for gas * price + value
```
Solution: Get test ETH from Amoy faucet

---

## Scaling Considerations

- **Database:** Use MongoDB Atlas for managed cloud database
- **AI Service:** Scale horizontally with load balancer
- **Frontend:** Deploy to Vercel or CloudFront CDN
- **Blockchain:** Consider L2 solutions (Arbitrum, Optimism) for lower gas costs
