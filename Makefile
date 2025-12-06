.PHONY: install test lint format docker-build docker-run docker-stop k8s-forward verify-local \
        deploy-build deploy-push deploy-secret deploy-apply deploy-status deploy-logs deploy-all

# ============================================================================
# Development
# These are your day-to-day commands when working on the codebase.
# ============================================================================

install:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check src tests

format:
	uv run black src tests
	uv run ruff check src tests --fix

# ============================================================================
# Local Docker Testing
# Always test locally before deploying to GKE. This catches most issues early
# and saves time waiting for remote builds. The Docker environment closely
# mirrors production.
# ============================================================================

docker-build:
	docker build -t google-maps-mcp-server:latest -f docker/Dockerfile .

# Requires GOOGLE_MAPS_API_KEY either as an environment variable or in a .env
# file at the project root. The .env file is gitignored so safe for secrets.
docker-run:
	@if [ -z "$$GOOGLE_MAPS_API_KEY" ] && [ ! -f .env ]; then \
		echo "Error: GOOGLE_MAPS_API_KEY not set and no .env file found"; \
		echo "Either:"; \
		echo "  1. Create a .env file with GOOGLE_MAPS_API_KEY=your-key"; \
		echo "  2. Run: export GOOGLE_MAPS_API_KEY=your-key"; \
		exit 1; \
	fi
	docker compose -f docker/docker-compose.yml up --build

docker-stop:
	docker compose -f docker/docker-compose.yml down

# Run this in a separate terminal after docker-run. Waits 5s for the server
# to initialise before testing health, SSE, and MCP tool listing.
verify-local:
	@echo "Verifying deployment at http://localhost:8080/sse"
	@echo "Waiting 5s for server to be ready..."
	@sleep 5
	uv run python scripts/verify_deployment.py http://localhost:8080/sse

# ============================================================================
# GKE Deployment
# These commands deploy to Google Kubernetes Engine. You must have gcloud and
# kubectl configured, and be authenticated to the correct project/cluster.
#
# Required environment variables:
#   GOOGLE_CLOUD_PROJECT - Your GCP project ID (e.g., simple-gcp-data-pipeline)
#   GOOGLE_CLOUD_REGION  - GCP region (e.g., europe-west2)
#
# First-time setup:
#   1. make deploy-secret  (creates K8s secret for the Maps API key)
#   2. make deploy-all     (builds image and deploys)
#
# Subsequent deploys after code changes:
#   make deploy-build && kubectl delete pod -l app=google-maps-mcp-server
# ============================================================================

# Hidden target that validates required env vars are set. Called by other
# targets as a dependency - you won't run this directly.
.check-gcp-env:
	@if [ -z "$$GOOGLE_CLOUD_PROJECT" ]; then \
		echo "Error: GOOGLE_CLOUD_PROJECT not set"; \
		echo "Run: export GOOGLE_CLOUD_PROJECT=your-project-id"; \
		exit 1; \
	fi
	@if [ -z "$$GOOGLE_CLOUD_REGION" ]; then \
		echo "Error: GOOGLE_CLOUD_REGION not set"; \
		echo "Run: export GOOGLE_CLOUD_REGION=your-region (e.g., europe-west2)"; \
		exit 1; \
	fi

# Submits code to Cloud Build which builds the Docker image remotely and pushes
# to Google Container Registry. Uses cloudbuild.yaml for build configuration.
deploy-build: .check-gcp-env
	@echo "Building and pushing to gcr.io/$$GOOGLE_CLOUD_PROJECT/google-maps-mcp-server:latest"
	gcloud builds submit --config=cloudbuild.yaml .

# Creates a Kubernetes secret containing the Google Maps API key. The pod reads
# this at runtime - it's not baked into the image. Run this once per cluster,
# or again if you need to rotate the key.
deploy-secret:
	@echo "Creating/updating Kubernetes secret for Google Maps API Key"
	@read -p "Enter your Google Maps API Key: " key && \
		kubectl create secret generic google-maps-api-key --from-literal=key=$$key --dry-run=client -o yaml | kubectl apply -f -

# Applies the Kubernetes Deployment and Service. Uses envsubst to substitute
# GOOGLE_CLOUD_PROJECT into k8s/deployment.yaml (for the image path).
deploy-apply: .check-gcp-env
	@echo "Deploying to GKE..."
	envsubst < k8s/deployment.yaml | kubectl apply -f -

deploy-status:
	@echo "=== Pods ==="
	kubectl get pods -l app=google-maps-mcp-server
	@echo ""
	@echo "=== Service ==="
	kubectl get service google-maps-mcp-server
	@echo ""
	@echo "=== Recent Events ==="
	kubectl get events --sort-by='.lastTimestamp' | grep -i google-maps-mcp || true

# Streams logs from the running pod. Useful for debugging startup issues or
# watching tool invocations. Press Ctrl+C to stop.
deploy-logs:
	kubectl logs -l app=google-maps-mcp-server --tail=100 -f

# Full deployment: builds image, pushes to GCR, applies K8s manifests.
# Note: If the image tag hasn't changed (we use :latest), K8s might not pull
# the new image. Delete the pod afterwards to force a fresh pull.
deploy-all: deploy-build deploy-apply
	@echo ""
	@echo "Deployment complete! Checking status..."
	@sleep 5
	$(MAKE) deploy-status

# Forwards the K8s service to localhost:8080. Run in a separate terminal, then
# use verify-gke or curl http://localhost:8080/health to test.
k8s-forward:
	@echo "Starting port-forward to http://localhost:8080"
	@echo "Press Ctrl+C to stop"
	kubectl port-forward service/google-maps-mcp-server 8080:80

# Tests the GKE deployment via the port-forward. Ensure k8s-forward is running
# in another terminal before executing this.
verify-gke:
	@echo "Verifying GKE deployment via port-forward..."
	@echo "Make sure 'make k8s-forward' is running in another terminal"
	uv run python scripts/verify_deployment.py http://localhost:8080/sse

# ============================================================================
# Help
# ============================================================================

help:
	@echo "Google Maps MCP Server - Makefile Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install       - Install dependencies with uv"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linter"
	@echo "  make format        - Format code"
	@echo ""
	@echo "Local Docker:"
	@echo "  make docker-build  - Build Docker image locally"
	@echo "  make docker-run    - Run with Docker Compose (needs GOOGLE_MAPS_API_KEY)"
	@echo "  make docker-stop   - Stop Docker Compose"
	@echo "  make verify-local  - Verify local deployment"
	@echo ""
	@echo "GKE Deployment (requires GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_REGION):"
	@echo "  make deploy-build  - Build and push to GCR"
	@echo "  make deploy-secret - Create/update API key secret"
	@echo "  make deploy-apply  - Apply Kubernetes manifests"
	@echo "  make deploy-all    - Full deployment (build + apply)"
	@echo "  make deploy-status - Check deployment status"
	@echo "  make deploy-logs   - View pod logs"
	@echo "  make k8s-forward   - Port forward for local access"
	@echo "  make verify-gke    - Verify GKE deployment"
