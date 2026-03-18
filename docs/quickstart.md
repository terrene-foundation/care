# Quickstart Tutorial

Get the CARE Platform running in under 5 minutes. Choose your path:

## Option A: Docker Compose (recommended)

The fastest way to get everything running — API server, dashboard, and database.

### 1. Clone and configure

```bash
git clone https://github.com/terrene-foundation/care.git
cd care
cp .env.example .env
```

Edit `.env` and set at minimum:

```bash
CARE_API_TOKEN=your-secure-token-here
POSTGRES_PASSWORD=your-db-password
```

### 2. Start the platform

```bash
docker compose up
```

This starts three services:

- **API server** at `http://localhost:8000`
- **Dashboard** at `http://localhost:3000`
- **PostgreSQL** database

### 3. Explore the dashboard

Open `http://localhost:3000` in your browser. Log in with the token you set in `.env`.

You'll see:

- **Dashboard overview** — agent activity, verification stats, cost tracking
- **Agents** — all registered agents with posture badges
- **Approvals** — held actions waiting for your review
- **ShadowEnforcer** — what agents would do vs what they're allowed to do
- **Bridges** — cross-functional team connections

---

## Option B: pip install (development)

### 1. Install the package

```bash
pip install care-platform
```

Or for development:

```bash
git clone https://github.com/terrene-foundation/care.git
cd care
pip install -e ".[dev]"
```

### 2. Run with demo data

```bash
python scripts/run_seeded_server.py
```

This seeds the platform with demo data (4 teams, 14 agents, 274 audits, 5 held actions, 4 bridges) and starts the API server at `http://localhost:8000`.

### 3. Explore the API

```bash
# Health check
curl http://localhost:8000/health

# List teams (requires auth)
curl -H "Authorization: Bearer demo" http://localhost:8000/api/v1/teams

# Verification gradient stats
curl -H "Authorization: Bearer demo" http://localhost:8000/api/v1/verification/stats

# Shadow metrics for an agent
curl -H "Authorization: Bearer demo" http://localhost:8000/api/v1/shadow/dm-team-lead/metrics
```

---

## Option C: CLI only

### 1. Create an organization

```bash
# List available templates
care-platform org list-templates

# Create from a template
care-platform org create --template media --name "My Media Team"

# Validate an organization
care-platform org validate
```

### 2. Check platform status

```bash
care-platform status
```

---

## What's Next

- **[Architecture](architecture.md)** — understand the trust model and constraint system
- **[REST API](rest-api.md)** — full endpoint reference
- **[Cookbook](cookbook.md)** — recipes for common tasks
- **[Python API](api.md)** — programmatic access to platform internals
