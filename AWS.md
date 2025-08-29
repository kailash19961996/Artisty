# Complete AWS Deployment Guide

## Architecture Overview
```
Frontend (React + Vite) → AWS Amplify
    ↓ API Calls
API Gateway → Lambda Function + Lambda Layers
    ↓ Dependencies
Lambda Layer (Python packages) + S3 (large dependencies)
```

---

## Part 1: Frontend Changes for AWS Deployment

### 1.1 Environment Configuration

**Create `.env` file in frontend folder:**
```bash
# Production API Gateway URL (replace after creating API Gateway)
VITE_API_BASE=https://YOUR-API-GATEWAY-ID.execute-api.YOUR-REGION.amazonaws.com/prod

# For local development
# VITE_API_BASE=http://localhost:5050
```

### 1.2 Amplify Build Configuration

**Frontend `amplify.yml`** (already exists):
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: dist
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
environmentVariables:
  - VITE_API_BASE
```

### 1.3 API Configuration

The frontend uses `src/components/api.js` which automatically handles environment variables:
```javascript
export const API_BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '');
export const apiFetch = (path, opts) =>
  fetch(`${API_BASE}${path.startsWith('/') ? path : '/' + path}`, opts);
```

This works for both:
- **Local**: Uses Vite proxy to `http://localhost:5050`
- **Production**: Uses `VITE_API_BASE` environment variable

---

## Part 2: Backend Lambda Setup

### 2.1 Lambda Function Code Structure

**Required files for Lambda package:**
```
lambda-function-code/
├── lambda.py          # Main handler (rename from lambda_function.py)
├── utils.py           # AI assistant logic
├── art.txt           # Inventory data
└── requirements.txt  # Empty (dependencies in layer)
```

### 2.2 Create Function-Only Package

#### Windows:
```powershell
# Navigate to backend folder
cd agent-new/Agent-shopper/backend

# Create clean function package
mkdir function-code
cd function-code

# Copy only Python files (not dependencies)
copy ..\Lambda\lambda.py .\lambda.py
copy ..\Lambda\utils.py .\utils.py
copy ..\art.txt .\art.txt

# Create empty requirements.txt
echo "# Dependencies provided by Lambda layer" > requirements.txt

# Create zip package
powershell Compress-Archive -Path * -DestinationPath function-code.zip -Force
```

#### Mac/Linux:
```bash
# Navigate to backend folder
cd agent-new/Agent-shopper/backend

# Create clean function package
mkdir function-code
cd function-code

# Copy only Python files
cp ../Lambda/lambda.py ./lambda.py
cp ../Lambda/utils.py ./utils.py
cp ../art.txt ./art.txt

# Create empty requirements.txt
echo "# Dependencies provided by Lambda layer" > requirements.txt

# Create zip package
zip -r function-code.zip *
```

### 2.3 Create Lambda Function in AWS

1. **AWS Console → Lambda → Create function**
2. **Configuration:**
   - Function name: `artisty-chatbot-backend`
   - Runtime: `Python 3.11`
   - Architecture: `x86_64`

3. **Upload function code:**
   - Upload from `.zip file`
   - Choose `function-code.zip`

4. **Configure function settings:**
   - Handler: `lambda.lambda_handler`
   - Timeout: `30 seconds`
   - Memory: `512 MB`

5. **Environment variables:**
   - `OPENAI_API_KEY`: `your-openai-api-key`
   - `OPENAI_MODEL`: `gpt-4o-mini`

---

## Part 3: Lambda Layers Setup (Linux-Compatible)

### 3.1 Create Dependencies Layer

#### Windows (Linux-compatible):
```powershell
# Create layer directory
mkdir lambda-layer
cd lambda-layer
mkdir python

# Install Linux-compatible dependencies
pip install --platform linux_x86_64 --only-binary=:all: --target python/ `
    openai==1.102.0 `
    langchain==0.3.27 `
    langchain-community==0.3.29 `
    langchain-openai==0.3.32 `
    pydantic==2.11.7

# Clean up unnecessary files
Get-ChildItem -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Include "*test*.py", "*tests*.py" | Remove-Item -Force

# Create layer zip
Compress-Archive -Path python -DestinationPath dependencies-layer.zip -Force
```

#### Mac:
```bash
# Create layer directory
mkdir lambda-layer
cd lambda-layer
mkdir python

# Install dependencies
pip install --platform linux_x86_64 --only-binary=:all: --target python/ \
    openai==1.102.0 \
    langchain==0.3.27 \
    langchain-community==0.3.29 \
    langchain-openai==0.3.32 \
    pydantic==2.11.7

# Clean up
find python/ -name "__pycache__" -type d -exec rm -rf {} +
find python/ -name "*test*.py" -delete

# Create layer zip
zip -r dependencies-layer.zip python/
```

#### Linux:
```bash
# Create layer directory
mkdir lambda-layer
cd lambda-layer
mkdir python

# Install dependencies for Lambda runtime
pip3 install --platform linux_x86_64 --only-binary=:all: --target python/ \
    openai==1.102.0 \
    langchain==0.3.27 \
    langchain-community==0.3.29 \
    langchain-openai==0.3.32 \
    pydantic==2.11.7

# Clean up unnecessary files
find python/ -name "__pycache__" -type d -exec rm -rf {} +
find python/ -name "*test*.py" -delete
find python/ -name "*.pyc" -delete

# Create layer zip
zip -r dependencies-layer.zip python/
```

### 3.2 Upload Layer via S3 (for large packages)

#### Upload to S3:
```bash
# Upload layer to S3
aws s3 cp dependencies-layer.zip s3://your-bucket-name/lambda-layers/

# Create layer from S3
aws lambda publish-layer-version \
    --layer-name artisty-dependencies \
    --content S3Bucket=your-bucket-name,S3Key=lambda-layers/dependencies-layer.zip \
    --compatible-runtimes python3.11
```

### 3.3 Attach Layer to Lambda Function

1. **Lambda Console → Your function → Layers section**
2. **Add a layer**
3. **Specify an ARN** (copy from layer creation response)
4. **Add**

**Example Layer ARN:**
```
arn:aws:lambda:us-east-1:123456789012:layer:artisty-dependencies:1
```

---

## Part 4: API Gateway Setup

### 4.1 Create REST API

1. **API Gateway Console → Create API → REST API**
2. **API name:** `artisty-chatbot-api`
3. **Endpoint Type:** Regional

### 4.2 Create Resources and Methods

#### Create `/api` resource:
```
Actions → Create Resource
Resource Name: api
Resource Path: /api
Enable API Gateway CORS: ✅
```

#### Create `/api/health` resource:
```
Select /api → Actions → Create Resource
Resource Name: health
Resource Path: /health
Enable API Gateway CORS: ✅
```

#### Create `/api/chat` resource:
```
Select /api → Actions → Create Resource
Resource Name: chat
Resource Path: /chat
Enable API Gateway CORS: ✅
```

### 4.3 Configure Methods

#### For `/api/health`:
1. **Create GET method:**
   - Integration type: Lambda Function
   - Lambda Function: `artisty-chatbot-backend`
   - Use Lambda Proxy integration: ✅

2. **Create OPTIONS method:**
   - Integration type: Mock
   - Deploy

#### For `/api/chat`:
1. **Create POST method:**
   - Integration type: Lambda Function
   - Lambda Function: `artisty-chatbot-backend`
   - Use Lambda Proxy integration: ✅

2. **Create OPTIONS method:**
   - Integration type: Mock
   - Deploy

### 4.4 Enable CORS

For each resource:
```
Actions → Enable CORS
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token
Access-Control-Allow-Methods: GET,POST,OPTIONS
```

### 4.5 Deploy API

```
Actions → Deploy API
Deployment stage: prod (create new)
```

**Note the Invoke URL:** `https://abc123.execute-api.region.amazonaws.com/prod`

---

## Part 5: Testing

### 5.1 Lambda Function Test Events

#### Health Check Test:
```json
{
  "httpMethod": "GET",
  "path": "/api/health",
  "headers": {
    "origin": "http://localhost:3000"
  },
  "queryStringParameters": null,
  "body": null
}
```

#### Chat Message Test:
```json
{
  "httpMethod": "POST",
  "path": "/api/chat",
  "headers": {
    "Content-Type": "application/json",
    "origin": "http://localhost:3000"
  },
  "body": "{\"message\": \"Hello, can you help me find some artwork?\"}"
}
```

#### Expected Success Response:
```json
{
  "statusCode": 200,
  "headers": {
    "Access-Control-Allow-Origin": "http://localhost:3000",
    "Content-Type": "application/json"
  },
  "body": "{\"response\":\"Hello! I'm Purple...\",\"web_actions\":[],\"intent\":\"general_info\",\"success\":true}"
}
```

### 5.2 API Gateway Testing

#### Test Health Endpoint:
```bash
curl https://YOUR-API-GATEWAY-URL/prod/api/health
```

#### Test Chat Endpoint:
```bash
curl -X POST https://YOUR-API-GATEWAY-URL/prod/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me find some artwork?"}'
```

### 5.3 Frontend Testing

1. **Update `.env` with your API Gateway URL**
2. **Deploy to Amplify**
3. **Test chatbot functionality**
4. **Check browser console for API calls**

---

## Part 6: AWS Amplify Frontend Deployment

### 6.1 Git Repository Setup

```bash
# Initialize git (if not already done)
cd agent-new/Agent-shopper
git init
git add .
git commit -m "Initial commit for Amplify deployment"

# Push to GitHub/GitLab
git remote add origin https://github.com/your-username/artisty-chatbot.git
git push -u origin main
```

### 6.2 Create Amplify App

1. **Amplify Console → Create new app**
2. **Connect repository** (GitHub/GitLab)
3. **Select branch:** `main`
4. **Build settings:** Auto-detected from `amplify.yml`
5. **App name:** `artisty-chatbot`

### 6.3 Environment Variables in Amplify

**App settings → Environment variables:**
```
VITE_API_BASE = https://YOUR-API-GATEWAY-URL/prod
```

### 6.4 Update Lambda CORS

After Amplify deployment, update Lambda function:
```python
ALLOWED_ORIGINS = [
    "https://main.YOUR-AMPLIFY-ID.amplifyapp.com",  # Your Amplify URL
    "http://localhost:5173",
    "http://localhost:3000",
]
```

---

## Part 7: Troubleshooting

### 7.1 Common Lambda Issues

#### Import Error (pydantic_core):
- **Cause:** Layer dependencies not Linux-compatible
- **Fix:** Recreate layer with `--platform linux_x86_64`

#### Memory/Timeout Issues:
- **Increase memory:** 512MB → 1GB
- **Increase timeout:** 30s → 60s

#### OpenAI API Errors:
- **Check environment variables** in Lambda
- **Verify API key** is valid

### 7.2 API Gateway Issues

#### CORS Errors:
- **Enable CORS** on all resources
- **Update Lambda ALLOWED_ORIGINS**
- **Deploy API** after changes

#### 502 Bad Gateway:
- **Check Lambda logs** in CloudWatch
- **Verify Lambda permissions**

### 7.3 Amplify Issues

#### Build Failures:
- **Check build logs** in Amplify console
- **Verify environment variables**
- **Check `amplify.yml` syntax**

#### API Call Failures:
- **Verify VITE_API_BASE** is set correctly
- **Check browser network tab** for errors

---

## Part 8: Security and Optimization

### 8.1 Security Best Practices

#### API Gateway:
- **Add API keys** for production
- **Implement rate limiting**
- **Use AWS Cognito** for authentication

#### Lambda:
- **Use IAM roles** for permissions
- **Store secrets** in AWS Secrets Manager
- **Enable CloudTrail** for audit logs

### 8.2 Cost Optimization

#### Lambda:
- **Use Provisioned Concurrency** for consistent performance
- **Monitor CloudWatch metrics**
- **Optimize memory allocation**

#### API Gateway:
- **Monitor usage** and set up billing alerts
- **Cache responses** where appropriate

---

## Part 9: Monitoring and Logs

### 9.1 CloudWatch Logs

#### Lambda Logs:
```
CloudWatch → Log groups → /aws/lambda/artisty-chatbot-backend
```

#### API Gateway Logs:
```
CloudWatch → Log groups → API-Gateway-Execution-Logs
```

### 9.2 Monitoring Setup

#### Lambda Metrics:
- **Duration**
- **Error rate**
- **Invocation count**
- **Memory utilization**

#### API Gateway Metrics:
- **Request count**
- **Error rate**
- **Latency**

---

## Part 10: Estimated Costs

### 10.1 AWS Lambda
- **Free tier:** 1M requests/month + 400,000 GB-seconds
- **Additional:** $0.20 per 1M requests + $0.0000166667 per GB-second

### 10.2 API Gateway
- **Free tier:** 1M API calls/month
- **Additional:** $3.50 per million API calls

### 10.3 AWS Amplify
- **Build:** $0.01 per build minute
- **Hosting:** $0.15 per GB served
- **Free tier:** 1,000 build minutes + 15GB served/month

### 10.4 S3 (for layer storage)
- **Storage:** $0.023 per GB/month
- **Requests:** Minimal cost for layer downloads

---

## Part 11: Production Checklist

### 11.1 Pre-Deployment
- [ ] Environment variables set in all services
- [ ] CORS origins updated for production URLs
- [ ] API Gateway deployed to `prod` stage
- [ ] Lambda function tested with real data
- [ ] Layer dependencies working correctly

### 11.2 Post-Deployment
- [ ] Health check endpoint responding
- [ ] Chat functionality working
- [ ] Frontend properly connecting to API
- [ ] CloudWatch logs showing expected behavior
- [ ] Error handling working correctly

### 11.3 Ongoing Maintenance
- [ ] Monitor CloudWatch metrics
- [ ] Set up billing alerts
- [ ] Regular dependency updates
- [ ] Performance optimization
- [ ] Security reviews

---

## Commands Quick Reference

### Layer Creation (Linux-compatible)
```bash
# Windows
pip install --platform linux_x86_64 --only-binary=:all: --target python/ package-name

# Mac/Linux
pip install --platform linux_x86_64 --only-binary=:all: --target python/ package-name
```

### Package Function Code
```bash
# Windows
powershell Compress-Archive -Path * -DestinationPath function-code.zip -Force

# Mac/Linux
zip -r function-code.zip *
```

### AWS CLI Commands
```bash
# Update Lambda function
aws lambda update-function-code --function-name artisty-chatbot-backend --zip-file fileb://function-code.zip

# Create layer
aws lambda publish-layer-version --layer-name artisty-dependencies --zip-file fileb://dependencies-layer.zip --compatible-runtimes python3.11

# Deploy API Gateway
aws apigateway create-deployment --rest-api-id YOUR-API-ID --stage-name prod
```

This guide provides complete instructions for deploying the Artisty chatbot to AWS using Lambda, API Gateway, and Amplify with proper separation of code and dependencies.
