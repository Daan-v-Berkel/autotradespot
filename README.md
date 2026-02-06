# AutoTradeSpot

AutoTradeSpot is a web application for listing cars for sale/lease. It combines a Django backend with HTMX/HyperScript-enhanced pages and React/Tailwind-based frontend components. The project is container-friendly via Docker Compose and can also be run locally for development.

## Table of Contents
- Features
- Tech stack
- Quickstart (Docker)
- Quickstart (Local / non-Docker)
- Tests
- Contributing

## Features

- Users: accounts, email confirmation, profiles, preferences, favorites and history.
- Listings: rich car data, images, favorites and owner contact.
- Admin: manual review workflow, hold/approve/decline listings, admin password reset/email actions.
- UI: light/dark mode, progressive enhancements via HTMX.

## Tech stack

- Backend: Django
- Frontend: HTMX + React + Tailwind CSS
- Dev tooling: Webpack, npm
- Infrastructure: Docker, docker-compose (see `local.yml`)

## Quickstart — Docker (recommended for local parity)

Prerequisites: Docker & Docker Compose.

Bring up the full local stack (Postgres, Django, etc.):

```bash
docker compose -f local.yml up -d
```

Apply migrations and create a dev superuser inside the `django` container:

```bash
docker compose -f local.yml exec django python manage.py migrate
docker compose -f local.yml exec django python manage.py createsuperuser
```
