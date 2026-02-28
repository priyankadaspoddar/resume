# Resume-Based Interview System - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Resume-Based Interview System to various environments, including local development, cloud platforms, and containerized deployments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Deployment](#local-development-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Production Configuration](#production-configuration)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: Minimum 10GB free space

### External Dependencies
- **Google Gemini API Key**: For AI-powered analysis
- **PostgreSQL Database**: For data persistence
- **Redis**: For caching (optional but recommended)

## Local Development Deployment

### 1. Clone the Repository
```bash
git clone https://github.com/priyankadaspoddar/resume.git
cd resume
```

### 2. Environment Setup
```bash
# Copy environment variables template
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

Required environment variables:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/interview_system
```

### 3. Start Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Verify Deployment
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Development Mode
```bash
# Start in development mode with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## Docker Deployment

### Production Deployment

#### 1. Build Images
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

#### 2. Start Services
```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d backend frontend
```

#### 3. Verify Services
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# Health check
curl http://localhost:8000/health
curl http://localhost:3000/health
```

#### 4. Scale Services
```bash
# Scale backend service
docker-compose up -d --scale backend=3

# Scale frontend service
docker-compose up -d --scale frontend=2
```

### Docker Swarm Deployment

#### 1. Initialize Swarm
```bash
docker swarm init
```

#### 2. Deploy Stack
```bash
docker stack deploy -c docker-compose.yml interview-system
```

#### 3. Monitor Stack
```bash
# List services
docker service ls

# View service logs
docker service logs interview-system_backend
```

### Kubernetes Deployment

#### 1. Apply Kubernetes Manifests
```bash
# Apply all manifests
kubectl apply -f kubernetes/

# Apply specific manifests
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/postgres.yaml
kubectl apply -f kubernetes/redis.yaml
kubectl apply -f kubernetes/backend.yaml
kubectl apply -f kubernetes/frontend.yaml
kubectl apply -f kubernetes/ingress.yaml
```

#### 2. Verify Deployment
```bash
# Check pods
kubectl get pods -n interview-system

# Check services
kubectl get services -n interview-system

# Check ingress
kubectl get ingress -n interview-system
```

## Cloud Deployment

### AWS Deployment

#### 1. Prerequisites
- AWS CLI configured
- IAM permissions for ECS, RDS, ECR
- VPC and subnets configured

#### 2. Create ECR Repositories
```bash
# Create repositories
aws ecr create-repository --repository-name interview-system-backend
aws ecr create-repository --repository-name interview-system-frontend

# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com
```

#### 3. Build and Push Images
```bash
# Build images
docker-compose build

# Tag images
docker tag interview-system-backend:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/interview-system-backend:latest
docker tag interview-system-frontend:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/interview-system-frontend:latest

# Push images
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/interview-system-backend:latest
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/interview-system-frontend:latest
```

#### 4. Create RDS Database
```bash
aws rds create-db-instance \
    --db-instance-identifier interview-system-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username postgres \
    --master-user-password your-password \
    --allocated-storage 20
```

#### 5. Deploy to ECS
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name interview-system

# Register task definitions
aws ecs register-task-definition --cli-input-json file://aws/task-definition-backend.json
aws ecs register-task-definition --cli-input-json file://aws/task-definition-frontend.json

# Create services
aws ecs create-service --cluster interview-system --service-name backend --task-definition backend:1 --desired-count 2
aws ecs create-service --cluster interview-system --service-name frontend --task-definition frontend:1 --desired-count 2
```

### Google Cloud Platform Deployment

#### 1. Prerequisites
- Google Cloud SDK installed
- Project created and configured
- Container Registry enabled

#### 2. Build and Push Images
```bash
# Set project
gcloud config set project your-project-id

# Build images
gcloud builds submit --tag gcr.io/your-project-id/interview-system-backend
gcloud builds submit --tag gcr.io/your-project-id/interview-system-frontend
```

#### 3. Create Cloud SQL Database
```bash
# Create instance
gcloud sql instances create interview-system-db \
    --database-version=POSTGRES_13 \
    --tier=db-custom-1-3840 \
    --region=us-central1

# Create database
gcloud sql databases create interview_system --instance=interview-system-db

# Create user
gcloud sql users create postgres --instance=interview-system-db --password=your-password
```

#### 4. Deploy to Cloud Run
```bash
# Deploy backend
gcloud run deploy backend \
    --image gcr.io/your-project-id/interview-system-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated

# Deploy frontend
gcloud run deploy frontend \
    --image gcr.io/your-project-id/interview-system-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### Azure Deployment

#### 1. Prerequisites
- Azure CLI installed
- Resource group created
- Container Registry created

#### 2. Build and Push Images
```bash
# Login to Azure
az login

# Build and push images
az acr build --image interview-system-backend:latest --registry your-registry --file backend/Dockerfile .
az acr build --image interview-system-frontend:latest --registry your-registry --file frontend/Dockerfile .
```

#### 3. Create Azure Database for PostgreSQL
```bash
# Create server
az postgres server create \
    --resource-group your-resource-group \
    --name interview-system-db \
    --location eastus \
    --admin-user postgres \
    --admin-password your-password \
    --sku-name B_Gen5_1 \
    --version 11

# Create database
az postgres db create \
    --resource-group your-resource-group \
    --server-name interview-system-db \
    --name interview_system
```

#### 4. Deploy to Azure Container Instances
```bash
# Deploy backend
az container create \
    --resource-group your-resource-group \
    --name backend \
    --image your-registry.azurecr.io/interview-system-backend:latest \
    --cpu 2 \
    --memory 4 \
    --ports 8000

# Deploy frontend
az container create \
    --resource-group your-resource-group \
    --name frontend \
    --image your-registry.azurecr.io/interview-system-frontend:latest \
    --cpu 1 \
    --memory 2 \
    --ports 3000
```

## Production Configuration

### Environment Variables

Create a `.env.production` file with production-specific configuration:

```bash
# Production environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Production database
DATABASE_URL=postgresql://prod_user:prod_password@prod-db:5432/prod_interview_system

# Production Redis
REDIS_URL=redis://prod-redis:6379

# Production security
SECRET_KEY=your-production-secret-key
JWT_SECRET=your-production-jwt-secret

# Production AI configuration
GEMINI_API_KEY=your-production-gemini-key
GEMINI_MODEL=gemini-2.5-pro

# Production performance
MAX_CONCURRENT_REQUESTS=200
REQUEST_TIMEOUT_SECONDS=60
CACHE_TTL_SECONDS=7200

# Production monitoring
ENABLE_ANALYTICS=true
SENTRY_DSN=your-sentry-dsn
```

### SSL/TLS Configuration

#### 1. Generate SSL Certificates
```bash
# Using Let's Encrypt
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# Or using self-signed certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx-selfsigned.key \
    -out nginx-selfsigned.crt
```

#### 2. Update Nginx Configuration
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/nginx-selfsigned.crt;
    ssl_certificate_key /path/to/nginx-selfsigned.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Rest of configuration...
}
```

### Load Balancing

#### 1. Configure Multiple Backend Instances
```yaml
# docker-compose.yml
backend:
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '1.0'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M
```

#### 2. Configure Nginx Load Balancer
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Monitoring and Logging

#### 1. Application Monitoring
```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:3000/health

# Metrics endpoint
curl http://localhost:8000/metrics
```

#### 2. Log Aggregation
```bash
# View logs
docker-compose logs -f

# Export logs
docker-compose logs --no-color > app.log

# Structured logging with ELK stack
# Configure logstash to parse application logs
```

#### 3. Performance Monitoring
```bash
# Monitor resource usage
docker stats

# Monitor application performance
# Use APM tools like New Relic, Datadog, or Prometheus
```

## Monitoring and Maintenance

### Health Checks

#### Application Health
```bash
# Backend health check
curl -f http://localhost:8000/health

# Frontend health check
curl -f http://localhost:3000/health

# Database health check
docker-compose exec database pg_isready -U postgres
```

#### Service Health
```bash
# Check all services
docker-compose ps

# Check specific service
docker-compose ps backend

# Restart unhealthy services
docker-compose restart backend
```

### Backup and Recovery

#### Database Backup
```bash
# Backup database
docker-compose exec database pg_dump -U postgres interview_system > backup.sql

# Restore database
docker-compose exec -T database psql -U postgres -d interview_system < backup.sql
```

#### Application Backup
```bash
# Backup application data
tar -czf app-backup.tar.gz uploads/ logs/ models/

# Restore application data
tar -xzf app-backup.tar.gz
```

### Security Updates

#### 1. Update Base Images
```bash
# Update Docker images
docker-compose pull

# Rebuild with updated images
docker-compose build --no-cache
docker-compose up -d
```

#### 2. Update Dependencies
```bash
# Update Python dependencies
pip-review --auto

# Update Node.js dependencies
npm update

# Rebuild and redeploy
docker-compose build
docker-compose up -d
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM users;

-- Create indexes
CREATE INDEX idx_users_email ON users(email);

-- Vacuum and analyze
VACUUM ANALYZE;
```

#### 2. Application Optimization
```python
# Enable caching
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation():
    # Implementation
    pass
```

#### 3. CDN Configuration
```nginx
# Configure CDN for static assets
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    proxy_pass https://cdn.your-domain.com;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Troubleshooting

### Common Issues

#### 1. Container Startup Failures
```bash
# Check container logs
docker-compose logs backend

# Check container status
docker-compose ps

# Restart failed containers
docker-compose restart backend
```

#### 2. Database Connection Issues
```bash
# Check database connectivity
docker-compose exec backend python -c "import sqlalchemy; engine = sqlalchemy.create_engine(os.getenv('DATABASE_URL')); engine.connect()"

# Check database logs
docker-compose logs database
```

#### 3. AI Model Connection Issues
```bash
# Check Gemini API connectivity
python -c "import google.generativeai as genai; genai.configure(api_key=os.getenv('GEMINI_API_KEY')); print('Connected')"

# Check API key validity
curl -H "Authorization: Bearer $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1/models
```

### Debug Mode

#### 1. Enable Debug Logging
```bash
# Set debug environment variable
export DEBUG=true
docker-compose up -d

# View debug logs
docker-compose logs -f backend
```

#### 2. Development Mode
```bash
# Start in development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Access development tools
# Backend: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

### Performance Issues

#### 1. High Memory Usage
```bash
# Monitor memory usage
docker stats

# Optimize application
# - Implement caching
# - Optimize database queries
# - Reduce image sizes
```

#### 2. Slow Response Times
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/resume/analyze

# Optimize performance
# - Enable compression
# - Use CDN for static assets
# - Implement database indexing
```

### Security Issues

#### 1. SSL/TLS Configuration
```bash
# Check SSL configuration
openssl s_client -connect your-domain.com:443

# Fix SSL issues
# - Update certificates
# - Configure proper cipher suites
# - Enable HSTS
```

#### 2. Authentication Issues
```bash
# Check JWT configuration
python -c "import jwt; jwt.encode({'test': 'data'}, 'secret', algorithm='HS256')"

# Fix authentication
# - Verify secret keys
# - Check token expiration
# - Validate CORS settings
```

### Getting Help

#### 1. Documentation
- [API Documentation](http://localhost:8000/docs)
- [Development Guide](DEVELOPMENT_GUIDE.md)
- [Troubleshooting Guide](#troubleshooting)

#### 2. Community Support
- GitHub Issues
- Stack Overflow
- Discord/Slack channels

#### 3. Professional Support
- Contact information
- Support plans
- SLA details

For additional deployment scenarios or specific cloud provider configurations, please refer to the [Development Guide](DEVELOPMENT_GUIDE.md) or create an issue on GitHub.