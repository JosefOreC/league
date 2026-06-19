# Auditoría de Configuración — Zoids League
**Auditor:** Ingeniero de Configuración / Seguridad (Claude Sonnet 4.6)  
**Fecha:** 2026-06-19  
**Archivos analizados:**
- `d:\league\.env.example`
- `d:\league\frontend\react\.env.template`
- `d:\league\config\settings.py`
- `d:\league\docker-compose.yml`
- `d:\league\Dockerfile`
- `d:\league\frontend\react\Dockerfile`
- `d:\league\authentication\application\service\jwt_service.py`
- `d:\league\authentication\infrastructure\security\auth_decorator.py`
- `d:\league\frontend\react\src\services\api.ts`
- `d:\league\simulacion\infrastructure\ml\xgboost_adapter.py`
- `d:\league\.coveragerc`

---

## 1. Tabla maestra de variables de configuración

### 1.1 Backend — Variables de entorno (`.env.example` + `settings.py`)

| Variable | Obligatoria | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|-------------|-----------------|--------|
| `DB_NAME` | ✅ Sí | Nombre de la base de datos PostgreSQL | `league_db` | `.env.example` |
| `DB_USER` | ✅ Sí | Usuario de conexión PostgreSQL | `admin` | `.env.example` |
| `DB_PASSWORD` | ✅ Sí | Contraseña del usuario PostgreSQL | `s3cur3P@ss!` | `.env.example` |
| `DB_HOST` | ✅ Sí | Host del servidor PostgreSQL. `db` en Docker, `localhost` en nativo | `db` / `localhost` | `.env.example` |
| `DB_PORT` | ✅ Sí | Puerto TCP de PostgreSQL | `5432` | `.env.example` |
| `DJANGO_SECRET_KEY` | ✅ Sí | Clave criptográfica de Django. Usada para JWT, cookies, CSRF. Mínimo 50 caracteres | `django-^abc123...XYZ!@#$` | `.env.example` |
| `DJANGO_DEBUG` | ⚠️ No | Activa el modo debug de Django. Nunca `True` en producción | `False` | `.env.example` |
| `DJANGO_ALLOWED_HOSTS` | ⚠️ No | Lista de hosts permitidos separada por comas. `*` solo aceptable en desarrollo local | `localhost,127.0.0.1` | `.env.example` |
| `LOG_LEVEL` | ⚠️ No | Nivel de logging: `DEBUG`, `INFO`, `WARNING`, `ERROR` | `WARNING` | `.env.example` |
| `OPENROUTER_API_KEY` | ⚠️ Condicional | Clave de API de OpenRouter. Obligatoria si se usa el módulo IA (`/api/ia/`) | `sk-or-v1-xxxxxxxx` | `.env.example` |

### 1.2 Frontend — Variables de entorno (`.env.template` / Vite)

| Variable | Obligatoria | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|-------------|-----------------|--------|
| `VITE_API_URL` | ✅ Sí | URL base del backend Django. Prefijo `VITE_` requerido por Vite para exponer al navegador | `http://localhost:8000/api` | `.env.template` |

### 1.3 Docker Compose — Variables de entorno de contenedores

| Variable | Contenedor | Obligatoria | Descripción | Valor declarado en compose | Problema |
|----------|-----------|-------------|-------------|--------------------------|---------|
| `POSTGRES_DB` | `db` | ✅ Sí | Nombre de la BD que PostgreSQL crea al iniciar | `league_db` (hardcoded) | ⚠️ No usa variable de entorno del host |
| `POSTGRES_USER` | `db` | ✅ Sí | Usuario inicial de PostgreSQL | `admin` (hardcoded) | ⚠️ No usa variable de entorno del host |
| `POSTGRES_PASSWORD` | `db` | ✅ Sí | Contraseña del usuario inicial | `admin` (hardcoded) | 🔴 Contraseña débil hardcodeada |
| `DB_NAME` | `backend` | ✅ Sí | Nombre de BD pasado a Django | `league_db` (hardcoded) | ⚠️ No usa variable del `.env` |
| `DB_USER` | `backend` | ✅ Sí | Usuario de BD pasado a Django | `admin` (hardcoded) | ⚠️ No usa variable del `.env` |
| `DB_PASSWORD` | `backend` | ✅ Sí | Contraseña de BD pasada a Django | `admin` (hardcoded) | 🔴 Contraseña débil hardcodeada |
| `DB_HOST` | `backend` | ✅ Sí | Host de BD (nombre del servicio Docker) | `db` (hardcoded) | ✅ Correcto para Docker |
| `DB_PORT` | `backend` | ✅ Sí | Puerto de BD | `5432` (hardcoded) | ✅ Aceptable como constante |
| `OPENROUTER_API_KEY` | `backend` | ⚠️ Condicional | Clave de OpenRouter — se pasa desde el shell del host | `${OPENROUTER_API_KEY}` | ✅ Correctamente referenciada |

### 1.4 Configuración de seguridad interna — `jwt_service.py` (valores hardcodeados)

| Parámetro | Valor | Configurable | Descripción |
|-----------|-------|--------------|-------------|
| Algoritmo JWT | `HS256` | ❌ No | Algoritmo de firma de tokens. Hardcodeado en `jwt.encode(..., algorithm="HS256")` |
| TTL access token | `15 minutos` | ❌ No | Tiempo de vida del access token. `timedelta(minutes=15)` en `jwt_service.py:17` |
| TTL refresh token | `7 días` | ❌ No | Tiempo de vida del refresh token. `timedelta(days=7)` en `jwt_service.py:29` |

### 1.5 Configuración de seguridad interna — `user.py` (valores hardcodeados en dominio)

| Parámetro | Valor | Configurable | Descripción |
|-----------|-------|--------------|-------------|
| Máximo intentos de login | `5` | ❌ No | `User.__MAX_ATTEMPTS = 5` en `user.py:9`. Bloquea la cuenta tras 5 fallos consecutivos |
| Tiempo de bloqueo | `15 min` | ❌ No | `User.__MIN_LOCK_TIME = 15` en `user.py:11`. Duración del bloqueo de cuenta |
| Longitud mínima de contraseña | `8 caracteres` | ❌ No | `User.__MIN_PASSWORD_LENGTH = 8` en `user.py:12` |
| Edad máxima de usuario | `80 años` | ❌ No | `User.__MAX_AGE = 80` en `user.py:10` |
| Edad mínima de usuario | `3 años` | ❌ No | `User.__MIN_AGE = 3` en `user.py:11` |

### 1.6 Configuración de CORS — `settings.py` (valores hardcodeados)

| Parámetro | Valor | Configurable | Descripción |
|-----------|-------|--------------|-------------|
| `CORS_ALLOWED_ORIGINS` | `["http://localhost:5173", "http://127.0.0.1:5173"]` | ❌ No | Orígenes permitidos para peticiones cross-origin. Hardcodeados — en producción requiere modificar el archivo |
| `CORS_ALLOW_CREDENTIALS` | `True` | ❌ No | Permite cookies/credentials en peticiones CORS |

### 1.7 Configuración del modelo ML — `xgboost_adapter.py` (valores hardcodeados)

| Parámetro | Valor | Configurable | Descripción |
|-----------|-------|--------------|-------------|
| `MODEL_PATH` | `simulacion/infrastructure/ml/xgboost_model.pkl` | ❌ No | Ruta al modelo XGBoost serializado. Relativa al propio archivo. Falla silenciosamente si el archivo no existe |

### 1.8 Configuración de cobertura — `.coveragerc`

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `source` | `.` | Directorio raíz para medir cobertura |
| `fail_under` | `60` | Cobertura mínima requerida. El CI falla si la cobertura es < 60% |
| `show_missing` | `True` | Muestra líneas sin cobertura en el reporte |
| `omit` | `*/migrations/*, */tests/*, manage.py, config/asgi.py, config/wsgi.py` | Archivos excluidos de la medición |

### 1.9 Configuración del cliente HTTP — `frontend/src/services/api.ts`

| Parámetro | Valor | Configurable | Descripción |
|-----------|-------|--------------|-------------|
| `baseURL` | `import.meta.env.VITE_API_URL \|\| "http://127.0.0.1:8000/api/"` | ✅ Sí (via `VITE_API_URL`) | URL base del backend. Tiene fallback hardcodeado |
| `withCredentials` | `true` | ❌ No | Permite enviar cookies en peticiones CORS |
| `Content-Type` | `application/json` | ❌ No | Tipo de contenido de las peticiones |
| Token refresh automático | Sí (interceptor en 401) | ❌ No | Si el access token expira, el interceptor intenta refresh automático |

---

## 2. Secretos identificados

> **Secretos** = valores que dan acceso a recursos, deben rotar periódicamente, nunca deben aparecer en logs ni en control de versiones.

| # | Secreto | Archivo | Estado | Riesgo |
|---|---------|---------|--------|--------|
| 1 | `DJANGO_SECRET_KEY` | `config/settings.py` | 🔴 **CRÍTICO** — tiene fallback inseguro hardcodeado: `'django-insecure-v50ee$v908kp8p)$_dx87tw39y##gb)=bwg872q@txgf=4no2g'`. Si `DJANGO_SETTINGS_MODULE` se ejecuta sin `.env`, esta clave se usa en producción | Sin rotación, conocida públicamente si el repo es público |
| 2 | `DB_PASSWORD` | `docker-compose.yml` | 🔴 **CRÍTICO** — valor `admin` hardcodeado directamente en el YAML: `DB_PASSWORD: admin`. Este archivo SÍ está en control de versiones | Contraseña trivial expuesta en git |
| 3 | `POSTGRES_PASSWORD` | `docker-compose.yml` | 🔴 **CRÍTICO** — valor `admin` hardcodeado: `POSTGRES_PASSWORD: admin` | Mismo riesgo que arriba |
| 4 | `OPENROUTER_API_KEY` | `.env.example` | ✅ **CORRECTO** — el `.env.example` contiene un placeholder. La variable real se pasa via `${OPENROUTER_API_KEY}` en el compose y debe estar en `.env` (en `.gitignore`) | Sin riesgo si `.env` no se commitea |
| 5 | `DB_PASSWORD` | `.env.example` | ✅ **CORRECTO** — el `.env.example` documenta el nombre, el `.env` real está en `.gitignore` | Sin riesgo de exposición |

### Árbol de uso de `DJANGO_SECRET_KEY`

```
settings.py
    │
    ├── Django CSRF tokens (firmados con SECRET_KEY)
    ├── Django session cookies (firmadas con SECRET_KEY)
    │
    └── authentication/infrastructure/adapters/input/api/views.py:19
            jwt_service = JWTService(SECRET_KEY=settings.SECRET_KEY)
                    │
                    └── jwt_service.py → jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                        ← TODOS los tokens JWT del sistema usan esta misma clave
```

**Implicación:** Si `DJANGO_SECRET_KEY` se compromete, un atacante puede:
1. Firmar tokens JWT arbitrarios con cualquier `user_id` y `rol`
2. Falsificar tokens CSRF
3. Descifrar cookies de sesión

---

## 3. Tokens identificados

| # | Token | Tipo | TTL | Algoritmo | Almacenamiento | Revocación |
|---|-------|------|-----|-----------|---------------|-----------|
| 1 | **JWT Access Token** | Bearer (Authorization header) | 15 minutos | HS256 | `localStorage` (frontend) | ❌ No implementada — logout solo en cliente |
| 2 | **JWT Refresh Token** | Body de request a `/api/auth/refresh/` | 7 días | HS256 | `localStorage` (frontend) | ❌ No implementada — token válido hasta expirar |
| 3 | **OPENROUTER_API_KEY** | API Key en header HTTP | Sin TTL propio (depende de OpenRouter) | — | Variable de entorno del servidor | Desde el dashboard de OpenRouter |

### Estructura del JWT Access Token (payload)

```json
{
  "user_id": "uuid-del-usuario",
  "email":   "user@example.com",
  "rol":     "admin | manager | coach | participant",
  "state":   "active | blocked | not_verified",
  "exp":     1234567890,
  "iat":     1234567890,
  "type":    "access"
}
```

### Estructura del JWT Refresh Token (payload)

```json
{
  "user_id": "uuid-del-usuario",
  "exp":     1234567890,
  "iat":     1234567890,
  "type":    "refresh"
}
```

### Flujo de tokens en `api.ts` (frontend)

```
Request → interceptor request → adjunta "Authorization: Bearer <access_token>"
Response 401 → interceptor response → llama a /api/auth/refresh/
    ├── refresh OK → nuevo access token → reintenta request original
    └── refresh FAIL → clearTokens() → redirect a "/" (login)
```

---

## 4. Configuración de base de datos

### 4.1 Parámetros de conexión

| Parámetro | Valor en Docker | Valor en nativo | Variable de entorno |
|-----------|----------------|----------------|---------------------|
| Engine | `django.db.backends.postgresql` | idem | Hardcodeado en `settings.py` |
| Nombre | `league_db` | `league_db` | `DB_NAME` |
| Usuario | `admin` | `admin` | `DB_USER` |
| Contraseña | `admin` | `admin` | `DB_PASSWORD` |
| Host | `db` (nombre servicio Docker) | `localhost` | `DB_HOST` |
| Puerto | `5432` | `5432` | `DB_PORT` |

### 4.2 Configuración del contenedor PostgreSQL

```yaml
# Extraído de docker-compose.yml
db:
  image: postgres:17
  restart: always
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U admin -d league_db"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 10s
  volumes:
    - postgres_data:/var/lib/postgresql/data   # ← persistencia entre reinicios
```

### 4.3 Problemas detectados en la configuración de base de datos

| # | Problema | Severidad | Descripción |
|---|----------|-----------|-------------|
| 1 | Contraseña hardcodeada en `docker-compose.yml` | 🔴 CRÍTICA | `POSTGRES_PASSWORD: admin` y `DB_PASSWORD: admin` están literales en el YAML que está en git |
| 2 | Credenciales duplicadas | 🟠 ALTA | Las mismas credenciales se declaran dos veces: en el bloque `db.environment` (para el servidor PostgreSQL) y en `backend.environment` (para Django). No están sincronizadas via variables |
| 3 | Sin connection pooling | 🟡 MEDIA | Django ORM sin `CONN_MAX_AGE` ni PgBouncer — cada request abre y cierra una conexión |
| 4 | Sin SSL para la conexión BD | 🟡 MEDIA | No hay `OPTIONS: {"sslmode": "require"}` en `DATABASES` — en producción la conexión a BD es sin cifrar |
| 5 | SQLite comentado pero presente | 🟢 BAJA | `settings.py` tiene bloques de configuración SQLite comentados — riesgo de activación accidental al descomentar |

### 4.4 Variables de BD no controladas por entorno

```python
# settings.py — líneas 118-127
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',   # ← hardcodeado
        'NAME': os.getenv('DB_NAME'),                # ← correcto
        'USER': os.getenv('DB_USER'),                # ← correcto
        'PASSWORD': os.getenv('DB_PASSWORD'),        # ← correcto
        'HOST': os.getenv('DB_HOST'),                # ← correcto
        'PORT': os.getenv('DB_PORT'),                # ← correcto
        # AUSENTE: CONN_MAX_AGE, OPTIONS (ssl, timeout)
    }
}
```

---

## 5. Configuración de APIs externas

### 5.1 OpenRouter (servicio LLM)

| Parámetro | Valor | Fuente | Estado |
|-----------|-------|--------|--------|
| URL base | Gestionada por el SDK de `openai` apuntando a OpenRouter | Implícita en `openai>=1.0.0` | ✅ |
| Clave de API | `OPENROUTER_API_KEY` | `.env.example` → variable de entorno | ✅ Correctamente externalizada |
| Modelo usado | No detectable — la generación de rúbricas usa plantillas locales (`rubrica_generator.py`) | — | ℹ️ El módulo IA usa plantillas hardcodeadas, no llamadas a LLM activas |
| Timeout | No configurado | — | ⚠️ Sin timeout definido — requests colgantes posibles |
| Retry logic | No implementado | — | ⚠️ Sin reintentos automáticos |
| Circuit breaker | No implementado | — | ⚠️ Si OpenRouter falla, el endpoint falla directamente |

> **Hallazgo importante:** `rubrica_generator.py` **no realiza llamadas HTTP a OpenRouter**. Es un generador de rúbricas basado en plantillas Python puras. La dependencia `openai>=1.0.0` está instalada pero no se detectó uso activo en el código auditado. Puede ser una dependencia preparada para integración futura o parte de `rules_nlp_adapter.py`.

### 5.2 Frontend → Backend (API propia)

| Parámetro | Valor | Fuente | Estado |
|-----------|-------|--------|--------|
| URL base | `import.meta.env.VITE_API_URL \|\| "http://127.0.0.1:8000/api/"` | `api.ts:9` | ⚠️ Fallback hardcodeado |
| Autenticación | `Bearer <JWT>` en header `Authorization` | `api.ts:22-28` (interceptor) | ✅ |
| Refresh automático | Sí — interceptor en respuesta 401 | `api.ts:95-121` | ✅ |
| Timeout | No configurado (default Axios: indefinido) | — | ⚠️ Sin timeout |
| `withCredentials` | `true` | `api.ts:15` | ✅ Requerido para CORS con cookies |

---

## 6. Mapa completo de origen → consumo de cada variable

```
VARIABLE                    ORIGEN              CONSUMIDO EN
────────────────────────────────────────────────────────────────────────
DB_NAME          ←── .env ──────────────────→ settings.py:119
DB_USER          ←── .env ──────────────────→ settings.py:120
DB_PASSWORD      ←── .env ──────────────────→ settings.py:121
DB_HOST          ←── .env ──────────────────→ settings.py:122
DB_PORT          ←── .env ──────────────────→ settings.py:123

DJANGO_SECRET_KEY ←── .env ─────────────────→ settings.py:27-30
                                             → jwt_service.py (via settings.SECRET_KEY)
                                             → auth_decorator.py (via settings.SECRET_KEY)
                                             → Django CSRF / sessions (built-in)

DJANGO_DEBUG     ←── .env ──────────────────→ settings.py:34
DJANGO_ALLOWED_HOSTS ←── .env ──────────────→ settings.py:40-42
LOG_LEVEL        ←── .env ──────────────────→ settings.py:177

OPENROUTER_API_KEY ←── .env / shell host ───→ docker-compose.yml:49 (${OPENROUTER_API_KEY})
                                             → consumido por el SDK openai (no detectado en código auditado)

POSTGRES_DB      ←── docker-compose.yml ────→ PostgreSQL container (init)
POSTGRES_USER    ←── docker-compose.yml ────→ PostgreSQL container (init)
POSTGRES_PASSWORD ←── docker-compose.yml ───→ PostgreSQL container (init)

VITE_API_URL     ←── frontend/.env.local ───→ frontend/src/services/api.ts:9 (import.meta.env)

MODEL_PATH       ←── hardcodeado ───────────→ xgboost_adapter.py:5
                                               (simulacion/infrastructure/ml/xgboost_model.pkl)
```

---

## 7. Hallazgos de seguridad en la configuración

### 7.1 Resumen por severidad

| Severidad | # | Hallazgo |
|-----------|---|---------|
| 🔴 CRÍTICA | 1 | `DJANGO_SECRET_KEY` con fallback inseguro hardcodeado en `settings.py`. Si el proceso arranca sin `.env`, usa la clave pública visible en el código fuente |
| 🔴 CRÍTICA | 2 | `DB_PASSWORD: admin` hardcodeado en `docker-compose.yml` — archivo versionado en Git |
| 🔴 CRÍTICA | 3 | `POSTGRES_PASSWORD: admin` hardcodeado en `docker-compose.yml` — contraseña trivial en archivo versionado |
| 🟠 ALTA | 4 | Sin revocación de tokens JWT — logout no invalida el token en servidor; un token robado permanece válido 15 minutos |
| 🟠 ALTA | 5 | Algoritmo JWT HS256 con clave simétrica — si `SECRET_KEY` se compromete, todos los tokens históricos son falsificables |
| 🟠 ALTA | 6 | CORS hardcodeado en `settings.py` — `CORS_ALLOWED_ORIGINS` no es configurable por entorno sin modificar el archivo |
| 🟡 MEDIA | 7 | Sin timeout en cliente Axios — requests colgantes pueden bloquear la UI indefinidamente |
| 🟡 MEDIA | 8 | Sin timeout en cliente OpenRouter — llamadas LLM sin límite de tiempo |
| 🟡 MEDIA | 9 | Sin SSL configurado para conexión PostgreSQL — tráfico BD sin cifrar en red |
| 🟡 MEDIA | 10 | `VITE_API_URL` con fallback hardcodeado en `api.ts:9` — si la variable no está definida, apunta a `127.0.0.1` silenciosamente |
| 🟡 MEDIA | 11 | `xgboost_model.pkl` falla con `RuntimeError` si no existe — no hay validación de existencia al arrancar |
| 🟢 BAJA | 12 | Parámetros de seguridad del dominio (intentos, TTL de bloqueo, longitud de contraseña) no son configurables por entorno |
| 🟢 BAJA | 13 | `DJANGO_DEBUG=False` por defecto — correcto, pero sin validación que lo fuerce en producción |

### 7.2 Correcciones recomendadas

```python
# 1. settings.py — SECRET_KEY sin fallback inseguro
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']  # falla si no está definida → fuerza configuración

# 2. settings.py — CORS configurable por entorno
CORS_ALLOWED_ORIGINS = [
    h.strip()
    for h in os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
    if h.strip()
]

# 3. settings.py — conexión PostgreSQL con SSL y timeout
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'sslmode': os.environ.get('DB_SSLMODE', 'prefer'),
            'connect_timeout': 10,
        },
    }
}
```

```yaml
# 4. docker-compose.yml — usar variables del host, no hardcodear
services:
  db:
    environment:
      POSTGRES_DB:       ${DB_NAME}
      POSTGRES_USER:     ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  backend:
    environment:
      DB_NAME:     ${DB_NAME}
      DB_USER:     ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      DB_HOST:     db
      DB_PORT:     ${DB_PORT:-5432}
      DJANGO_SECRET_KEY:   ${DJANGO_SECRET_KEY}
      DJANGO_DEBUG:        ${DJANGO_DEBUG:-False}
      DJANGO_ALLOWED_HOSTS: ${DJANGO_ALLOWED_HOSTS:-localhost}
      OPENROUTER_API_KEY:  ${OPENROUTER_API_KEY}
```

```typescript
// 5. api.ts — timeout explícito
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,   // eliminar fallback hardcodeado
  timeout: 30000,                           // 30 segundos
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});
```

---

## 8. Matriz de configuración: archivos vs categorías

| Archivo | Secretos | Tokens | BD | API externa | Logging | Seguridad |
|---------|----------|--------|-----|-------------|---------|-----------|
| `.env.example` | `DB_PASSWORD`, `DJANGO_SECRET_KEY`, `OPENROUTER_API_KEY` | — | `DB_*` | `OPENROUTER_API_KEY` | `LOG_LEVEL` | `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS` |
| `frontend/.env.template` | — | — | — | `VITE_API_URL` | — | — |
| `config/settings.py` | `SECRET_KEY` (con fallback inseguro) | — | `DATABASES` dict | `CORS_ALLOWED_ORIGINS` (hardcoded) | `LOGGING` dict | `ALLOWED_HOSTS`, `DEBUG`, `MIDDLEWARE` |
| `docker-compose.yml` | `POSTGRES_PASSWORD: admin` 🔴, `DB_PASSWORD: admin` 🔴 | — | `POSTGRES_*`, `DB_*` | `OPENROUTER_API_KEY: ${...}` | — | `restart: always`, healthchecks |
| `jwt_service.py` | `SECRET_KEY` (recibido) | Generación JWT | — | — | — | HS256, TTL 15min/7d (hardcoded) |
| `auth_decorator.py` | — | Verificación JWT | — | — | — | RBAC, extracción de rol |
| `frontend/api.ts` | — | Adjunta Bearer token | — | `VITE_API_URL` (con fallback hardcoded) | — | Interceptor 401 → refresh |
| `xgboost_adapter.py` | — | — | — | — | — | `MODEL_PATH` (hardcoded) |
| `.coveragerc` | — | — | — | — | — | `fail_under: 60` |

---

*Auditoría generada mediante análisis estático directo de todos los archivos de configuración identificados. No se ejecutó el sistema. Los valores de secretos en el análisis son los encontrados en el repositorio — en ningún caso representan secretos reales de producción.*
