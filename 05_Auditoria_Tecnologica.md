# Auditoría Tecnológica — Zoids League
**Auditor:** Senior Software Auditor (Claude Sonnet 4.6)  
**Fecha:** 2026-06-19  
**Rama auditada:** `Auditoria-Furps`  
**Directorio raíz:** `d:\league`

---

## 1. Lenguajes encontrados

| # | Lenguaje | Versión detectada | Evidencia |
|---|----------|-------------------|-----------|
| 1 | Python | 3.12 (imagen Docker) | `Dockerfile` → `FROM python:3.12-slim` |
| 2 | TypeScript | ^6.0.2 | `frontend/react/package.json` → `"typescript": "^6.0.2"` |
| 3 | JavaScript (ES Modules) | ES2020 target | `tsconfig.json` → `"target": "ES2020"` |
| 4 | SQL | PostgreSQL dialect | Migraciones Django (22 archivos) |
| 5 | HTML | HTML5 | `frontend/react/index.html` |
| 6 | CSS | CSS3 + PostCSS | `frontend/react/src/styles/index.css`, `postcss.config.mjs` |

---

## 2. Frameworks encontrados

| # | Framework | Versión | Evidencia |
|---|-----------|---------|-----------|
| 1 | Django | 6.0.4 | `requirements.txt` → `Django==6.0.4` |
| 2 | Django REST Framework | 3.17.1 | `requirements.txt` → `djangorestframework==3.17.1` |
| 3 | React | 18.3.1 | `package.json` → `"react": "^18.3.1"` |
| 4 | React Router | 7.13.0 | `package.json` → `"react-router": "7.13.0"` |
| 5 | Material UI (MUI) | 7.3.5 | `package.json` → `"@mui/material": "7.3.5"` |
| 6 | Tailwind CSS | 4.1.12 | `package.json` → `"tailwindcss": "4.1.12"` |
| 7 | scikit-learn | 1.6.1 | `requirements.txt` → `scikit-learn==1.6.1` |

---

## 3. Tecnologías Backend

| # | Tecnología | Versión | Evidencia |
|---|------------|---------|-----------|
| 1 | Django ORM | 6.0.4 | Migraciones en `*/migrations/`, modelos en `*/infrastructure/adapters/output/models.py` |
| 2 | Django REST Framework | 3.17.1 | `requirements.txt`; serializers en `simulacion/infrastructure/adapters/input/api/serializers.py` |
| 3 | SimpleJWT | 5.5.1 | `requirements.txt` → `djangorestframework_simplejwt==5.5.1` |
| 4 | Gunicorn (WSGI) | 26.0.0 | `requirements.txt` → `gunicorn==26.0.0` |
| 5 | django-cors-headers | 4.9.0 | `requirements.txt` → `django-cors-headers==4.9.0` |
| 6 | Whitenoise | 6.12.0 | `requirements.txt` → `whitenoise==6.12.0` (archivos estáticos) |
| 7 | bcrypt | 5.0.0 | `requirements.txt` → `bcrypt==5.0.0`; `authentication/application/service/password_service.py` |
| 8 | python-dotenv | >=1.0.0 | `requirements.txt` → `python-dotenv>=1.0.0` |
| 9 | XGBoost | 2.1.4 | `requirements.txt` → `xgboost==2.1.4`; `simulacion/infrastructure/adapters/ia/prediction_model.py` |
| 10 | openai SDK | >=1.0.0 | `requirements.txt` → `openai>=1.0.0`; cliente hacia OpenRouter |
| 11 | psycopg2 | 2.9.12 | `requirements.txt` → `psycopg2==2.9.12` (driver PostgreSQL) |
| 12 | Arquitectura Hexagonal (Ports & Adapters) | — | Estructura de carpetas: `domain/`, `application/`, `infrastructure/` en los 4 módulos |

---

## 4. Tecnologías Frontend

| # | Tecnología | Versión | Evidencia |
|---|------------|---------|-----------|
| 1 | Vite | 6.3.5 | `package.json` → `"vite": "6.3.5"` |
| 2 | @vitejs/plugin-react | 4.7.0 | `package.json`; `vite.config.ts` |
| 3 | Axios | ^1.15.0 | `package.json` → `"axios": "^1.15.0"`; `src/services/api.ts` |
| 4 | React Hook Form | 7.55.0 | `package.json` → `"react-hook-form": "7.55.0"` |
| 5 | Recharts | 2.15.2 | `package.json` → `"recharts": "2.15.2"` (gráficos) |
| 6 | React DnD | 16.0.1 | `package.json` → `"react-dnd": "16.0.1"` (drag & drop) |
| 7 | Radix UI | varios | `package.json` → `@radix-ui/*` (componentes accesibles) |
| 8 | Emotion | 11.14.0 | `package.json` → `"@emotion/react": "11.14.0"` (CSS-in-JS para MUI) |
| 9 | PostCSS | — | `postcss.config.mjs` |
| 10 | @tailwindcss/vite | 4.1.12 | `package.json`; integración Vite |

---

## 5. Bases de datos

| # | Base de datos | Versión | Evidencia |
|---|---------------|---------|-----------|
| 1 | PostgreSQL | 17 | `docker-compose.yml` → `image: postgres:17` |
| 2 | SQLite (implícito) | — | Fallback Django por defecto en desarrollo sin `.env`; no confirmado en uso activo |

**Tablas identificadas (20+):**

| Módulo | Tablas |
|--------|--------|
| `authentication` | `authentication_user` |
| `competencia` | `tournament`, `tournament_rule`, `tournament_member`, `team`, `participant`, `institution`, `docente_asesor`, `match`, `match_result`, `standing`, `group`, `criteria`, `criterio_ia`, `nlp_analysis`, `final_ranking` |
| `simulacion` | `simulacion_predictiva`, `analisis_entrega`, `simulacion_resultado` |

---

## 6. Herramientas DevOps

| # | Herramienta | Versión | Evidencia |
|---|-------------|---------|-----------|
| 1 | Docker | — | `Dockerfile` (raíz) + `frontend/react/Dockerfile` |
| 2 | Docker Compose | — | `docker-compose.yml` (3 servicios orquestados) |
| 3 | Git | — | `.git/` presente; ramas detectadas: `main`, `Auditoria-Furps` |
| 4 | Coverage.py | — | `.coveragerc` → objetivo de cobertura 60% |
| 5 | pip | — | `requirements.txt`; `RUN pip install --no-cache-dir -r requirements.txt` en Dockerfile |
| 6 | npm | — | `package-lock.json` (214 KB) |

> **No se detectó CI/CD automatizado** (ausencia de `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile` o equivalente).

---

## 7. Servicios externos

| # | Servicio | Propósito | Evidencia |
|---|----------|-----------|-----------|
| 1 | OpenRouter | Proxy LLM — acceso a GPT-4o para generación de criterios de evaluación con IA | `.env.example` → `OPENROUTER_API_KEY`; `competencia/infrastructure/adapters/ia/rubrica_generator.py` |
| 2 | OpenAI SDK | Cliente HTTP hacia OpenRouter (usa la misma interfaz de API) | `requirements.txt` → `openai>=1.0.0` |

> No se detectaron integraciones con servicios de email, SMS, almacenamiento cloud (S3, GCS), CDN ni servicios de monitoreo externos.

---

## 8. Sistemas de autenticación

| # | Mecanismo | Implementación | Evidencia |
|---|-----------|----------------|-----------|
| 1 | JWT (JSON Web Tokens) | `djangorestframework_simplejwt` + servicio propio | `authentication/application/service/jwt_service.py`; endpoint `/api/auth/refresh/` |
| 2 | bcrypt | Hash de contraseñas en registro | `authentication/application/service/password_service.py`; `bcrypt==5.0.0` |
| 3 | RBAC (Role-Based Access Control) | Roles: `admin`, `manager`, `coach`, `participant` | `authentication/domain/value_objects/enum/system_rol.py`; decorador `@auth_required` |
| 4 | Bloqueo por intentos fallidos | Campo `attempts` + `blocked_until` en modelo de usuario | `authentication_user` → columnas `attempts`, `blocked_until` |
| 5 | Context de autenticación (Frontend) | React Context API | `frontend/react/src/context/AuthContext.tsx` |
| 6 | Guard de rutas por rol (Frontend) | Componente `RoleGuard` | `frontend/react/src/components/auth/RoleGuard.tsx`; `src/hooks/useRoleGuard.ts` |

---

## 9. Sistema de despliegue

| # | Componente | Tecnología | Evidencia |
|---|------------|------------|-----------|
| 1 | Backend container | Python 3.12-slim + Gunicorn | `Dockerfile` raíz |
| 2 | Frontend container | Node (Vite dev server en puerto 5173) | `frontend/react/Dockerfile` |
| 3 | Base de datos container | postgres:17 con volumen persistente | `docker-compose.yml` → `postgres_data` volume |
| 4 | Orquestación | Docker Compose (desarrollo) | `docker-compose.yml` — 3 servicios con healthchecks |
| 5 | Archivos estáticos | Whitenoise (servidos desde Django) | `requirements.txt` → `whitenoise==6.12.0` |
| 6 | ASGI (preparado) | `config/asgi.py` presente | Listo para despliegue con Daphne/Uvicorn |

> El despliegue actual es **local/desarrollo**. No se detectó configuración para entorno productivo (Nginx, Kubernetes, servicios cloud, pipeline de release).

---

## 10. Tabla consolidada de auditoría tecnológica

| Categoría | Tecnología | Evidencia | Confianza |
|-----------|------------|-----------|-----------|
| **Lenguaje** | Python 3.12 | `Dockerfile` → `FROM python:3.12-slim` | Alta |
| **Lenguaje** | TypeScript ^6.0.2 | `package.json` → `"typescript": "^6.0.2"` | Alta |
| **Lenguaje** | JavaScript ES2020 | `tsconfig.json` → `"target": "ES2020"` | Alta |
| **Lenguaje** | SQL (PostgreSQL dialect) | 22 archivos de migración Django | Alta |
| **Lenguaje** | HTML5 / CSS3 | `index.html`, `src/styles/` | Alta |
| **Framework** | Django 6.0.4 | `requirements.txt` + `manage.py` + `config/settings.py` | Alta |
| **Framework** | Django REST Framework 3.17.1 | `requirements.txt` + serializers + views | Alta |
| **Framework** | React 18.3.1 | `package.json` + 31 archivos `.tsx` | Alta |
| **Framework** | React Router 7.13.0 | `package.json` + `src/routes/index.tsx` | Alta |
| **Framework** | Material UI 7.3.5 | `package.json` → `@mui/material` | Alta |
| **Framework** | Tailwind CSS 4.1.12 | `package.json` + `postcss.config.mjs` | Alta |
| **Framework** | scikit-learn 1.6.1 | `requirements.txt` | Alta |
| **Backend** | Django ORM | Migraciones + modelos en `/infrastructure/` | Alta |
| **Backend** | Gunicorn 26.0.0 | `requirements.txt` | Alta |
| **Backend** | SimpleJWT 5.5.1 | `requirements.txt` | Alta |
| **Backend** | django-cors-headers 4.9.0 | `requirements.txt` + CORS config en `settings.py` | Alta |
| **Backend** | Whitenoise 6.12.0 | `requirements.txt` | Alta |
| **Backend** | bcrypt 5.0.0 | `requirements.txt` + `password_service.py` | Alta |
| **Backend** | XGBoost 2.1.4 | `requirements.txt` + `prediction_model.py` | Alta |
| **Backend** | Arquitectura Hexagonal | 4 módulos con `domain/`, `application/`, `infrastructure/` | Alta |
| **Frontend** | Vite 6.3.5 | `package.json` + `vite.config.ts` | Alta |
| **Frontend** | Axios ^1.15.0 | `package.json` + `src/services/api.ts` | Alta |
| **Frontend** | React Hook Form 7.55.0 | `package.json` | Alta |
| **Frontend** | Recharts 2.15.2 | `package.json` | Alta |
| **Frontend** | React DnD 16.0.1 | `package.json` | Alta |
| **Frontend** | Radix UI | `package.json` → `@radix-ui/*` | Alta |
| **Frontend** | Emotion 11.14.0 | `package.json` → `@emotion/react` | Alta |
| **Base de datos** | PostgreSQL 17 | `docker-compose.yml` → `image: postgres:17` | Alta |
| **Base de datos** | psycopg2 2.9.12 | `requirements.txt` (driver nativo) | Alta |
| **Base de datos** | SQLite | Implícito como fallback Django | Baja |
| **DevOps** | Docker | `Dockerfile` (backend y frontend) | Alta |
| **DevOps** | Docker Compose | `docker-compose.yml` | Alta |
| **DevOps** | Git | `.git/` + historial de commits | Alta |
| **DevOps** | Coverage.py | `.coveragerc` | Alta |
| **DevOps** | CI/CD pipeline | No detectado | N/A |
| **Servicio externo** | OpenRouter (GPT-4o) | `.env.example` → `OPENROUTER_API_KEY` | Alta |
| **Servicio externo** | OpenAI SDK | `requirements.txt` → `openai>=1.0.0` | Alta |
| **Autenticación** | JWT | `djangorestframework_simplejwt` + `jwt_service.py` | Alta |
| **Autenticación** | bcrypt | `password_service.py` | Alta |
| **Autenticación** | RBAC (4 roles) | `system_rol.py` + `@auth_required` | Alta |
| **Autenticación** | Bloqueo por intentos | Modelo `authentication_user` (`attempts`, `blocked_until`) | Alta |
| **Autenticación** | React Context (Frontend) | `AuthContext.tsx` + `RoleGuard.tsx` | Alta |
| **Despliegue** | Docker Compose (dev) | `docker-compose.yml` | Alta |
| **Despliegue** | Whitenoise (estáticos) | `requirements.txt` | Alta |
| **Despliegue** | ASGI (preparado) | `config/asgi.py` | Media |
| **Despliegue** | Producción cloud | No detectado | N/A |

---

## 11. Conclusión técnica

### Stack tecnológico detectado

Zoids League es una **aplicación web full-stack de arquitectura desacoplada**, compuesta por:

- **Backend:** Django 6.0.4 con Django REST Framework, implementado bajo el patrón **Arquitectura Hexagonal (Ports & Adapters / DDD)**. Los cuatro módulos del sistema (`authentication`, `competencia`, `simulacion`, `analitica`) respetan la separación `domain → application → infrastructure`, lo que constituye el activo técnico más valioso del proyecto.
- **Frontend:** SPA en React 18 con TypeScript estricto, empaquetada con Vite 6. La UI combina Material UI y Tailwind CSS, lo que introduce dualidad de sistema de diseño (riesgo de inconsistencia visual).
- **Base de datos:** PostgreSQL 17 como única fuente de verdad, accedida exclusivamente vía Django ORM con 22 migraciones versionadas.
- **Inteligencia artificial:** Doble integración — XGBoost 2.1.4 para predicción determinista de resultados y OpenRouter (GPT-4o) como servicio LLM externo para generación de criterios de evaluación via NLP.
- **Despliegue:** Totalmente contenedorizado con Docker Compose para desarrollo local (3 servicios: postgres, django, react). No existe configuración productiva (Nginx, HTTPS, escalado, CI/CD).

### Fortalezas detectadas

1. **Arquitectura limpia y extensible:** La separación hexagonal en los 4 módulos permite escalar el sistema sin romper la lógica de negocio.
2. **Tipado estático en ambos extremos:** Python con type hints inferidos por Django ORM y TypeScript en modo estricto en el frontend.
3. **Seguridad de autenticación robusta:** bcrypt para hashing, JWT con refresh tokens, RBAC con 4 roles, bloqueo por intentos fallidos — todo implementado desde la capa de dominio.
4. **IA integrada de forma pragmática:** XGBoost para predicciones locales (sin dependencia de red) y LLM externo solo para generación de contenido, separación correcta de responsabilidades.
5. **Trazabilidad de BD:** 22 migraciones versionadas en Git — el esquema es auditable en su totalidad.

### Brechas y riesgos detectados

| Riesgo | Severidad | Descripción |
|--------|-----------|-------------|
| Sin pipeline CI/CD | Alta | No existe automatización de tests ni despliegue. Todo es manual. |
| Despliegue productivo ausente | Alta | `docker-compose.yml` usa `runserver` (servidor de desarrollo Django, no apto para producción) |
| Doble sistema de diseño | Media | Convivencia de MUI 7 + Tailwind 4 sin una capa de abstracción puede generar deuda de UI |
| Dependencia LLM externa | Media | `OPENROUTER_API_KEY` sin fallback — si el servicio cae, la generación de criterios falla completamente |
| Cobertura de tests objetivo 60% | Media | `.coveragerc` declara objetivo del 60%; la cobertura actual podría estar por debajo |
| SQLite implícito como fallback | Baja | Sin `.env` configurado, Django puede silenciosamente caer en SQLite, ocultando errores de BD |
| ASGI configurado pero no usado | Baja | `config/asgi.py` está presente pero no hay soporte WebSocket ni worker async en docker-compose |

### Recomendaciones prioritarias

1. **Reemplazar `runserver` por Gunicorn en `docker-compose.yml`** — ya está instalado en `requirements.txt`, solo falta wiring.
2. **Agregar Nginx** como proxy inverso para TLS, servicio de estáticos y balanceo.
3. **Implementar GitHub Actions** (o equivalente) con jobs de lint, test y build para cada PR.
4. **Centralizar el sistema de diseño** — elegir MUI o Tailwind como sistema primario y usar el otro solo como utilidad.
5. **Agregar circuit breaker o fallback** para la dependencia con OpenRouter.

### Veredicto técnico

> El proyecto demuestra un nivel de madurez arquitectónica alto para un MVP educativo. La separación hexagonal, el tipado estático y la autenticación robusta son señales de diseño deliberado. Las brechas principales son operativas (DevOps, producción) y no arquitectónicas, lo que implica que el costo de llevar el sistema a producción es bajo comparado con reescribir la base. **El stack es coherente, moderno y sostenible.**

---

*Auditoría generada automáticamente mediante análisis estático de código, configuración y dependencias. No se ejecutó el sistema durante la auditoría.*
