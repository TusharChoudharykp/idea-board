# Idea Board

A full-stack idea-sharing application built for the Halcer DevOps case study.

## Stack
- React + TypeScript + Vite frontend
- Python FastAPI backend
- PostgreSQL database
- Docker and Docker Compose

## Run locally with Docker Compose

Requirements: Docker Desktop (or Docker Engine) with the Compose plugin.

```bash
docker compose up --build -d
```

Open:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health endpoint: http://localhost:8000/health

Stop the application:

```bash
docker compose down
```

Stop and remove the local database volume (this permanently deletes saved ideas):

```bash
docker compose down -v
```

## API

### GET /api/ideas
Returns all ideas as a JSON array.

### POST /api/ideas
Request:

```json
{"content": "My new idea"}
```

The API stores the idea in PostgreSQL and returns the created record.

## Database

The backend creates the required `ideas` table on startup:

| Column | Type |
|---|---|
| id | integer, primary key |
| content | varchar/text |
| created_at | timestamp with time zone |

## Current scope

This initial milestone implements the requested app and local container setup. Terraform, Kubernetes, two-cloud deployment, and the AI-powered CI/CD workflow will be added as subsequent case-study milestones.
