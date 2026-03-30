# summaries-api

**Live API:** https://summaries-api-production-67c6.up.railway.app/docs

REST API that receives a URL and returns an AI-generated summary of its content. Built with FastAPI, PostgreSQL, and a multi-provider AI fallback chain.

---

## Motivation

Most AI integration tutorials wire the API call directly into the route handler. This project treats the AI provider as an external dependency — isolated behind an integration layer, swappable, and fault-tolerant. The goal was to build something that could survive a provider outage without the caller knowing.

---

## Architecture

The codebase follows a strict 6-layer architecture. Each layer has one responsibility and communicates only with its adjacent layers.

```
Request → Router → Service → Integration / Repository → DB
```

| Layer | Responsibility |
|---|---|
| `api/` | HTTP concerns: parsing, validation, response codes |
| `services/` | Business logic: orchestrates integration + persistence |
| `integrations/` | External API calls: AI providers, scrapers |
| `repositories/` | Database queries: no business logic |
| `models/` | SQLModel table definitions |
| `schemas/` | Pydantic request/response contracts |

The key architectural decision: the router passes the full schema to the service, not individual fields. This means adding a field to `SummaryCreate` requires touching one file, not three.

---

## AI Fallback Chain

Generating a summary is the core business operation. If the primary provider is unavailable, the API falls back automatically:

```
1. Claude Sonnet (Anthropic)   — primary
2. Claude Haiku (Anthropic)    — cheaper fallback
3. GPT-4o-mini (OpenAI)        — external fallback
4. 503 Service Unavailable     — all providers failed
```

Each attempt is logged independently. The caller receives either a completed summary or a clear error — never a silent `null`.

Implemented in `app/integrations/summarizer_client.py` using async coroutine factories so providers are only invoked when their turn comes, not all at once.

---

## Stack

- **FastAPI** — async web framework
- **SQLModel** — ORM with Pydantic integration
- **PostgreSQL** — primary database
- **Alembic** — schema migrations
- **JWT** — stateless authentication (`python-jose`)
- **Docker Compose** — local development environment
- **pytest + pytest-asyncio** — integration tests against a real test database

---

## Running locally

**Requirements:** Docker and Docker Compose.

```bash
git clone https://github.com/your-username/summaries-api
cd summaries-api
cp .env.example .env  # fill in your values
docker compose up
```

API available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | JWT signing key |
| `ANTHROPIC_API_KEY` | ✅ | Primary AI provider |
| `OPENAI_API_KEY` | ☐ | Fallback provider (optional) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ☐ | Default: 30 |

---

## Running tests

Tests run inside the container against an isolated test database. Migrations are applied automatically before each test session.

```bash
docker compose exec api uv run pytest tests/integration/ -v
```

12 integration tests covering auth and summary endpoints.

---

## API overview

Authentication uses JWT Bearer tokens. Obtain a token via `POST /api/v1/auth/login`, then include it as `Authorization: Bearer <token>` on protected endpoints.

The Swagger UI at `/docs` includes an **Authorize** button for testing authenticated endpoints directly.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | — | Create account |
| `POST` | `/api/v1/auth/login` | — | Obtain JWT |
| `POST` | `/api/v1/summaries/` | ✅ | Generate and store a summary |
| `GET` | `/api/v1/summaries/` | ✅ | List your summaries |
| `GET` | `/api/v1/summaries/{id}` | ✅ | Get a summary |
| `PATCH` | `/api/v1/summaries/{id}` | ✅ | Update a summary |
| `DELETE` | `/api/v1/summaries/{id}` | ✅ | Delete a summary |

---

## Project structure

```
app/
├── api/v1/endpoints/   # Route handlers
├── core/               # Config, security, JWT
├── db/                 # Session management
├── integrations/       # summarizer_client.py (fallback chain)
├── models/             # SQLModel table definitions
├── repositories/       # Database queries
├── schemas/            # Pydantic contracts
└── services/           # Business logic
migrations/             # Alembic migration files
tests/integration/      # End-to-end tests
```
