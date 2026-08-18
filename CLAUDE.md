# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A local full-stack Todo List app. Backend is FastAPI + SQLModel + SQLite (async), frontend is Vue 3 + Axios + Vite. Frontend dev server proxies `/api` to the backend on port 8000, so no CORS issues in dev.

The authoritative spec is `Plan.md` — when the doc and code diverge, the code is source of truth but note the spec was written against older dependency versions.

## Environment & running

All backend work runs in a dedicated conda env `todo` (Python 3.11). Reference it by explicit interpreter path, not `python` or `conda activate` (the latter doesn't persist across shell invocations here):

```bash
PY=/d/anaconda/envs/todo/python.exe

# Backend (must run from backend/ so `main` is importable)
cd backend
`$PY` -m pip install -r requirements.txt
`$PY` -m uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev        # serves http://localhost:5173
npm run build      # production build
```

Database is a local SQLite file `backend/todos.db` (gitignored; auto-created on startup via lifespan).

## Key non-obvious facts (verified)

- **`sqlmodel.ext.asyncio.engine` does NOT exist** in SQLModel 0.0.39. Create the async engine with SQLAlchemy:
  `from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker` and use `from sqlmodel.ext.asyncio.session import AsyncSession`. Do not follow old `create_async_engine` tutorial imports.
- **Verify routes via `/openapi.json`, not `app.routes`.** This FastAPI build (0.141.1) wraps included routers in an internal `_IncludedRouter` object, so `app.routes` won't show the todos paths even though they work. Hit `GET http://localhost:8000/openapi.json` to confirm registered endpoints.
- **Do not use curl for POST/PUT with a JSON body** on this setup — starlette's body parser rejects curl's body encoding on Windows ("error parsing the body"), while real clients work. Test writes with Python urllib or axios/fetch instead.
- Backend startup uses FastAPI `lifespan` (not the deprecated `@app.on_event`), and pydantic v2 `SettingsConfigDict` in `config.py`.

## Architecture (backend layer separation)

Strict layered separation — business rules live only in services, DB access only in repositories:

- `app/core/` — config (`Settings`), async engine/session + `get_db` dependency (`database.py`), custom exceptions.
- `app/models/` — SQLModel table models.
- `app/schemas/` — Pydantic request/response models (`TodoCreate`/`TodoUpdate`/`TodoResponse`).
- `app/repositories/` — pure CRUD against `AsyncSession`; no business logic.
- `app/services/` — business logic; raises `TodoNotFoundError` (→404) and `TodoTitleEmptyError` (→400).
- `app/api/v1/endpoints/` — FastAPI routes with `Depends(get_todo_service)`; catches the service exceptions and maps to HTTP status codes.
- `app/dependencies.py` — DI factory wiring a session to `TodoService`.
- `main.py` — app factory: CORS, lifespan init_db, router registration under `settings.API_V1_PREFIX`.

Note `app/core/database.py` exports `get_db`, but `app/dependencies.py` re-exports/wraps it — endpoint layer should depend on `get_todo_service`, not reach into core directly.

## API contract

`GET /api/v1/todos/` (list, ordered by `created_at` desc), `POST /api/v1/todos/` (create, 201), `PUT /api/v1/todos/{id}`, `DELETE /api/v1/todos/{id}` (204), `DELETE /api/v1/todos/` (clear completed), `GET /health`. Errors return `{"detail": ...}`.

## Frontend

Vanilla Vue 3 SFCs (`<script setup>`), no router/pinia. Structure:
- `src/api/axios.js` — axios instance (`baseURL: '/api/v1'`) with response interceptor that unwraps `error.response.data.detail`.
- `src/api/todos.js` — thin wrappers returning `res.data`.
- `src/components/TodoApp.vue` — all UI + interactions; parent `App.vue` renders only this.

`created_at` is stored as UTC; frontend currently displays it as-is.