# Deploying Zoids League to a VPS (Docker + HTTPS)

Production deployment with Gunicorn, Nginx (reverse proxy + TLS), Let's Encrypt,
and PostgreSQL. The local `docker-compose.yml` is for development and is **not**
used here — production uses `docker-compose.prod.yml`.

## Architecture

```
Internet ── :443 Nginx (TLS) ── /        → React build (static)
                              ── /api/    → Gunicorn (Django)
                              ── /admin/  → Gunicorn (Django)
                              ── /static/ → Django collected static
            db (PostgreSQL, internal network only — no public port)
```

## Prerequisites

- A Contabo VPS with a public IP.
- A domain whose DNS **A record** (and `www`) points to the VPS IP.
- Docker Engine + the Compose plugin installed on the VPS.

Install Docker on a fresh Ubuntu VPS:

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # log out/in afterwards
```

## Step 1 — Get the code on the server

```bash
git clone https://github.com/JosefOreC/league
cd league
```

## Step 2 — Create the production .env

```bash
cp .env.example .env
nano .env
```

Fill in **real** values. Generate a fresh secret key:

```bash
docker run --rm python:3.12-slim python -c \
  "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(50)))"
```

Required: `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DB_PASSWORD`
(long and random — never `admin`), `DOMAIN`, `CERTBOT_EMAIL`,
`OPENROUTER_API_KEY`.

> The old `SECRET_KEY` that was committed in `settings.py` is considered
> **compromised**. Do not reuse it — generate a new one as above.

## Step 3 — Confirm DNS is pointing at the VPS

```bash
dig +short yourdomain.com    # must return your VPS IP
```

Wait until it resolves before requesting the certificate, or Let's Encrypt will
fail the challenge.

## Step 4 — Obtain the TLS certificate (one time)

```bash
chmod +x init-letsencrypt.sh entrypoint.prod.sh
./init-letsencrypt.sh
```

This boots Nginx with a temporary certificate, requests the real Let's Encrypt
certificate over HTTP, and reloads Nginx with it.

## Step 5 — Start the full stack

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

The backend automatically runs `migrate` and `collectstatic` on start.

## Step 6 — Create the Django admin user

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## Verify

```bash
docker compose -f docker-compose.prod.yml ps      # all services up
curl -I https://yourdomain.com                     # 200 + valid TLS
```

- App:   `https://yourdomain.com`
- API:   `https://yourdomain.com/api/`
- Admin: `https://yourdomain.com/admin/`

## Day-2 operations

| Task | Command |
|------|---------|
| View logs | `docker compose -f docker-compose.prod.yml logs -f backend` |
| Deploy new code | `git pull && docker compose -f docker-compose.prod.yml up -d --build` |
| Restart | `docker compose -f docker-compose.prod.yml restart` |
| Stop | `docker compose -f docker-compose.prod.yml down` |
| DB backup | `docker compose -f docker-compose.prod.yml exec db pg_dump -U $DB_USER $DB_NAME > backup.sql` |

TLS certificates renew automatically: the `certbot` service checks twice a day
and Nginx reloads every 6 hours to pick up renewed certs.

## Notes

- Keep ports **80** and **443** open in the Contabo firewall; **5432** must stay
  closed to the public.
- Static frontend assets are baked into the Nginx image at build time, with the
  API URL set to the same-origin `/api/` path (no CORS needed in production).
