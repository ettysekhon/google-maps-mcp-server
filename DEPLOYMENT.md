# Deployment Guide

This guide covers deploying the Google Maps MCP Server to Google Kubernetes Engine (GKE).

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────┐
│  MCP Client (Agent, Claude, etc.)                               │
│  Connects via SSE to: http://<IP>/sse                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP (SSE + POST)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  GKE Load Balancer (or ClusterIP for internal)                  │
│  Port 80 → Pod Port 8080                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  MCP Server Pod                                                 │
│  ├── /sse      - SSE endpoint (GET) - streaming connection     │
│  ├── /messages - Message endpoint (POST) - client requests     │
│  └── /health   - Health check (GET) - returns JSON status      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Google Maps Platform APIs                                      │
│  (Places, Directions, Geocoding, etc.)                          │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Google Cloud SDK (`gcloud`) installed and configured
- `kubectl` installed
- `envsubst` available (usually pre-installed on Linux/macOS)
- A Google Cloud Project with billing enabled
- A Google Maps API Key with required APIs enabled

---

## Quick Reference: Makefile Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make docker-run` | Run locally with Docker Compose |
| `make verify-local` | Verify local Docker deployment |
| `make deploy-all` | Full GKE deployment (build + push + apply) |
| `make deploy-build` | Build and push container to GCR |
| `make deploy-apply` | Apply Kubernetes manifests |
| `make deploy-secret` | Create/update API key secret (interactive) |
| `make deploy-status` | Check pods and service status |
| `make deploy-logs` | Stream pod logs |
| `make k8s-forward` | Port-forward for local access |
| `make verify-gke` | Verify GKE deployment |

---

## Local Docker Testing

**Always test locally before deploying to GKE.**

### 1. Set API Key

```bash
# Option A: Environment variable
export GOOGLE_MAPS_API_KEY=your-key

# Option B: Create .env file in project root
echo "GOOGLE_MAPS_API_KEY=your-key" > .env
```

### 2. Build and Run

```bash
make docker-run
```

### 3. Verify (in another terminal)

```bash
make verify-local
```

Expected output:

```text
Step 1: Health Check
  [PASS] Health Check Passed
Step 2: SSE Endpoint Accessibility
  [PASS] SSE Endpoint Accessible
Step 3: MCP Client Connection & Tool Listing
  [PASS] Connected! Found 11 tools
```

### 4. Stop

```bash
make docker-stop
```

---

## First-Time GKE Deployment

### 1. Set Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_REGION=europe-west2  # or your preferred region
```

### 2. Create GKE Cluster (if needed)

```bash
gcloud container clusters create-auto google-maps-cluster \
    --region $GOOGLE_CLOUD_REGION \
    --project $GOOGLE_CLOUD_PROJECT

gcloud container clusters get-credentials google-maps-cluster \
    --region $GOOGLE_CLOUD_REGION \
    --project $GOOGLE_CLOUD_PROJECT
```

### 3. Create API Key Secret

```bash
make deploy-secret
```

### 4. Deploy

```bash
make deploy-all
```

### 5. Verify

```bash
make deploy-status
make deploy-logs
```

---

## Redeploying After Code Changes

This is the most common operation. Follow these steps:

### Step 1: Test Locally First

```bash
make docker-run
make verify-local
```

### Step 2: Build and Push New Image

```bash
make deploy-build
```

This uses Cloud Build to:

1. Upload source code to GCS
2. Build Docker image using `docker/Dockerfile`
3. Push to `gcr.io/$GOOGLE_CLOUD_PROJECT/google-maps-mcp-server:latest`

### Step 3: Force Pod to Pull New Image

**Important:** Simply running `make deploy-apply` may not pull the new image because:

- The image tag is `latest` (unchanged)
- Kubernetes may use the cached image

To force a fresh pull:

```bash
kubectl delete pod -l app=google-maps-mcp-server
kubectl rollout restart deployment/google-maps-mcp-server
```

### Step 4: Wait for New Pod

```bash
kubectl get pods -l app=google-maps-mcp-server -w
```

Wait until you see `1/1 Running` for the new pod.

### Step 5: Verify

```bash
uv run python scripts/verify_deployment.py http://<EXTERNAL-IP>/sse
make k8s-forward
make verify-gke
```

### Quick Redeploy (All Steps Combined)

```bash
make deploy-build && kubectl delete pod -l app=google-maps-mcp-server && kubectl get pods -l app=google-maps-mcp-server -w
```

---

## Connecting to the Server

### Internal (ClusterIP) - For Agents in Same Cluster

Default configuration. Agents running in the same GKE cluster connect via:

```text
http://google-maps-mcp-server.default.svc.cluster.local/sse
```

### Public (LoadBalancer) - For External Testing

To expose publicly:

1. Edit `k8s/deployment.yaml`: change `type: ClusterIP` to `type: LoadBalancer`
2. Apply: `make deploy-apply`
3. Get external IP: `kubectl get service google-maps-mcp-server -w`
4. Wait for `EXTERNAL-IP` (may take 1-2 minutes)

**Security Warning:** Public endpoints are accessible to anyone. For production:

- Add authentication
- Use HTTPS (configure Ingress with TLS)
- Restrict with firewall rules

To revert to internal-only:

1. Edit `k8s/deployment.yaml`: change `type: LoadBalancer` to `type: ClusterIP`
2. Apply: `make deploy-apply`

### Local Testing via Port-Forward

```bash
make k8s-forward
curl http://localhost:8080/health
make verify-gke
```

---

## Troubleshooting

### Pod Stuck in Pending

```bash
kubectl describe pod -l app=google-maps-mcp-server
```

**Common causes:**

- Insufficient cluster resources → Autopilot will scale, wait 1-2 minutes
- Image pull errors → Check GCR permissions

### Pod in CrashLoopBackOff

```bash
kubectl logs -l app=google-maps-mcp-server --previous
```

**Common causes:**

- Missing `GOOGLE_MAPS_API_KEY` secret → Run `make deploy-secret`
- Invalid API key → Check key in Google Cloud Console
- Pydantic validation error → API key is empty or malformed

### Secret Not Found

```bash
kubectl get secrets
```

If missing:

```bash
make deploy-secret
```

### LoadBalancer External IP Stuck on `<pending>`

```bash
kubectl describe service google-maps-mcp-server
```

**Common causes:**

- Quota limits → Check project quotas in GCP Console
- Permissions → GKE service account needs compute permissions
- Wait longer → Can take 1-3 minutes

### MCP Client Connection Fails (Error in post_writer)

**Symptom:** Health check passes, SSE connects, but tool listing fails with `RemoteProtocolError: Server disconnected without sending a response`

**Cause:** Pod is running old image that doesn't have the latest SSE fixes.

**Fix:**

```bash
kubectl delete pod -l app=google-maps-mcp-server
kubectl get pods -l app=google-maps-mcp-server -w
make verify-gke
```

### 307 Redirect on /sse Endpoint

**Symptom:** SSE endpoint returns HTTP 307 instead of 200.

**Cause:** Starlette's `Mount` adds trailing slash redirects.

**Fix:** This was fixed in `api.py` by using middleware to handle `/sse` and `/messages` as raw ASGI handlers. Ensure you have the latest code deployed.

### Health Check Passes But SSE Fails

**Symptom:** `/health` returns 200, but `/sse` returns 500 or connection errors.

**Diagnosis:**

```bash
kubectl logs -l app=google-maps-mcp-server --tail=100
```

**Common causes:**

- TypeError in ASGI handlers → Deploy latest code
- Missing dependencies → Rebuild image with `make deploy-build`

### Cloud Build Fails

**Symptom:** `make deploy-build` fails.

**Common errors:**

1. `Dockerfile required when specifying --tag`
   - Fixed: We now use `cloudbuild.yaml` which specifies `docker/Dockerfile`

2. `NOT_FOUND: Requested entity was not found`
   - Enable required APIs:

     ```bash
     gcloud services enable cloudbuild.googleapis.com
     gcloud services enable containerregistry.googleapis.com
     ```

3. Permission denied
   - Ensure Cloud Build service account has Storage and GCR permissions

---

## File Reference

| File | Purpose |
|------|---------|
| `src/google_maps_mcp_server/api.py` | HTTP/SSE server implementation |
| `docker/Dockerfile` | Container build instructions |
| `docker/docker-compose.yml` | Local Docker testing config |
| `k8s/deployment.yaml` | Kubernetes Deployment and Service |
| `cloudbuild.yaml` | Google Cloud Build configuration |
| `scripts/verify_deployment.py` | Deployment verification script |
| `Makefile` | Convenience commands |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_MAPS_API_KEY` | Yes | Google Maps Platform API key |
| `LOG_LEVEL` | No | Logging level (default: INFO) |
| `GOOGLE_CLOUD_PROJECT` | For GKE | GCP project ID |
| `GOOGLE_CLOUD_REGION` | For GKE | GCP region (e.g., europe-west2) |

---

## CI/CD Pipeline

Automated deployment is configured via GitHub Actions. Pushes to the `main` branch automatically deploy to GKE.

### GitHub Secrets Required

Configure the following secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | Your Google Cloud project ID |
| `GCP_SERVICE_ACCOUNT` | Service account email (e.g., `deployer@project.iam.gserviceaccount.com`) |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload Identity Provider resource name |

### Setting Up Workload Identity Federation (Recommended)

Workload Identity Federation is more secure than using service account keys.

```bash
export PROJECT_ID=your-project-id
export GITHUB_ORG=your-github-username-or-org
export GITHUB_REPO=google-maps-mcp-server
export SA_NAME=github-deployer

gcloud iam service-accounts create $SA_NAME \
    --display-name="GitHub Actions Deployer" \
    --project=$PROJECT_ID

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/container.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud iam workload-identity-pools create github-pool \
    --location="global" \
    --display-name="GitHub Actions Pool" \
    --project=$PROJECT_ID

gcloud iam workload-identity-pools providers create-oidc github-provider \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --project=$PROJECT_ID

gcloud iam service-accounts add-iam-policy-binding $SA_NAME@$PROJECT_ID.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-pool/attribute.repository/$GITHUB_ORG/$GITHUB_REPO" \
    --project=$PROJECT_ID

# Get the Workload Identity Provider resource name (use this for GCP_WORKLOAD_IDENTITY_PROVIDER secret)
gcloud iam workload-identity-pools providers describe github-provider \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --project=$PROJECT_ID \
    --format="value(name)"
```

### Pipeline Flow

```text
Push to main
    │
    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Test     │────▶│    Build    │────▶│   Deploy    │
│  (lint,     │     │  (Docker    │     │  (kubectl   │
│   mypy,     │     │   to GCR)   │     │   apply +   │
│   pytest)   │     │             │     │   restart)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Manual Trigger

You can also manually trigger the deployment workflow from the GitHub Actions tab using the "Run workflow" button.
