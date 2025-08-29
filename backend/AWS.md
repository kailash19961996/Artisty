# Complete AWS Deployment Guide

## Architecture Overview
```
Frontend (React + Vite) → AWS Amplify
    ↓ API Calls
API Gateway → Lambda Function + Lambda Layers
    ↓ Dependencies
Lambda Layers (Python 3.11 packages built with Docker) + S3 (for layer zips)
```

---

## Part 1: Frontend Changes for AWS Deployment

### 1.1 Environment Configuration
Create `.env` in the frontend:
```bash
# Production API Gateway URL (replace after creating API Gateway)
VITE_API_BASE=https://YOUR-API-GATEWAY-ID.execute-api.YOUR-REGION.amazonaws.com/prod

# For local development
# VITE_API_BASE=http://localhost:5050
```

### 1.2 Amplify Build Configuration (`amplify.yml`)
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

### 1.3 API Helper
`src/components/api.js`:
```javascript
export const API_BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '');
export const apiFetch = (path, opts) =>
  fetch(`${API_BASE}${path.startsWith('/') ? path : '/' + path}`, opts);
```

---

## Part 2: Backend Lambda Setup

### 2.1 Function Code Structure (dependencies come from layers)
```
lambda-function-code/
├── lambda.py          # main handler (module: lambda, function: lambda_handler)
├── utils.py           # app logic
└── requirements.txt   # optional/empty (do not package 3rd‑party libs here)
```

### 2.2 Package the Function Only (no site-packages)

Windows (PowerShell):
```powershell
cd path\to\backend
mkdir function-code; cd function-code
copy ..\lambda.py .
copy ..\utils.py .
'Dependencies provided by Lambda layers' > requirements.txt
Compress-Archive -Path * -DestinationPath function-code.zip -Force
```

macOS/Linux:
```bash
cd path/to/backend
mkdir function-code && cd function-code
cp ../lambda.py ./
cp ../utils.py ./
echo "Dependencies provided by Lambda layers" > requirements.txt
zip -r function-code.zip *
```

### 2.3 Create the Lambda Function
- **Runtime:** Python 3.11
- **Architecture:** x86_64
- **Handler:** `lambda.lambda_handler`
- **Memory/Timeout:** 512MB / 30s (tune later)
- **Env vars:** `OPENAI_API_KEY=...`, optionally `OPENAI_MODEL=gpt-4o-mini`
- Upload `function-code.zip` in the Lambda console.

---

## Part 3: Lambda Layers Setup (Linux-Compatible via Docker + S3)

We build three **Python 3.11** layers on **Amazon Linux** using Docker, then upload to S3 and publish as layer versions.

### 3.1 Build Layers on Windows (PowerShell) with Docker Desktop
```powershell
# Work in an empty folder, e.g. C:\lambda-layers
$PY = "3.11"
$PLATFORM = "linux/amd64"   # use "linux/arm64/v8" if your Lambda uses arm64

# 1) pydantic layer (contains pydantic + pydantic-core)
docker run --rm --platform $PLATFORM -v "${PWD}:/var/task" public.ecr.aws/lambda/python:$PY bash -c "
set -e
L=/var/task/pydantic/python/lib/python$PY/site-packages
mkdir -p \$L
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -t \$L pydantic>=2.5.0
cd /var/task/pydantic && zip -r9 /var/task/layer-pydantic311.zip python
"

# 2) openai layer (exclude pydantic to avoid duplication)
docker run --rm --platform $PLATFORM -v "${PWD}:/var/task" public.ecr.aws/lambda/python:$PY bash -c "
set -e
L=/var/task/openai/python/lib/python$PY/site-packages
mkdir -p \$L
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -t \$L openai>=1.0.0 python-dotenv==1.0.0
rm -rf \$L/pydantic* \$L/pydantic_core*
cd /var/task/openai && zip -r9 /var/task/layer-openai311.zip python
"

# 3) langchain layer (exclude pydantic)
docker run --rm --platform $PLATFORM -v "${PWD}:/var/task" public.ecr.aws/lambda/python:$PY bash -c "
set -e
L=/var/task/langchain/python/lib/python$PY/site-packages
mkdir -p \$L
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -t \$L langchain>=0.1.0 langchain-community>=0.0.20 langchain-openai>=0.0.5
rm -rf \$L/pydantic* \$L/pydantic_core*
cd /var/task/langchain && zip -r9 /var/task/layer-langchain311.zip python
"
# Output zips in this folder:
#   layer-pydantic311.zip, layer-openai311.zip, layer-langchain311.zip
```

macOS/Linux (bash/zsh) equivalent:
```bash
PY=3.11
PLATFORM=linux/amd64   # use linux/arm64/v8 for Graviton

# pydantic
docker run --rm --platform "$PLATFORM" -v "$PWD:/var/task" public.ecr.aws/lambda/python:$PY bash -c '
set -e
L=/var/task/pydantic/python/lib/python'"$PY"'/site-packages
mkdir -p $L
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -t $L pydantic>=2.5.0
cd /var/task/pydantic && zip -r9 /var/task/layer-pydantic311.zip python
'
# openai
docker run --rm --platform "$PLATFORM" -v "$PWD:/var/task" public.ecr.aws/lambda/python:$PY bash -c '
set -e
L=/var/task/openai/python/lib/python'"$PY"'/site-packages
mkdir -p $L
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -t $L openai>=1.0.0 python-dotenv==1.0.0
rm -rf $L/pydantic* $L/pydantic_core*
cd /var/task/openai && zip -r9 /var/task/layer-openai311.zip python
'
# langchain
docker run --rm --platform "$PLATFORM" -v "$PWD:/var/task" public.ecr.aws/lambda/python:$PY bash -c '
set -e
L=/var/task/langchain/python/lib/python'"$PY"'/site-packages
mkdir -p $L
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -t $L langchain>=0.1.0 langchain-community>=0.0.20 langchain-openai>=0.0.5
rm -rf $L/pydantic* $L/pydantic_core*
cd /var/task/langchain && zip -r9 /var/task/layer-langchain311.zip python
'
```

### 3.2 Upload Zips to S3 and Publish Layers
```bash
# Upload
aws s3 cp layer-pydantic311.zip   s3://YOUR-BUCKET/lambda-layers/
aws s3 cp layer-openai311.zip     s3://YOUR-BUCKET/lambda-layers/
aws s3 cp layer-langchain311.zip  s3://YOUR-BUCKET/lambda-layers/

# Publish layer versions (Python 3.11)
aws lambda publish-layer-version \
  --layer-name pydantic-311 \
  --content S3Bucket=YOUR-BUCKET,S3Key=lambda-layers/layer-pydantic311.zip \
  --compatible-runtimes python3.11

aws lambda publish-layer-version \
  --layer-name openai-311 \
  --content S3Bucket=YOUR-BUCKET,S3Key=lambda-layers/layer-openai311.zip \
  --compatible-runtimes python3.11

aws lambda publish-layer-version \
  --layer-name langchain-311 \
  --content S3Bucket=YOUR-BUCKET,S3Key=lambda-layers/layer-langchain311.zip \
  --compatible-runtimes python3.11
```

### 3.3 Attach Layers to the Function
Lambda → your function → **Configuration → Layers → Add a layer** → select each custom layer (latest version).

---

## Part 4: API Gateway Setup

### 4.1 Create REST API
- API Gateway → **Create API → REST API**
- Name: `artisty-chatbot-api`
- Endpoint type: **Regional**

### 4.2 Resources
Create:
- `/api`
- `/api/health`
- `/api/chat`

### 4.3 Methods & Integration
For **/api/health**:
- **GET** → Integration type **Lambda Function**, Function: `artisty-chatbot-backend`, **Use Lambda Proxy integration** ✅
- **OPTIONS** → Mock (for CORS)

For **/api/chat**:
- **POST** → Lambda Function (proxy) → `artisty-chatbot-backend`
- **OPTIONS** → Mock

### 4.4 Enable CORS
Actions → **Enable CORS** on `/api`, `/api/health`, `/api/chat` with:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token
Access-Control-Allow-Methods: GET,POST,OPTIONS
```

### 4.5 Deploy
Actions → **Deploy API** → stage `prod`.
Invoke base URL: `https://YOUR-ID.execute-api.YOUR-REGION.amazonaws.com/prod`

---

## Part 5: Testing (Lambda & API Gateway)

### 5.1 Lambda Console Test Events (proxy format)

Health (GET):
```json
{
  "httpMethod": "GET",
  "path": "/api/health",
  "headers": { "origin": "http://localhost:3000" },
  "queryStringParameters": null,
  "body": null
}
```

Chat (POST):
```json
{
  "httpMethod": "POST",
  "path": "/api/chat",
  "headers": { "Content-Type": "application/json", "origin": "http://localhost:3000" },
  "body": "{\"message\": \"Hello, can you help me find some artwork?\"}"
}
```

### 5.2 API Gateway Console Test (raw HTTP bodies)

`/api/health` (GET):
- No body; click **Test**.

`/api/chat` (POST) body:
```json
{
  "message": "Hello, can you help me find some artwork?"
}
```

### 5.3 Curl (public URL)

Health:
```bash
curl -s https://YOUR-ID.execute-api.YOUR-REGION.amazonaws.com/prod/api/health
```

Chat:
```bash
curl -s -X POST https://YOUR-ID.execute-api.YOUR-REGION.amazonaws.com/prod/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, can you help me find some artwork?"}'
```

---

## Part 6: AWS Amplify Frontend Deployment

### 6.1 Connect Repo
Push your frontend repo (Amplify auto-detects Vite):
```bash
git init
git add .
git commit -m "Deploy to Amplify"
git remote add origin https://github.com/your-username/artisty-chatbot.git
git push -u origin main
```

### 6.2 Create Amplify App
- Amplify Console → **Create new app → Connect repository**
- Select branch `main`
- Add env var: `VITE_API_BASE=https://YOUR-ID.execute-api.YOUR-REGION.amazonaws.com/prod`
- Deploy

---

## Part 7: Troubleshooting

- **Internal server error at API Gateway but Lambda works:** Ensure **Lambda Proxy integration** is enabled, API is **deployed**, and the integration function **ARN** matches the current Lambda (if you deleted/recreated the function, re-select it and redeploy).
- **ImportError (pydantic_core, etc.):** Rebuild layers via Docker for the correct **Python 3.11** and **x86_64**.
- **CORS in browser:** Enable CORS in API Gateway and return `Access-Control-Allow-Origin` from Lambda.
- **Missing OpenAI key:** Set `OPENAI_API_KEY` in Lambda env vars.
- **Timeouts or OOM:** Bump memory to 1024MB and/or timeout to 60s, then re-test.

---

## Part 8: Security and Optimization

- Use **IAM roles** with least privilege.
- Put secrets in **AWS Secrets Manager** or SSM Parameter Store.
- Consider **API keys** / **Cognito** for production auth.
- Enable **CloudTrail** and **CloudWatch Alarms**.
- Right-size Lambda memory; consider **Provisioned Concurrency** if needed.

---

## Part 9: Monitoring and Logs

- **Lambda logs:** CloudWatch → Log groups → `/aws/lambda/artisty-chatbot-backend`
- **API Gateway logs:** enable execution logging (Stage settings) → CloudWatch log groups.
- Track Lambda metrics: Duration, Errors, Throttles, Memory.
- Track API Gateway metrics: Count, 4XX/5XX, Latency.

---

## Part 10: Estimated Costs (rough)

- **Lambda:** $0.20 per 1M requests + $/GB-s (first 1M + 400k GB-s free).
- **API Gateway (REST):** ~$3.50 per 1M calls (first 1M free).
- **Amplify:** $0.01/min build, $0.15/GB hosted (free tier available).
- **S3:** ~$0.023/GB-month for layer storage.

---

## Part 11: Production Checklist

- [ ] Lambda uses Python **3.11** and **x86_64**.
- [ ] Layers built with Docker; attached to function.
- [ ] Env vars: `OPENAI_API_KEY` (and model if overriding).
- [ ] API Gateway methods use **Lambda Proxy integration**.
- [ ] CORS enabled and API **deployed** to `prod`.
- [ ] Frontend `VITE_API_BASE` points to the prod stage URL.
- [ ] CloudWatch logging enabled for API Gateway and Lambda.
- [ ] Billing alarms set; dashboards configured.
