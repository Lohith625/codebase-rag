# Deployment Guide

## Docker Deployment

### Build and Run with Docker Compose
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

Create a `.env` file with:
```
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=us-east-1
```

## Manual Deployment

### Requirements
- Python 3.9+
- Git
- 2GB+ RAM
- 10GB+ storage

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/codebase-rag.git
cd codebase-rag

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start API server
python scripts/run_api.py

# In another terminal, start frontend
streamlit run frontend/app.py
```

## Cloud Deployment Options

### AWS
- **EC2**: t2.medium or larger
- **S3**: For data storage
- **ECS**: For containerized deployment

### GCP
- **Cloud Run**: Serverless deployment
- **Compute Engine**: VM deployment
- **Cloud Storage**: For data

### Azure
- **App Service**: Web app hosting
- **Container Instances**: Docker deployment
- **Blob Storage**: For data

## CI/CD

GitHub Actions workflows:
- **tests.yml**: Runs tests on push
- **auto-update.yml**: Updates index every 6 hours

## Monitoring

- Health endpoint: `/health`
- Stats endpoint: `/stats`
- API docs: `/docs`

## Scaling

For high traffic:
1. Use Pinecone instead of FAISS
2. Deploy multiple API instances with load balancer
3. Use Redis for caching
4. Enable CDN for frontend

## Security

- Use environment variables for secrets
- Enable HTTPS in production
- Implement rate limiting
- Use API authentication
