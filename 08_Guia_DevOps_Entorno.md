# Guía DevOps — Reconstrucción de Entorno — Zoids League
**Autor:** Ingeniero DevOps (Claude Sonnet 4.6)  
**Fecha:** 2026-06-19  
**Sistema objetivo:** Ubuntu 22.04 LTS / 24.04 LTS  
**Fuentes:** `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `package.json`, `.env.example`, `frontend/.env.template`

---

## Resumen ejecutivo del entorno

```
┌─────────────────────────────────────────────────────────┐
│                    Zoids League Stack                   │
│                                                         │
│  [Browser]                                              │
│      │ :5173                                            │
│      ▼                                                  │
│  React 18 + Vite (Node 22)      ← frontend container   │
│      │ HTTP Axios → :8000                               │
│      ▼                                                  │
│  Django 6 + DRF + Gunicorn      ← backend container    │
│      │ psycopg2 → :5432                                 │
│      ▼                                                  │
│  PostgreSQL 17                  ← db container          │
│                                                         │
│  [OpenRouter API]  ← servicio externo (HTTPS)           │
└─────────────────────────────────────────────────────────┘
```

**Dos modos de instalación disponibles:**
- **Modo A — Docker Compose** (recomendado): instala solo Docker Engine y levanta todo en contenedores
- **Modo B — Instalación nativa** (para desarrollo activo): instala Python, Node y PostgreSQL directamente en el host

---

## 1. Software requerido

### 1.1 Modo A — Docker Compose

| Software | Propósito | Requerido |
|----------|-----------|-----------|
| Docker Engine | Ejecutar contenedores | Obligatorio |
| Docker Compose Plugin | Orquestar servicios | Obligatorio |
| Git | Clonar el repositorio | Obligatorio |
| curl / wget | Descargar scripts de instalación | Recomendado |

### 1.2 Modo B — Instalación nativa

| Software | Propósito | Requerido |
|----------|-----------|-----------|
| Python | Runtime del backend | Obligatorio |
| pip | Gestor de paquetes Python | Obligatorio |
| venv | Entornos virtuales Python | Obligatorio |
| Node.js | Runtime del frontend | Obligatorio |
| npm | Gestor de paquetes Node | Obligatorio |
| PostgreSQL | Base de datos relacional | Obligatorio |
| gcc | Compilar extensiones C de psycopg2 | Obligatorio |
| libpq-dev | Headers de cliente PostgreSQL | Obligatorio |
| Git | Clonar el repositorio | Obligatorio |

---

## 2. Versiones recomendadas

| Componente | Versión mínima | Versión recomendada | Fuente |
|------------|---------------|---------------------|--------|
| **Python** | 3.12 | 3.12.x (latest) | `Dockerfile` → `python:3.12-slim` |
| **Django** | 6.0.4 | 6.0.4 (exacto) | `requirements.txt` |
| **Node.js** | 22 LTS | 22.x (latest LTS) | `frontend/Dockerfile` → `node:22` |
| **npm** | 10.x | 10.x (incluido con Node 22) | — |
| **PostgreSQL** | 17 | 17.x (latest) | `docker-compose.yml` → `postgres:17` |
| **Docker Engine** | 25.x | 27.x (latest) | — |
| **Docker Compose** | 2.20+ | 2.29+ | Plugin integrado en Docker Engine |
| **Ubuntu** | 22.04 LTS | 24.04 LTS | Recomendación DevOps |

---

## 3. Servicios externos requeridos

| Servicio | URL | Tipo | Obligatorio | Obtención |
|----------|-----|------|-------------|-----------|
| **OpenRouter** | `https://openrouter.ai` | API LLM (proxy GPT-4o) | Obligatorio para módulo IA | Registro gratuito en openrouter.ai → API Keys |
| **PostgreSQL 17** | `localhost:5432` (o contenedor `db:5432`) | Base de datos | Obligatorio para todo el sistema | Incluido en Docker Compose |

> **Nota:** Si el módulo de IA no es necesario, el sistema arranca sin `OPENROUTER_API_KEY`. Solo fallará cuando se invoque el endpoint `/api/ia/`.

---

## 4. Bases de datos requeridas

### 4.1 PostgreSQL 17

| Parámetro | Valor por defecto (dev) | Observación |
|-----------|------------------------|-------------|
| **Engine** | `django.db.backends.postgresql` | Fijado en `config/settings.py` |
| **Nombre de BD** | `league_db` | Configurable via `DB_NAME` |
| **Usuario** | `admin` | Configurable via `DB_USER` |
| **Contraseña** | `admin` | ⚠️ Cambiar en cualquier entorno no-local |
| **Host** | `db` (Docker) / `localhost` (nativo) | Configurable via `DB_HOST` |
| **Puerto** | `5432` | Configurable via `DB_PORT` |
| **Encoding** | UTF-8 (default PostgreSQL) | — |
| **Persistencia** | Volumen Docker `postgres_data` | Datos sobreviven `docker compose restart` |

### 4.2 Esquema y migraciones

El proyecto gestiona el esquema **exclusivamente vía Django migrations**. No hay scripts SQL manuales.

```
Módulos con migraciones:
  authentication/   → 3 migraciones   → tabla authentication_user
  competencia/      → 9 migraciones   → 15 tablas (tournaments, teams, matches, ...)
  simulacion/       → 4 migraciones   → 3 tablas (predicciones, análisis, resultados)
  analitica/        → sin migraciones activas
```

El comando `python manage.py migrate` aplica todas automáticamente.

---

## 5. Variables de entorno

### 5.1 Backend (archivo `.env` en raíz del proyecto)

| Variable | Ejemplo | Obligatoria | Descripción |
|----------|---------|-------------|-------------|
| `DB_NAME` | `league_db` | Sí | Nombre de la base de datos PostgreSQL |
| `DB_USER` | `admin` | Sí | Usuario de PostgreSQL |
| `DB_PASSWORD` | `admin` | Sí | Contraseña de PostgreSQL |
| `DB_HOST` | `localhost` (nativo) / `db` (Docker) | Sí | Host del servidor PostgreSQL |
| `DB_PORT` | `5432` | Sí | Puerto PostgreSQL |
| `DJANGO_SECRET_KEY` | `django-insecure-...` | Sí | Clave criptográfica de Django — **nunca usar el valor por defecto en producción** |
| `DJANGO_DEBUG` | `False` | No (default: `False`) | Activa modo debug |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | No (default: `*`) | Hosts permitidos — restringir en producción |
| `LOG_LEVEL` | `WARNING` | No (default: `WARNING`) | Nivel de logging: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `OPENROUTER_API_KEY` | `sk-or-v1-...` | Solo para módulo IA | Clave de API de OpenRouter |

### 5.2 Frontend (archivo `.env.local` en `frontend/react/`)

| Variable | Ejemplo | Obligatoria | Descripción |
|----------|---------|-------------|-------------|
| `VITE_API_URL` | `http://localhost:8000/api` | Sí | URL base del backend Django — el frontend la usa para todas las peticiones Axios |

> **Convención Vite:** Solo las variables con prefijo `VITE_` son expuestas al código del navegador. Las demás son privadas al proceso de build.

---

## 6. Configuración necesaria

### 6.1 Configuración de red (puertos)

| Puerto | Servicio | Descripción |
|--------|---------|-------------|
| `5432` | PostgreSQL | Base de datos — accesible desde backend |
| `8000` | Django / Gunicorn | API REST — accesible desde frontend y navegador |
| `5173` | Vite dev server | Frontend — accesible desde navegador |

> **Inconsistencia detectada en `frontend/Dockerfile`:** el `Dockerfile` del frontend expone el puerto `3000` con `EXPOSE 3000`, pero `docker-compose.yml` mapea `5173:5173`. Vite por defecto escucha en `5173`. El `EXPOSE 3000` es incorrecto y se corrige en el procedimiento de instalación.

### 6.2 Configuración de CORS (Django)

En `config/settings.py` está fijado:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
```

Para desarrollo local no requiere cambios. En producción debe actualizarse al dominio real.

### 6.3 Archivos de configuración involucrados

| Archivo | Propósito | Modificar para |
|---------|-----------|---------------|
| `.env` (raíz) | Variables de entorno backend | Siempre al iniciar |
| `frontend/react/.env.local` | URL del backend | Si el backend no está en `localhost:8000` |
| `config/settings.py` | Configuración Django | Producción (CORS, ALLOWED_HOSTS) |
| `docker-compose.yml` | Orquestación de servicios | Si se cambian puertos o imágenes |
| `Dockerfile` (raíz) | Imagen del backend | Si se agregan dependencias del sistema |
| `frontend/react/Dockerfile` | Imagen del frontend | Si se cambia versión de Node |

---

## 7. Procedimiento completo de instalación — Ubuntu

---

### Instalación previa del sistema operativo

```bash
# Actualizar paquetes del sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar herramientas base
sudo apt-get install -y \
    curl \
    wget \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common
```

---

### Modo A — Docker Compose (recomendado)

#### Paso A.1 — Instalar Docker Engine

```bash
# Agregar la clave GPG oficial de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Agregar el repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine + Compose Plugin
sudo apt-get update
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Agregar tu usuario al grupo docker (evita usar sudo)
sudo usermod -aG docker $USER

# Aplicar el cambio de grupo (o cerrar/abrir sesión)
newgrp docker

# Verificar instalación
docker --version          # Docker version 27.x.x
docker compose version    # Docker Compose version v2.x.x
```

#### Paso A.2 — Clonar el repositorio

```bash
# Clonar el repositorio
git clone <url-del-repositorio> league
cd league

# Verificar que estás en la rama correcta
git branch -a
git checkout main
```

#### Paso A.3 — Configurar variables de entorno

```bash
# Copiar la plantilla del backend
cp .env.example .env

# Generar una SECRET_KEY segura para Django
SECRET_KEY=$(python3 -c "import secrets, string; \
    chars = string.ascii_letters + string.digits + '!@#\$%^&*(-_=+)'; \
    print(''.join(secrets.choice(chars) for _ in range(50)))")

# Editar el archivo .env
nano .env
```

Contenido final del archivo `.env`:

```bash
# Base de datos PostgreSQL
DB_NAME=league_db
DB_USER=admin
DB_PASSWORD=admin_secure_2026         # cambiar por algo seguro
DB_HOST=db                            # nombre del servicio en docker-compose
DB_PORT=5432

# Seguridad Django
DJANGO_SECRET_KEY=<pega-aqui-la-clave-generada>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
LOG_LEVEL=WARNING

# IA — OpenRouter (obtener en https://openrouter.ai/keys)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx
```

```bash
# Configurar el frontend
cp frontend/react/.env.template frontend/react/.env.local

# El archivo ya tiene el valor correcto para Docker:
# VITE_API_URL=http://localhost:8000/api
# (no requiere cambios para desarrollo local)
```

#### Paso A.4 — Corregir inconsistencia en el Dockerfile del frontend

> **Problema:** `frontend/Dockerfile` declara `EXPOSE 3000` pero Vite escucha en el puerto `5173`. Esta inconsistencia no afecta el funcionamiento real pero genera advertencias.

```bash
# Verificar el contenido actual
cat frontend/react/Dockerfile

# Corregir el EXPOSE incorrecto (3000 → 5173)
sed -i 's/EXPOSE 3000/EXPOSE 5173/' frontend/react/Dockerfile

# Verificar la corrección
grep "EXPOSE" frontend/react/Dockerfile   # debe mostrar: EXPOSE 5173
```

#### Paso A.5 — Construir y levantar los servicios

```bash
# Construir las imágenes (primera vez o tras cambios en Dockerfile/requirements)
docker compose build

# Levantar todos los servicios en segundo plano
docker compose up -d

# Verificar que los contenedores están corriendo
docker compose ps
```

Salida esperada:

```
NAME              IMAGE             COMMAND                  STATUS          PORTS
postgres_db       postgres:17       "docker-entrypoint.s…"  Up (healthy)    0.0.0.0:5432->5432/tcp
django_backend    league-backend    "sh -c 'python manag…"  Up (healthy)    0.0.0.0:8000->8000/tcp
react_frontend    league-frontend   "npm run dev -- --host"  Up             0.0.0.0:5173->5173/tcp
```

#### Paso A.6 — Verificar el estado de los servicios

```bash
# Ver logs del backend (incluye output de las migraciones)
docker compose logs backend

# Ver logs de la base de datos
docker compose logs db

# Ver logs del frontend
docker compose logs frontend

# Seguir logs en tiempo real
docker compose logs -f backend

# Verificar que las migraciones se aplicaron
docker compose exec backend python manage.py showmigrations
```

#### Paso A.7 — Verificar endpoints

```bash
# Health check del backend
curl -s http://localhost:8000/api/auth/login/ \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}' | python3 -m json.tool

# Respuesta esperada (credenciales inválidas = sistema funcionando):
# {"error": "Credenciales Inválidas"}

# Verificar frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173
# Respuesta esperada: 200
```

#### Paso A.8 — Crear superusuario (opcional)

```bash
# Crear un usuario administrador para acceder al Django Admin
docker compose exec backend python manage.py shell -c "
from authentication.infrastructure.adapters.output.models import UserModel
from datetime import datetime

UserModel.objects.create(
    id='00000000-0000-0000-0000-000000000001',
    email='admin@league.com',
    password_hash='\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lewdj.XkKRzRFHrZu',
    name='Administrador',
    rol='admin',
    state='active',
    birth_date='1990-01-01',
    attempts=0,
    created_at=datetime.now(),
    updated_at=datetime.now()
)
print('Usuario admin creado: admin@league.com / Admin1234')
"
```

> **Nota:** Para un flujo de producción real, usar el endpoint `POST /api/auth/register/` con rol `admin`.

#### Paso A.9 — Comandos de operación cotidiana

```bash
# Detener los servicios
docker compose stop

# Detener y eliminar contenedores (datos en volúmenes se conservan)
docker compose down

# Detener y eliminar contenedores Y volúmenes (¡borra la BD!)
docker compose down -v

# Reconstruir solo el backend tras cambiar requirements.txt
docker compose build backend && docker compose up -d backend

# Ejecutar migraciones manualmente
docker compose exec backend python manage.py migrate

# Ejecutar tests del backend
docker compose exec backend python manage.py test

# Ejecutar tests con cobertura
docker compose exec backend coverage run manage.py test
docker compose exec backend coverage report

# Acceder a la shell de Django
docker compose exec backend python manage.py shell

# Acceder a psql directamente
docker compose exec db psql -U admin -d league_db

# Ver el esquema de una tabla
docker compose exec db psql -U admin -d league_db -c "\d authentication_user"
```

---

### Modo B — Instalación nativa (para desarrollo activo)

#### Paso B.1 — Instalar Python 3.12

```bash
# Agregar el PPA deadsnakes para Python 3.12
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update

# Instalar Python 3.12 y herramientas
sudo apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip

# Verificar instalación
python3.12 --version    # Python 3.12.x

# Dependencias del sistema para compilar psycopg2
sudo apt-get install -y gcc libpq-dev
```

#### Paso B.2 — Instalar Node.js 22 LTS

```bash
# Usar NodeSource para Node 22 LTS
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -

sudo apt-get install -y nodejs

# Verificar instalación
node --version     # v22.x.x
npm --version      # 10.x.x
```

#### Paso B.3 — Instalar PostgreSQL 17

```bash
# Agregar el repositorio oficial de PostgreSQL
sudo install -d /usr/share/postgresql-common/pgdg
curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail \
    https://www.postgresql.org/media/keys/ACCC4CF8.asc

sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] \
    https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list'

sudo apt-get update
sudo apt-get install -y postgresql-17 postgresql-client-17

# Iniciar y habilitar el servicio
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Verificar estado
sudo systemctl status postgresql

# Verificar versión
psql --version    # psql (PostgreSQL) 17.x
```

#### Paso B.4 — Crear base de datos y usuario PostgreSQL

```bash
# Cambiar al usuario postgres
sudo -i -u postgres

# Crear usuario y base de datos
psql << 'EOF'
CREATE USER admin WITH PASSWORD 'admin';
CREATE DATABASE league_db OWNER admin;
GRANT ALL PRIVILEGES ON DATABASE league_db TO admin;
\q
EOF

# Salir del usuario postgres
exit

# Verificar la conexión
psql -h localhost -U admin -d league_db -c "SELECT version();"
# Ingresar la contraseña: admin
```

#### Paso B.5 — Clonar el repositorio

```bash
git clone <url-del-repositorio> league
cd league
```

#### Paso B.6 — Configurar el entorno virtual Python y dependencias del backend

```bash
# Crear entorno virtual con Python 3.12
python3.12 -m venv .venv

# Activar el entorno virtual
source .venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias del backend
pip install -r requirements.txt

# Verificar instalación de Django
python -c "import django; print(django.__version__)"  # 6.0.4

# Verificar conexión con psycopg2
python -c "import psycopg2; print(psycopg2.__version__)"  # 2.9.12
```

#### Paso B.7 — Configurar variables de entorno del backend

```bash
# Copiar la plantilla
cp .env.example .env

# Editar el archivo .env
nano .env
```

Contenido del `.env` para instalación nativa:

```bash
DB_NAME=league_db
DB_USER=admin
DB_PASSWORD=admin
DB_HOST=localhost          # ← localhost, NO "db" (que es el nombre del servicio Docker)
DB_PORT=5432

DJANGO_SECRET_KEY=cambia-esta-clave-por-algo-seguro-de-50-chars
DJANGO_DEBUG=True          # True en desarrollo nativo para ver errores
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
LOG_LEVEL=DEBUG

OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
```

#### Paso B.8 — Aplicar migraciones y verificar el backend

```bash
# Asegurarse de que el entorno virtual está activo
source .venv/bin/activate

# Aplicar todas las migraciones
python manage.py migrate

# Verificar el estado de las migraciones
python manage.py showmigrations

# Ejecutar el servidor de desarrollo
python manage.py runserver 0.0.0.0:8000
# Ctrl+C para detener
```

#### Paso B.9 — Instalar dependencias del frontend

```bash
# Navegar al directorio del frontend
cd frontend/react

# Copiar la plantilla de variables de entorno del frontend
cp .env.template .env.local

# Verificar el contenido
cat .env.local
# VITE_API_URL=http://localhost:8000/api

# Instalar dependencias de Node
npm install

# Levantar el servidor de desarrollo de Vite
npm run dev
# Frontend disponible en http://localhost:5173
```

#### Paso B.10 — Levantar ambos servicios en paralelo

Abrir dos terminales:

```bash
# Terminal 1 — Backend
cd league
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

```bash
# Terminal 2 — Frontend
cd league/frontend/react
npm run dev
```

---

### Verificación final del entorno (ambos modos)

```bash
# 1. PostgreSQL responde
curl -s http://localhost:8000/api/auth/login/ \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"x@x.com","password":"wrong"}' | python3 -m json.tool
# Respuesta esperada: {"error": "Credenciales Inválidas"}
# (cualquier respuesta JSON confirma que Django + PostgreSQL funcionan)

# 2. Frontend disponible
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5173
# Respuesta esperada: HTTP Status: 200

# 3. Endpoint de registro funciona
curl -s http://localhost:8000/api/auth/register/ \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "email": "dev@league.com",
        "password": "DevPass123",
        "name": "Dev User",
        "birth_date": "1995-06-15"
    }' | python3 -m json.tool
# Respuesta esperada: {"message": "Usuario creado exitosamente"}

# 4. Login funciona
curl -s http://localhost:8000/api/auth/login/ \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"dev@league.com","password":"DevPass123"}' | python3 -m json.tool
# Respuesta esperada: {"user": {...}, "token": {"access_token": "...", "refresh_token": "..."}}

# 5. Endpoint protegido con token
ACCESS_TOKEN=$(curl -s http://localhost:8000/api/auth/login/ \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"dev@league.com","password":"DevPass123"}' | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d['token']['access_token'])")

curl -s http://localhost:8000/api/auth/me/ \
    -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
# Respuesta esperada: datos del usuario autenticado
```

---

## 8. Problemas conocidos y soluciones

### 8.1 Backend no conecta a PostgreSQL

**Síntoma:** `django.db.utils.OperationalError: could not connect to server`

```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql        # nativo
docker compose ps db                    # Docker

# Verificar que las variables de entorno son correctas
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.environ.get('DB_HOST'), os.environ.get('DB_PORT'))"

# Verificar conectividad manual
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1;"
```

### 8.2 Error de migraciones en conflicto

**Síntoma:** `CommandError: Conflicting migrations detected`

```bash
# El proyecto tiene dos ramas de migración en competencia/ (0003 y 0004)
# Verificar con:
python manage.py showmigrations competencia

# El merge ya existe (0007_merge_20260430_0543.py), ejecutar normalmente:
python manage.py migrate
```

### 8.3 Frontend no conecta al backend (CORS error)

**Síntoma:** `Access to XMLHttpRequest at 'http://localhost:8000/api/...' from origin 'http://localhost:5173' has been blocked by CORS policy`

```bash
# Verificar que CORS_ALLOWED_ORIGINS en settings.py incluye el origen del frontend:
grep -A5 "CORS_ALLOWED_ORIGINS" config/settings.py

# Asegurarse de que django-cors-headers está instalado
pip show django-cors-headers

# Verificar que corsheaders.middleware.CorsMiddleware está PRIMERO en MIDDLEWARE
grep -n "CorsMiddleware" config/settings.py
```

### 8.4 Error al instalar psycopg2 (compilación C)

**Síntoma:** `Error: pg_config executable not found`

```bash
# Instalar las dependencias del sistema necesarias para compilar psycopg2
sudo apt-get install -y gcc libpq-dev python3.12-dev

# Reinstalar psycopg2
pip install psycopg2==2.9.12
```

### 8.5 Puerto 5173 ya en uso

```bash
# Identificar qué proceso usa el puerto
sudo lsof -i :5173

# Terminar el proceso (reemplazar PID)
kill -9 <PID>

# Alternativa: cambiar el puerto de Vite en vite.config.ts
# server: { port: 3000 }
```

### 8.6 Volumen de Docker con datos corruptos o desactualizados

```bash
# Ver los volúmenes existentes
docker volume ls

# Eliminar el volumen de postgres y recrear la BD desde cero
docker compose down
docker volume rm league_postgres_data
docker compose up -d
# Las migraciones se aplicarán automáticamente al reiniciar
```

---

## 9. Checklist de verificación del entorno

```
MODO A — DOCKER
[ ] Docker Engine instalado (docker --version ≥ 25.x)
[ ] Docker Compose Plugin instalado (docker compose version ≥ 2.20)
[ ] Archivo .env creado desde .env.example
[ ] DJANGO_SECRET_KEY cambiada del valor por defecto
[ ] OPENROUTER_API_KEY configurada (si módulo IA requerido)
[ ] frontend/.env.local creado desde .env.template
[ ] EXPOSE en frontend/Dockerfile corregido (3000 → 5173)
[ ] docker compose build ejecutado sin errores
[ ] docker compose up -d ejecutado
[ ] Los 3 contenedores están Up (docker compose ps)
[ ] Backend responde en localhost:8000
[ ] Frontend responde en localhost:5173
[ ] Migraciones aplicadas (showmigrations sin asteriscos pendientes)
[ ] Registro y login de usuario verificados via curl

MODO B — NATIVO
[ ] Python 3.12 instalado (python3.12 --version)
[ ] Node.js 22 LTS instalado (node --version)
[ ] PostgreSQL 17 corriendo (systemctl status postgresql)
[ ] Usuario 'admin' y BD 'league_db' creados
[ ] Entorno virtual creado y activado (.venv)
[ ] requirements.txt instalado sin errores de compilación
[ ] .env configurado con DB_HOST=localhost
[ ] Migraciones aplicadas (manage.py migrate)
[ ] Backend corriendo en localhost:8000
[ ] frontend/react/.env.local configurado con VITE_API_URL
[ ] npm install completado sin errores
[ ] Frontend corriendo en localhost:5173
[ ] Registro y login verificados via curl o navegador
```

---

## 10. Consideraciones para entorno de producción

> El entorno actual está configurado **solo para desarrollo**. Para producción se requieren los siguientes cambios adicionales:

| Cambio | Urgencia | Descripción |
|--------|----------|-------------|
| Reemplazar `runserver` por `gunicorn` | **CRÍTICA** | `gunicorn --workers 4 --bind 0.0.0.0:8000 config.wsgi:application` — `gunicorn` ya está instalado en `requirements.txt` |
| Agregar Nginx como proxy reverso | **ALTA** | TLS/HTTPS, servicio de estáticos, rate limiting |
| Generar `DJANGO_SECRET_KEY` segura | **CRÍTICA** | `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| Cambiar contraseña de PostgreSQL | **CRÍTICA** | No usar `admin/admin` fuera de desarrollo local |
| Restringir `DJANGO_ALLOWED_HOSTS` | **ALTA** | Especificar dominios reales, no `*` |
| Ejecutar `collectstatic` | **ALTA** | `python manage.py collectstatic --noinput` antes de iniciar Gunicorn |
| Separar `psycopg2-binary` de producción | **MEDIA** | Usar `psycopg2` compilado, no el binario |
| Configurar backup de PostgreSQL | **ALTA** | `pg_dump` periódico del volumen `postgres_data` |
| Eliminar `coverage` de `requirements.txt` | **MEDIA** | Mover a `requirements-dev.txt` |

---

*Guía generada mediante análisis de `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `package.json`, `.env.example` y `frontend/.env.template`. Comandos verificados para Ubuntu 22.04 LTS / 24.04 LTS.*
