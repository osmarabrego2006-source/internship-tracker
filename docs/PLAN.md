# Build Plan

Target: trimmed MVP by Oct 31, 2026. Checkpoint Oct 15: if the API isn't done, fall back to the Dec 6 timeline.
Update the checkboxes at the end of every session.

## Current status
- Phase 0 nearly done (Sep 30, one session). Postgres runs in Docker, server/ is set up, and GET /api/health returns 200 after SELECT 1.
- Host port is 5433, not 5432: a native Windows Postgres 18 service (postgresql-x64-18) holds 5432.
- Next: Vite scaffold in client/ (~15 min), then optional 503 + connect_timeout on /api/health, then Phase 1 migration.

## Phase 0: Setup (Sep 30 – Oct 4)
- [x] Install Python 3.12+, uv, Node 22+, Docker Desktop, Git
- [x] GitHub repo, .gitignore, .env.example, .env
- [x] docker-compose.yml with postgres:16, named volume, host port 5433 -> container 5432
- [ ] Vite React scaffold in client/
- [x] server/: uv init, add fastapi uvicorn "psycopg[binary,pool]" pydantic-settings alembic; dev: pytest httpx ruff
- [x] GET /api/health runs SELECT 1 (Osmar writes this)
- [ ] CLAUDE.md, LEARNING_LOG.md, first commit

Checkpoint: `docker compose up -d` runs, /api/health returns ok, Vite page loads.

## Phase 1: Database (Oct 1 – Oct 3)
- [ ] Alembic migration 001: full schema below, raw SQL in op.execute (Osmar writes)
- [ ] seed.sql with real applications + stage histories
- [ ] Funnel and stale queries run by hand in psql

Checkpoint: both queries return sensible results.

## Phase 2: API (Oct 4 – Oct 15)
- [ ] app/db.py: ConnectionPool + get_conn dependency
- [ ] Applications CRUD (Osmar writes), then the transactional stage endpoint (Osmar writes)
- [ ] Companies, contacts, tasks routes (Claude may draft from Osmar's pattern)
- [ ] /api/stats/funnel and /api/stats/summary
- [ ] pytest + TestClient: create, stage change (incl. 404 + no stray event), stats

Checkpoint: every endpoint works from /docs and `uv run pytest` passes.

## Phase 3: React UI, trimmed (Oct 16 – Oct 28)
- [ ] Router, layout shell, TanStack Query provider
- [ ] Applications list page with filters and search
- [ ] Detail page with stage dropdown and timeline
- [ ] Create/edit form with validation

Checkpoint: log a real application and move one to OA without touching SQL.

## Phase 4: CI + README (Oct 29 – Oct 31)
- [ ] Ruff on server/, ESLint on client/
- [ ] GitHub Actions: Postgres service, alembic upgrade head, pytest, client build
- [ ] README: screenshot, schema diagram, run in 3 commands

## Pushed to November
- Dashboard (stat cards, funnel chart), Companies & Contacts page, loading/empty/error polish
- Optional: deploy a demo copy with fake data, deadline reminders, analytics page

## Schema reference
Tables: companies, applications, stage_events, contacts, tasks.
- Enum app_stage: wishlist, applied, oa, phone_screen, interview, final_round, offer, accepted, rejected, withdrawn, ghosted
- applications: company_id FK, role_title, req_id, posting_url, location, season, current_stage, applied_on, deadline, priority 1-3, notes, created_at, updated_at
- stage_events: application_id FK, stage, occurred_on, note (the log is the source of truth)
- contacts: company_id FK, name, role, email, linkedin, notes
- tasks: application_id FK nullable, title, due_on, done
- Indexes: applications(current_stage), applications(deadline), stage_events(application_id, occurred_on), tasks(due_on) WHERE NOT done
- All FKs ON DELETE CASCADE

Rule: a stage change updates applications.current_stage AND inserts a stage_events row in ONE transaction. Update first; if no row, 404 (rolls back).

## API reference
| Method | Path | Does |
| --- | --- | --- |
| GET | /api/applications?stage=&q=&sort= | List, joined with company name |
| POST | /api/applications | Create (upsert company, first stage event) |
| GET | /api/applications/{id} | One app with events, tasks, contacts |
| PATCH | /api/applications/{id} | Edit fields (not stage) |
| DELETE | /api/applications/{id} | Delete (cascades) |
| POST | /api/applications/{id}/stage | Transactional stage change |
| GET/POST/PATCH/DELETE | /api/companies | Companies |
| GET/POST | /api/contacts | Contacts, filter by company_id |
| GET/POST/PATCH | /api/tasks | Tasks, ?due=week |
| GET | /api/stats/funnel, /api/stats/summary | Dashboard numbers |
