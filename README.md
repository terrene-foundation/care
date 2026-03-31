# CARE Assessment & Onboarding Kit

AI-guided governance assessment for non-technical leaders. Discover what AI governance your organization needs, then generate configuration to operationalize it.

**Terrene Foundation** | Apache 2.0

## Quick Start

```bash
# Backend
pip install -e ".[all]"
cp .env.example .env  # Add your API key
care  # Starts API server on :8000

# Frontend
cd apps/web
npm install
npm run dev  # Starts web app on :3000
```

## Docker

```bash
cp .env.example .env  # Add your API key
docker compose up
```

Open `http://localhost:3000` and start your assessment.
