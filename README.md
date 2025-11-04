# ITAM Chat Backend (FastAPI)

A FastAPI backend for a messenger app with JWT auth, user search, chat previews, chat contents, and real-time messaging via WebSockets. Fully containerized with Docker Compose and documented with Swagger.

## Features

- JWT auth with dev mode for infinite TTL
- Endpoints: `/register`, `/login`, `/search`, `/chats`, `/chats/{chat_id}`
- Pagination for search, chats, and messages
- WebSocket for sending/receiving messages and seen updates
- PostgreSQL + SQLAlchemy + Alembic
- Rich OpenAPI docs with examples

## Quick start

1. Copy env template and edit as needed:
   ```bash
   cp env.example .env
   ```
2. Build and run:
   ```bash
   docker compose up --build
   ```
3. Open docs:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Production hosting with Caddy (TLS on chat.salut.uno)

The stack includes a Caddy reverse proxy that terminates TLS for your domain and proxies to the FastAPI app.

1. Set domain and ACME email in `.env`:
   ```env
   DOMAIN=chat.salut.uno
   ACME_EMAIL=admin@example.com
   ```
2. Point your DNS A record for `chat.salut.uno` to your server's public IP and ensure ports 80 and 443 are open.
3. Start the stack:
   ```bash
   docker compose up --build -d
   ```
4. Access your API at `https://chat.salut.uno`.

Certificates are persisted across restarts via Docker volumes `caddy_data` and `caddy_config`, so Caddy won't re-request certificates on every run.

## Dev mode and JWT TTL

- Set `DEV=true` in `.env` to issue JWTs without expiration (`exp` omitted).
- Set `DEV=false` to enforce `JWT_EXPIRES_MINUTES`.

## Migrations

- On container start, Alembic runs `upgrade head` automatically.
- To create a new migration locally:
  ```bash
  docker compose run --rm app alembic revision --autogenerate -m "your message"
  docker compose run --rm app alembic upgrade head
  ```

## Project layout

```
app/
  core/
  db/
  models/
  routers/
  schemas/
  utils/
  main.py
alembic/
Dockerfile
docker-compose.yml
requirements.txt
```

## Notes

- For production, set a strong `JWT_SECRET` and `DEV=false`.
- WebSocket URL: `ws://localhost:8000/ws/chats/{chat_id}?token=YOUR_JWT`.
