# PACT — Deployment Configuration

**Provider**: Google Cloud Platform (GCP)
**Account**: jack@terrene.foundation
**Budget**: $379 credits — deploy cost-efficiently
**Date**: 2026-03-17

---

## Architecture (Cost-Optimized)

```
                    ┌─────────────────┐
                    │   Vercel (Free)  │
                    │  Next.js Web UI  │
                    │  care.terrene.dev│
                    └────────┬────────┘
                             │ API calls
                    ┌────────▼────────┐
                    │  GCP Cloud Run  │
                    │  FastAPI + Seed │
                    │  Scales to zero │
                    │  ~$0-2/month    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Neon (Free)   │
                    │   PostgreSQL    │
                    │   0.5GB free    │
                    └─────────────────┘
```

### Why This Architecture

| Decision           | Choice               | Cost        | Rationale                                                                              |
| ------------------ | -------------------- | ----------- | -------------------------------------------------------------------------------------- |
| API hosting        | Cloud Run            | ~$0-2/month | Always free tier: 2M requests, 360K GB-s. Scales to zero. Runs our Dockerfile.         |
| Database           | Neon Free Tier       | $0          | 0.5GB storage, always free. No Cloud SQL ($7+/month). Seed data regenerates on deploy. |
| Web frontend       | Vercel Free          | $0          | Next.js creators, zero config, 100GB bandwidth.                                        |
| Container registry | Artifact Registry    | ~$0         | 500MB free storage. One image ~200MB.                                                  |
| Domain             | \*.run.app (initial) | $0          | Custom domain later via terrene.dev DNS.                                               |

**Estimated monthly cost: $0-2** (well within the $379 credit budget)

---

## GCP Project Setup

```bash
# 1. Authenticate
gcloud auth login jack@terrene.foundation

# 2. Create project
gcloud projects create terrene-pact --name="PACT"

# 3. Link billing
gcloud billing projects link terrene-pact --billing-account=BILLING_ACCOUNT_ID

# 4. Set as active project
gcloud config set project terrene-pact

# 5. Enable required APIs
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com

# 6. Create Artifact Registry repo
gcloud artifacts repositories create pact \
  --repository-format=docker \
  --location=asia-southeast1 \
  --description="PACT container images"
```

## Deploy API to Cloud Run

```bash
# Build and push image
gcloud builds submit \
  --tag asia-southeast1-docker.pkg.dev/terrene-pact/pact/api:latest

# Deploy to Cloud Run
gcloud run deploy pact-api \
  --image asia-southeast1-docker.pkg.dev/terrene-pact/pact/api:latest \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars "PACT_DEV_MODE=true,PACT_API_PORT=8080,PACT_API_HOST=0.0.0.0"
```

## Deploy Web to Vercel

```bash
cd apps/web
vercel --prod
# Set NEXT_PUBLIC_API_URL to the Cloud Run URL
```

---

## Cost Controls

- **Cloud Run**: min-instances=0 (scales to zero when idle)
- **Memory**: 512Mi (minimum viable for FastAPI + seed data)
- **Max instances**: 2 (prevents runaway scaling)
- **No Cloud SQL**: Using Neon free tier or SQLite in-container
- **Budget alert**: Set at $10/month to catch unexpected usage

## Rollback

```bash
# List revisions
gcloud run revisions list --service pact-api --region asia-southeast1

# Roll back to previous revision
gcloud run services update-traffic pact-api \
  --to-revisions PREVIOUS_REVISION=100 \
  --region asia-southeast1
```

## Production Checklist

- [ ] GCP account authenticated (jack@terrene.foundation)
- [ ] Project created (terrene-pact)
- [ ] Billing linked
- [ ] APIs enabled (Cloud Run, Artifact Registry, Cloud Build)
- [ ] Docker image built and pushed
- [ ] Cloud Run service deployed
- [ ] Health check passing (GET /health returns 200)
- [ ] API endpoints accessible
- [ ] Budget alert configured ($10/month)
- [ ] Vercel frontend deployed with correct API URL
- [ ] Custom domain configured (future)
