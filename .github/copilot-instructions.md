# Copilot Instructions for emergent-1

## Architecture Overview
- **Backend**: FastAPI app in `backend/` with async endpoints using asyncpg for PostgreSQL/Supabase. Key files: `server.py`, `db.py`, `models/order.py`.
- **Frontend**: React app in `frontend/` (see `frontend/README.md`).
- **Services & Routers**: Business logic is split into `services/` and `routers/` for modularity.

## Backend Patterns & Conventions
- **Database Access**: Use `asyncpg` via `get_pg_pool()` in `db.py`. All queries are async and use SQL parameterization (e.g., `$1`, `$2`).
- **Models**: Pydantic models for request/response validation. SQLAlchemy table definitions exist for legacy, but asyncpg is preferred for queries.
- **Endpoints**: Define endpoints in `server.py` and `routers/`. Example:
  ```python
  @app.post("/orders/")
  async def create_order(order: Order):
      async with pg_pool.acquire() as conn:
          await conn.execute("INSERT INTO orders (token, status) VALUES ($1, $2)", order.token, order.status)
  ```
- **Startup/Shutdown**: Use FastAPI events to manage DB pool lifecycle.
- **Health Check**: `/health` endpoint runs a simple query to verify DB connection.

## Developer Workflows
- **Start Backend**: From `backend/`, run:
  ```bash
  uvicorn server:app --reload

  source env/bin/activate && python -m uvicorn server:app --reload
  ```
- **Install Dependencies**:
  ```bash
  pip install -r requirements.txt
  pip install asyncpg python-dotenv
  ```
- **Environment**: Set `DATABASE_URL` in `.env` (PostgreSQL/Supabase connection string).
- **Frontend**: From `frontend/`, use `npm start` for development.

## Integration Points
- **Supabase/PostgreSQL**: All persistent data is stored in PostgreSQL. Ensure tables exist before running endpoints.
- **Async Only**: All DB and endpoint code is async; avoid sync DB libraries.
- **Error Handling**: Use FastAPI's `HTTPException` for API errors.

## Project-Specific Notes
- **Table Creation**: Backend does not auto-create tables; use migrations or manual SQL.
- **Legacy SQLAlchemy**: Some files (e.g., `models/order.py`) have SQLAlchemy tables for reference, but asyncpg is the source of truth for queries.
- **Frontend/Backend Separation**: No direct coupling; communicate via REST endpoints.

## Example Files
- `backend/server.py`: Main FastAPI app and endpoints
- `backend/db.py`: Asyncpg pool setup
- `backend/models/order.py`: Pydantic models and legacy table definition

---
If any section is unclear or missing, please provide feedback for further refinement.
