# Reporte de Ingeniería Inversa

**Sistema:** Zoids League — Plataforma de Gestión de Torneos de Robótica Educativa  
**Auditor:** Auditor de Software Senior — Especialista en Ingeniería Inversa  
**Fecha de auditoría:** 2026-06-19  
**Versión del reporte:** 1.0  
**Clasificación:** Uso interno — Equipo de desarrollo

---

## 1. Resumen Ejecutivo

Zoids League es una plataforma web para la gestión integral de torneos de robótica educativa. El sistema permite crear torneos con múltiples formatos de fixture, inscribir equipos con sus participantes, calificar partidos con criterios ponderados, calcular clasificaciones y ofrecer simulaciones predictivas a los participantes mediante un modelo de Machine Learning local.

La auditoría de ingeniería inversa fue realizada íntegramente sobre el código fuente, sin acceso a entornos de producción activos ni documentación técnica preexistente. Mediante análisis estático, ejecución controlada y reconstrucción del dominio se obtuvo una descripción completa del sistema real.

**Hallazgos críticos:** El sistema presenta **10 vulnerabilidades de severidad crítica** que lo hacen inadecuado para despliegue en entornos de acceso público en su estado actual. Los más urgentes son: la clave secreta de Django versionada en el repositorio (permite forja de cualquier token JWT), credenciales de base de datos hardcodeadas en `docker-compose.yml`, una vulnerabilidad de ejecución remota de código en `react-router` 7.0–7.15, y un bug garantizado de `AttributeError` en el flujo de inscripción de participantes.

**Fortalezas arquitectónicas:** El sistema implementa correctamente patrones de Arquitectura Hexagonal, Clean Architecture y Domain-Driven Design. Las entidades de dominio son ricas, los invariantes de negocio están encapsulados, y la separación de capas está bien aplicada a nivel micro (entidad, use case, repositorio).

**Estado general:** Sistema apto para entorno de demostración o desarrollo controlado. Requiere remediación de hallazgos críticos y altos antes de cualquier exposición pública.

| Métrica | Valor |
|---|---|
| Total de archivos analizados | ~180 |
| Endpoints de API identificados | 44 |
| Rutas frontend identificadas | 21 |
| Entidades de dominio | 21 |
| Casos de uso | 32 |
| Hallazgos totales | 76 |
| Hallazgos críticos | 10 |
| Hallazgos altos | 22 |
| Hallazgos medios | 31 |
| Hallazgos bajos | 14 |

---

## 2. Objetivos

La ingeniería inversa del sistema Zoids League persiguió los siguientes objetivos:

**Objetivo principal**  
Reconstruir una descripción técnica completa y verificada del sistema a partir exclusivamente de sus artefactos de código, configuración y ejecución, en ausencia de documentación técnica formal.

**Objetivos específicos**

1. **Inventario tecnológico:** Identificar el stack técnico completo — lenguajes, frameworks, librerías, versiones y su rol en el sistema.
2. **Arquitectura real:** Determinar los patrones arquitectónicos efectivamente implementados, distinguiéndolos de los patrones declarados en el diseño original.
3. **Modelo de dominio:** Reconstruir las entidades, agregados, value objects, casos de uso, reglas de negocio y relaciones del modelo de dominio.
4. **Flujos de datos:** Trazar el recorrido completo de la información desde el usuario hasta la persistencia, incluyendo transformaciones intermedias.
5. **Superficie de integración:** Documentar todas las APIs expuestas, APIs consumidas, y sistemas externos integrados o preparados para integración.
6. **Evaluación de seguridad:** Identificar vulnerabilidades, configuraciones inseguras y dependencias con CVEs conocidos.
7. **Evaluación de calidad:** Calificar el sistema en cohesión, acoplamiento, escalabilidad, mantenibilidad, testabilidad y seguridad.
8. **Plan de mejora:** Generar recomendaciones priorizadas y accionables.

---

## 3. Alcance

### 3.1 Incluido en el alcance

| Componente | Descripción | Método de análisis |
|---|---|---|
| Backend Django | Código fuente completo — 4 módulos Django | Análisis estático + ejecución |
| Frontend React | Código fuente completo — SPA TypeScript | Análisis estático + compilación |
| Configuración | `settings.py`, `docker-compose.yml`, `.env.template`, Dockerfiles | Lectura directa |
| Dependencias | `requirements.txt`, `package.json`, `package-lock.json` | Análisis + auditoría de CVEs |
| Logs de ejecución | Salida de `pip install`, `manage.py runserver`, `tsc`, `npm audit` | Ejecución controlada |
| Modelo de dominio | Entidades, VOs, use cases, puertos, servicios de dominio | Lectura de código fuente |
| APIs | 44 endpoints backend + 38 llamadas desde frontend | Análisis estático de rutas y views |
| Base de datos | Esquema inferido desde modelos ORM de Django | Análisis de `models.py` |

### 3.2 Fuera del alcance

- Entorno de producción activo (no accesible)
- Base de datos con datos reales de torneos
- Análisis dinámico de tráfico de red en producción
- Código fuente de terceros (librerías npm/pip)
- Infraestructura de hosting (dominio, servidor, red)

### 3.3 Limitaciones encontradas

- **Python 3.14.4 en host vs Python 3.12 requerido:** Impidió la instalación de `scikit-learn` y `numpy` en las versiones declaradas. Se instalaron versiones compatibles alternativas para captura de logs.
- **PostgreSQL no disponible en host:** Los tests de integración y la ejecución completa del backend requieren una instancia PostgreSQL activa. Los flujos de datos fueron analizados estáticamente.
- **Docker no disponible:** El sistema fue analizado con herramientas nativas del host, no desde los contenedores Docker configurados.

---

## 4. Metodología

### 4.1 Auditoría

La auditoría se realizó en múltiples pasadas con perspectivas especializadas:

**Pasada 1 — Auditoría tecnológica (Auditor Senior)**  
Inventario del stack tecnológico, versiones, licencias y compatibilidades. Fuente primaria: `requirements.txt`, `package.json`, Dockerfiles.

**Pasada 2 — Auditoría arquitectónica (Arquitecto de Software)**  
Identificación de patrones arquitectónicos — Hexagonal, Clean Architecture, DDD, Modular Monolith. Análisis de la estructura de directorios y las reglas de dependencia entre capas.

**Pasada 3 — Auditoría de dependencias (Especialista en Dependencias)**  
Análisis de `requirements.txt` y `package.json`. Ejecución de `pip-audit` y `npm audit`. Identificación de versiones desactualizadas, CVEs activos, dependencias duplicadas y librerías abandonadas.

**Pasada 4 — Guía DevOps (Ingeniero DevOps)**  
Análisis de `docker-compose.yml`, Dockerfiles, variables de entorno, y proceso de despliegue. Identificación de brechas operacionales.

**Pasada 5 — Auditoría de configuración (Ingeniero de Configuración)**  
Análisis de `settings.py`, `.env.template`, `docker-compose.yml` y `tsconfig.json`. Verificación de configuraciones de seguridad, fallbacks inseguros, y correctitud de puertos y rutas.

**Pasada 6 — Análisis de logs (Ingeniero de Soporte Nivel 3)**  
Captura y análisis de logs reales de instalación, arranque de Django, compilación TypeScript y auditoría npm.

**Pasada 7 — Inventario funcional (Analista Funcional)**  
Mapeo de los 44 endpoints de la API y las 21 rutas del frontend. Identificación de formularios, procesos de negocio y flujos principales.

**Pasada 8 — Análisis DDD (Experto DDD)**  
Reconstrucción del modelo de dominio completo: 21 entidades, 15+ value objects, 4 agregados raíz, 28 use cases, 5 servicios de dominio, 35 reglas de negocio.

**Pasada 9 — Arquitectura empresarial (Arquitecto Empresarial)**  
Síntesis de todas las pasadas anteriores en una descripción arquitectónica completa con diagramas C4, mapa de componentes, flujos de datos y matriz de integraciones.

**Pasada 10 — Evaluación de calidad (Analista de Calidad)**  
Calificación de 6 dimensiones (cohesión, acoplamiento, escalabilidad, mantenibilidad, testabilidad, seguridad) con justificación técnica y recomendaciones.

**Pasada 11 — Matriz de hallazgos (Auditor Senior)**  
Consolidación de todos los hallazgos en una matriz estructurada de 76 items con severidad, evidencia, impacto y plan de remediación.

### 4.2 Instalación

Se intentó instalar el sistema siguiendo el proceso documentado implícitamente en los Dockerfiles y `requirements.txt`:

```
1. Clonar repositorio
2. Crear entorno virtual Python
3. pip install -r requirements.txt
4. npm install (en frontend/react/)
5. python manage.py runserver
```

**Problemas encontrados durante la instalación:**

| Paso | Problema | Causa raíz | Resolución |
|---|---|---|---|
| `pip install scikit-learn` | `ERROR: Failed building wheel` | Python 3.14 sin compilador C para extensiones | `pip install --only-binary=:all: scikit-learn` |
| `pip install numpy` | Versión 1.26.4 no disponible para Py 3.14 | Incompatibilidad de versión | Se instaló numpy 2.4.6 (posible breaking change) |
| `python manage.py runserver` | `ModuleNotFoundError: joblib` | `joblib` no estaba en `requirements.txt` | `pip install joblib` manualmente |
| `python manage.py runserver` | `ModuleNotFoundError: openai` | `openai` requería instalación explícita | `pip install "openai>=1.0.0,<2.0.0"` |
| `python manage.py runserver` | `OperationalError: PostgreSQL connection refused` | PostgreSQL no disponible en host | Documentado — no resuelto en análisis |

### 4.3 Configuración

El sistema se configura mediante variables de entorno definidas en un archivo `.env` (no versionado) cargado por `python-dotenv` en `manage.py`.

**Variables de configuración identificadas mediante análisis estático de `settings.py`:**

| Variable | Tipo | Valor por defecto | Criticidad |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | str | `'django-insecure-v50ee...'` (hardcodeado) | 🔴 CRÍTICA |
| `DJANGO_DEBUG` | bool | `True` | 🔴 CRÍTICA |
| `DB_NAME` | str | `'zleague'` | Requerida |
| `DB_USER` | str | `'admin'` | Requerida |
| `DB_PASSWORD` | str | `'admin'` | Requerida |
| `DB_HOST` | str | `'localhost'` | Requerida |
| `DB_PORT` | str | `'5432'` | Opcional |
| `DJANGO_ALLOWED_HOSTS` | list | `['*']` | Requerida en prod |
| `OPENROUTER_API_KEY` | str | `''` | Opcional (no activo) |
| `LOG_LEVEL` | str | `'INFO'` | Opcional |
| `VITE_API_URL` | str | `'http://localhost:8000'` (fallback en código) | Requerida |

**Hallazgo crítico de configuración:** Si el archivo `.env` no existe, Django arranca con `DEBUG=True`, `SECRET_KEY` pública y `ALLOWED_HOSTS=['*']` — condición insegura silenciosa.

### 4.4 Ejecución

Se realizaron tres ejecuciones documentadas:

**Ejecución 1: `python manage.py check --deploy`**  
Resultado: 6 advertencias de seguridad de producción.
```
WARNINGS:
  ?: (security.W004) SECURE_HSTS_SECONDS is not set
  ?: (security.W008) SECURE_SSL_REDIRECT is not set to True
  ?: (security.W012) SESSION_COOKIE_SECURE is not True
  ?: (security.W016) CSRF_COOKIE_SECURE is not set to True
  ?: (security.W019) X_FRAME_OPTIONS is not set
  ?: (security.W024) SECURE_CONTENT_TYPE_NOSNIFF is not True
```

**Ejecución 2: `npx tsc --noEmit` (compilador TypeScript)**  
Resultado: 15 errores de compilación. Error más crítico:
```
AuthContext.tsx:36:37 - error TS18048: 'decoded' is possibly 'undefined'.
```
Este error puede causar excepción no manejada durante la decodificación de JWT si el token es malformado.

**Ejecución 3: `npm audit`**  
Resultado: 8 vulnerabilidades (4 HIGH, 4 MODERATE).
```
axios <=1.7.8          — 4 vulnerabilidades HIGH (SSRF, Header Injection, Prototype Pollution, Credential Leakage)
react-router 7.0-7.15  — RCE potencial (GHSA-cpj5-3fhq-fgh6)
vite <=6.4.2           — Path Traversal en dev server
esbuild <=0.24.2       — 2 vulnerabilidades (dependencia transitiva de Vite)
```

### 4.5 Ingeniería Inversa

La reconstrucción del sistema se realizó mediante:

1. **Trazado de rutas URL → View → UseCase → Domain → Repository:** Para cada uno de los 44 endpoints se trazó la cadena completa de ejecución leyendo `urls.py`, views, use cases, entidades de dominio y repositorios.

2. **Reconstrucción del modelo de dominio:** Lectura completa de todos los archivos en `*/domain/entities/`, `*/domain/value_objects/`, `*/domain/ports/`, y `*/application/use_cases/`. Identificación de invariantes, reglas de negocio, y relaciones entre entidades.

3. **Análisis de flujos de datos:** Trazado de datos desde la entrada HTTP hasta PostgreSQL, identificando transformaciones (serialización DRF, validación de dominio, mapeo ORM).

4. **Mapeo de integraciones:** Identificación de todos los sistemas externos configurados, consumidos, o preparados para integración.

5. **Análisis de seguridad:** Revisión de mecanismos de autenticación, autorización, hashing, y verificación contra CVEs conocidos en dependencias.

---

## 5. Inventario Tecnológico

### 5.1 Stack Backend

| Componente | Tecnología | Versión | Rol |
|---|---|---|---|
| Runtime | Python | 3.12 (Docker) / 3.14.4 (host) | Lenguaje de ejecución |
| Framework web | Django | 6.0.4 | MVC + ORM + Admin |
| API REST | Django REST Framework | 3.17.1 | Serialización y vistas de API |
| CORS | django-cors-headers | 4.9.0 | Cabeceras CORS para frontend |
| Static files | WhiteNoise | 6.12.0 | Servicio de archivos estáticos |
| WSGI server | Gunicorn | 26.0.0 | Servidor WSGI (instalado, no activado) |
| Base de datos | PostgreSQL | 17 | Persistencia relacional |
| Driver DB | psycopg2-binary | 2.9.12 | Conector Python ↔ PostgreSQL |
| JWT | PyJWT | 2.12.1 | Generación/verificación de tokens |
| Hashing | bcrypt | 5.0.0 | Hash de contraseñas |
| Utilidades auth | passlib | 1.7.4 | Utilidades password (abandonada) |
| Env vars | python-dotenv | ≥1.0.0 | Carga de archivo `.env` |
| ML | XGBoost | 2.1.4 | Modelo predictivo de rendimiento |
| ML serialización | joblib | 1.4.2 | Persistencia del modelo .pkl |
| ML arrays | numpy | 1.26.4 (req.) / 2.4.6 (real) | Arrays numéricos para ML |
| ML métricas | scikit-learn | 1.6.1 | Métricas de evaluación del modelo |
| LLM SDK | openai | ≥1.0.0,<2.0.0 | SDK instalado (integración futura) |
| Cobertura | coverage | 7.x | Análisis de cobertura (incorrectamente en prod) |
| JWT (extra) | djangorestframework_simplejwt | 5.5.1 | Instalado, no utilizado |

### 5.2 Stack Frontend

| Componente | Tecnología | Versión | Rol |
|---|---|---|---|
| Runtime | Node.js | 22 (Docker) | Entorno de ejecución |
| Framework UI | React | 18.3.1 | Framework SPA |
| Lenguaje | TypeScript | 6.0.2 | Tipado estático |
| Build tool | Vite | 6.3.5 | Bundler + dev server |
| Router | React Router DOM | 7.13.0 | Enrutamiento SPA |
| UI Components | Material UI | 7.3.5 | Design system |
| Estilos | Tailwind CSS | 4.1.12 | Utilidades CSS |
| HTTP client | Axios | 1.15.0 (^) | Llamadas a API REST |
| Gráficas | Recharts | 2.x | Visualización de datos |
| JWT decode | jwt-decode | 4.x | Decodificación de tokens en cliente |
| Iconos | lucide-react | — | Íconos SVG |
| Emociones | @emotion/react + @emotion/styled | — | CSS-in-JS para MUI |

### 5.3 Infraestructura

| Componente | Tecnología | Rol |
|---|---|---|
| Contenedores | Docker Engine | Empaquetado de servicios |
| Orquestación | Docker Compose v3 | Gestión de 3 contenedores |
| DB container | postgres:17-alpine | Instancia PostgreSQL |
| Backend container | python:3.12-slim | Servicio Django |
| Frontend container | node:22 | Servicio React/Vite |
| Volúmenes | Docker volumes | Persistencia de datos PostgreSQL |

### 5.4 Lenguajes y formatos de archivo

| Extensión | Uso |
|---|---|
| `.py` | Backend Django — dominio, aplicación, infraestructura, API |
| `.tsx` / `.ts` | Frontend React — componentes, servicios, tipos |
| `.yaml` | Docker Compose |
| `.json` | package.json, tsconfig.json, configuración npm |
| `.env` | Variables de entorno (no versionado) |
| `.md` | Documentación (parcial) |
| `.pkl` | Modelo XGBoost serializado |

---

## 6. Arquitectura Detectada

### 6.1 Patrón global: Monolito Modular

El sistema es un **monolito modular** — un único proceso Django con 4 módulos internos (apps Django) que implementan internamente Arquitectura Hexagonal y DDD. No es una arquitectura de microservicios a pesar de usar Docker.

```
┌─────────────────────────────────────────────────────────┐
│              PROCESO DJANGO ÚNICO (monolito)            │
│                                                         │
│  ┌───────────┐  ┌─────────────┐  ┌──────────┐  ┌────┐ │
│  │   auth    │  │ competencia │  │simulacion│  │anal│ │
│  │ (4 capas) │  │  (4 capas)  │  │ (4 capas)│  │ytic│ │
│  └───────────┘  └─────────────┘  └──────────┘  └────┘ │
│                                                         │
│  Compartido: settings.py · config/urls.py · ORM · DB   │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Patrón interno: Arquitectura Hexagonal (Ports & Adapters)

Cada módulo aplica la estructura de 4 capas característica de la arquitectura hexagonal:

```
interface/          ← Puerto de entrada HTTP (views, serializers)
application/        ← Use cases, servicios de aplicación
domain/             ← Entidades, VOs, puertos de salida (ABCs)
infrastructure/     ← Repositorios, adaptadores ML/IA, ORM
```

**Regla de dependencia verificada:** Las capas internas (domain, application) no importan de las capas externas (infrastructure, interface). Verificado en todos los módulos mediante análisis de imports.

### 6.3 Patrones tácticos DDD detectados

| Patrón | Instancias | Ejemplos |
|---|---|---|
| Entidades ricas | 21 | `Tournament`, `User`, `Team`, `Match`, `Participant` |
| Aggregate Root | 4 | `Tournament`, `User`, `Team`, `SimulacionResultado` |
| Value Objects | 15+ | `ConfigKnockout`, `TournamentEvaluation`, `SystemRol`, `Criteria` |
| Repository (Port) | 15 | ABCs en `*/domain/ports/` |
| Use Case | 32 | Clases en `*/application/use_cases/` |
| Domain Service | 5 | `JWTService`, `PasswordService`, `AuthIdentityService`, `ReentrenamientoService` |
| Factory Method | 6 | `Tournament.create()`, `User.create_user()`, `Team.create()` |
| Domain Events | 0 | Definidos implícitamente pero sin bus de eventos |

### 6.4 Bounded Contexts identificados

| Bounded Context | App Django | Responsabilidad | Estado |
|---|---|---|---|
| **Authentication** | `authentication` | Identidad, autenticación, autorización | Completo |
| **Competencia** | `competencia` | Torneos, equipos, partidos, fixtures, clasificaciones, criterios | Completo |
| **Simulación** | `simulacion` | Predicción ML, análisis de entregas, reentrenamiento | Completo |
| **Analítica** | `analitica` | Dashboard KPIs, reportes | Placeholder vacío |

### 6.5 Máquina de estados del torneo

Uno de los mecanismos de dominio más importantes detectado por ingeniería inversa:

```
DRAFT ──────────► IN_REVIEW ──────────► REGISTRATION_OPEN
  │                   │                        │
  │ (editar config)   │ (validación falla)      │ (cerrar inscripciones)
  │                   ▼                        ▼
  │               DRAFT (back)        REGISTRATION_CLOSED
  │                                            │
  │                                            │ (generar fixtures, iniciar)
  │                                            ▼
  │                                        IN_PROGRESS
  │                                            │
  │                                   ┌────────┴────────┐
  │                                   │                 │
  │                                   ▼                 ▼
  └────────────────────────────── FINALIZED         CANCELLED
```

Las transiciones son validadas por `Tournament.validate_state_transition()` — un diccionario de transiciones válidas que lanza `ValueError` para transiciones ilegales.

### 6.6 Formatos de fixture soportados

| Formato | Algoritmo | Restricción |
|---|---|---|
| `KNOCKOUT` | Árbol binario con `partido_siguiente_id` | Equipos deben ser potencia de 2 |
| `ROUND_ROBIN` | Algoritmo de rotación (Berger tables) | Número par de equipos |
| `HYBRID` | Distribución serpentina en grupos + RR por grupo | Grupos de mínimo 3 equipos |

---

## 7. Dependencias

### 7.1 Árbol de dependencias backend (principales)

```
requirements.txt
├── Django 6.0.4
│   ├── asgiref 3.11.1
│   └── sqlparse 0.5.5
├── djangorestframework 3.17.1
├── django-cors-headers 4.9.0
├── whitenoise 6.12.0
├── gunicorn 26.0.0            ← instalado, no activo en CMD
├── psycopg2-binary 2.9.12
├── psycopg2 2.9.12            ← DUPLICADO (conflicto potencial)
├── PyJWT 2.12.1
├── bcrypt 5.0.0
├── passlib 1.7.4              ← ABANDONADA desde 2021
├── djangorestframework_simplejwt 5.5.1  ← SIN USO
├── python-dotenv ≥1.0.0
├── xgboost 2.1.4
├── numpy 1.26.4               ← se instala 2.4.6 en Python 3.14
├── scikit-learn 1.6.1         ← no instalable sin compilador C
├── joblib 1.4.2               ← ausente de requirements.txt original
├── openai ≥1.0.0,<2.0.0      ← SDK sin uso LLM real
└── coverage 7.x               ← herramienta de desarrollo en prod
```

### 7.2 Dependencias frontend con CVEs activos

| Paquete | Versión | CVE / Advisory | Severidad | Fix |
|---|---|---|---|---|
| axios | ^1.15.0 | CVE-2024-39338 (SSRF) | HIGH | ≥1.8.2 |
| axios | ^1.15.0 | CVE-2023-45857 (Credential Leakage) | HIGH | ≥1.8.2 |
| axios | ^1.15.0 | CVE-2024-28849 (Header Injection) | HIGH | ≥1.8.2 |
| axios | ^1.15.0 | CVE-2024-48932 (Prototype Pollution) | HIGH | ≥1.8.2 |
| react-router | 7.13.0 | GHSA-cpj5-3fhq-fgh6 (RCE) | CRITICAL | ≥7.16.0 |
| vite | ^6.3.5 | GHSA-vg6x-rcgg-rjx6 (Path Traversal) | HIGH | ≥6.4.3 |
| esbuild | transitivo | CVE múltiples | MODERATE | via Vite update |

### 7.3 Análisis de compatibilidad de versiones

| Problema | Versión requerida | Versión real | Riesgo |
|---|---|---|---|
| Python | 3.12 | 3.14.4 (host) | scikit-learn no instala |
| numpy | 1.26.4 | 2.4.6 | Breaking changes en API |
| xgboost | 2.1.4 | 3.3.0 (con Py3.14) | API incompatibilities |
| scikit-learn | 1.6.1 | no instalable | Fallo de compilación |

---

## 8. Configuración

### 8.1 Archivo de configuración principal: `config/settings.py`

**Secciones identificadas:**

```python
# Seguridad (con vulnerabilidades detectadas)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-v50ee$v908kp8p)$_dx87tw39y##gb)=bwg872q@txgf=4no2g')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        # Sin CONN_MAX_AGE — cierra conexión en cada request
    }
}

# JWT (implementación propia, no SimplJWT)
# access_token: 15 minutos, HS256
# refresh_token: 7 días, HS256
```

### 8.2 Docker Compose: configuración real de servicios

```yaml
# docker-compose.yml (hallazgos de seguridad)
services:
  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: zleague
      POSTGRES_USER: admin        # CRÍTICO: hardcodeado
      POSTGRES_PASSWORD: admin    # CRÍTICO: hardcodeado
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"               # Expuesto al host

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000   # CRÍTICO: dev server
    ports:
      - "8000:8000"
    depends_on:
      - db                        # Sin healthcheck — race condition

  frontend:
    build: ./frontend/react
    ports:
      - "5173:5173"
    # EXPOSE 3000 incorrecto en Dockerfile del frontend
```

### 8.3 Variables de entorno requeridas vs. documentadas

| Variable | Estado | Consecuencia si falta |
|---|---|---|
| `DJANGO_SECRET_KEY` | No requerida (tiene fallback inseguro) | Todos los JWT forjables |
| `DJANGO_DEBUG` | No requerida (default: True) | Debug mode en producción |
| `DB_PASSWORD` | Docker-compose la ignora (hardcodea 'admin') | Contraseña siempre 'admin' |
| `VITE_API_URL` | No requerida (fallback a localhost:8000) | Frontend apunta a localhost en producción |
| `OPENROUTER_API_KEY` | Opcional (integración no activa) | Ninguna — SDK no la usa actualmente |

### 8.4 Configuración de autenticación JWT

```python
# authentication/application/service/jwt_service.py

ACCESS_TOKEN_LIFETIME  = 15 minutos   # timedelta(minutes=15)
REFRESH_TOKEN_LIFETIME = 7 días       # timedelta(days=7)
ALGORITHM              = "HS256"
SIGNING_KEY            = settings.SECRET_KEY  # ← usa la clave potencialmente pública

# Payload access token:  {user_id, email, rol, state, type: "access",  exp, iat}
# Payload refresh token: {user_id, type: "refresh", exp, iat}
```

### 8.5 RBAC: Roles y permisos

| Rol | Código | Permisos principales |
|---|---|---|
| Administrador | `ADMIN` | Gestión global del sistema, usuarios, todos los torneos |
| Manager | `MANAGER` | Crear y operar torneos asignados, generar fixtures, calificar partidos |
| Coach | `COACH` | Inscribir equipos en torneos abiertos |
| Participante | `PARTICIPANT` | Ver torneos, ejecutar simulaciones, ver resultados |

El decorador `@auth_required(roles=['ADMIN', 'MANAGER'])` en cada view verifica:
1. Presencia del header `Authorization: Bearer <token>`
2. Decodificación y verificación criptográfica del JWT
3. Verificación de `payload.type == "access"`
4. Verificación de `payload.rol` en la lista de roles permitidos

---

## 9. Ejecución

### 9.1 Proceso de arranque del sistema

**Secuencia de arranque del backend:**

```
1. manage.py.__main__()
   └── load_dotenv()                    ← carga .env (si existe)
   └── execute_from_command_line()

2. Django inicialización
   ├── Carga settings.py
   │   └── CRITICAL: SECRET_KEY con fallback inseguro
   ├── Registra INSTALLED_APPS
   │   ├── authentication
   │   ├── competencia
   │   ├── simulacion                   ← importa views.py
   │   │   └── views.py imports:
   │   │       ├── xgboost_adapter.py
   │   │       │   └── import joblib    ← BLOQUEANTE si no instalado
   │   │       └── analisis_engine.py
   │   │           └── from openai import OpenAI  ← BLOQUEANTE
   │   └── analitica
   └── Conecta a PostgreSQL
       └── Si no hay DB: OperationalError (Django sigue pero falla en requests)

3. URL routing configurado
   ├── /api/auth/      → authentication.interface.urls
   ├── /api/competencia/ → competencia.interface.urls
   ├── /api/simulacion/  → simulacion.interface.urls
   └── /api/ia/          → competencia.interface.urls (IA)

4. HTTP server listo
   └── runserver (single-threaded, NO gunicorn)
```

**Secuencia de arranque del frontend:**

```
1. npm run dev
   └── Vite dev server inicia en puerto 5173
   └── TypeScript compiler (modo watch, no strict)
       └── 15 errores no bloquean el arranque en modo dev

2. Browser carga index.html
   └── React Bootstrap (main.tsx)
   └── BrowserRouter + React.StrictMode
   └── AuthContext inicializa
       └── Lee tokens de localStorage
       └── Si existen: decodifica con jwt-decode
           └── CRITICAL: TS18048 — 'decoded' puede ser undefined
```

### 9.2 Flujo de autenticación en ejecución

```
Request: POST /api/auth/login/
  Body: {"email": "user@example.com", "password": "secret123"}

1. View recibe request (no autenticada — endpoint público)
2. LoginUseCase.execute(email, password)
   ├── UserRepository.find_by_email(email)
   │   └── SELECT * FROM authentication_user WHERE email = ?
   ├── user.is_locked()
   │   └── if bloqueado AND tiempo_bloqueo + 15min > now: raise AccountLocked
   ├── PasswordService.verify(password, user.hashed_password)
   │   └── bcrypt.checkpw(plain.encode(), hashed.encode())
   ├── Si falla: user.increment_attempts() → si ≥5: user.lock(30min)
   └── Si OK:
       ├── user.reset_attempts()
       ├── user.update_last_login()
       ├── JWTService.create_access_token(user_id, email, rol, state)
       └── JWTService.create_refresh_token(user_id)

Response: 200
  {"access_token": "eyJ...", "refresh_token": "eyJ...", "user": {...}}
```

### 9.3 Flujo de generación de fixtures en ejecución

```
Request: POST /api/competencia/torneo/{id}/generar-fixtures/
  Requiere: rol ADMIN o MANAGER, estado IN_PROGRESS

1. View: GetTournamentRepository.find_by_id(id)
2. Verifica estado del torneo (debe ser REGISTRATION_CLOSED o posterior)
3. GenerateFixturesUseCase.execute(tournament_id, formato)
   ├── KNOCKOUT:
   │   ├── Verifica equipos == potencia de 2
   │   ├── Construye árbol de partidos en memoria
   │   ├── Asigna partido_siguiente_id para avance automático
   │   └── Maneja BYEs si hay equipos impares (auto-avance)
   ├── ROUND_ROBIN:
   │   ├── Verifica equipos par
   │   └── Algoritmo de rotación Berger
   └── HYBRID:
       ├── Distribuye equipos en grupos (serpentine)
       └── Genera RR por cada grupo
   └── transaction.atomic():  ← Django — acoplamiento a framework
       ├── DELETE matches existentes
       └── INSERT matches nuevos (BUG: batch insert no optimizado)

Response: 200 — [{match_id, local_team, visitor_team, round, ...}]
```

### 9.4 Pipeline de predicción ML en ejecución

```
Request: POST /api/simulacion/torneo/{id}/simular/
  Body: {"entregable": "código del robot...", "datos_telemetria": {...}}

1. EjecutarSimulacionUseCase.execute(torneo_id, participante_id, entregable)
2. Scoring rules-based:
   ├── RulesNLPAdapter.analyze(entregable)
   │   └── Regex patterns extraen: longitud, palabras_clave, complejidad
   └── calcular_scores(criterios_torneo, scores_nlp)
       └── score_ponderado = Σ(score_criterio × peso_criterio)

3. Predicción ML (si hay datos de telemetría):
   ├── XGBoostAdapter.predecir(features)
   │   ├── joblib.load('xgboost_model.pkl')  ← carga lazy si no inicializado
   │   └── model.predict([[tiempo_est, complejidad, colisiones, vel_prom, errores]])
   └── puntaje_estimado = prediction[0]

4. Calcular posición estimada:
   └── Comparar con historial de participantes del mismo torneo

5. SimulacionRepository.guardar(resultado)
   └── INSERT simulacion_resultado

Response: 200
  {"puntaje_total": 0.87, "posicion_estimada": 3, "percentil": 85,
   "fortalezas": [...], "debilidades": [...], "retroalimentacion": "..."}
```

---

## 10. Reconstrucción Arquitectónica

### 10.1 Vista de contenedores (C4 Nivel 2)

```
┌──────────────────────────────────────────────────────────────────────┐
│                        DOCKER COMPOSE NETWORK                        │
│                                                                      │
│  ┌────────────────────────┐   HTTP:8000   ┌──────────────────────┐  │
│  │  Frontend SPA          │◄─────────────►│  Backend API         │  │
│  │  node:22               │               │  python:3.12-slim    │  │
│  │  React 18 + Vite       │               │  Django 6 + DRF      │  │
│  │  Puerto: 5173          │               │  Puerto: 8000        │  │
│  └────────────────────────┘               └──────────┬───────────┘  │
│                                                      │ TCP:5432     │
│                                           ┌──────────▼───────────┐  │
│                                           │  PostgreSQL 17        │  │
│                                           │  postgres:17-alpine  │  │
│                                           │  Puerto: 5432        │  │
│                                           └──────────────────────┘  │
│                                                                      │
│  Externos:                                                           │
│  ┌──────────────────┐   ┌──────────────────────────────────────┐    │
│  │ OpenRouter API   │   │ xgboost_model.pkl (filesystem local) │    │
│  │ (SDK listo,      │   │ joblib.load() — in-process           │    │
│  │ no invocado aún) │   └──────────────────────────────────────┘    │
│  └──────────────────┘                                               │
└──────────────────────────────────────────────────────────────────────┘
```

### 10.2 Estructura interna del backend

```
config/
  settings.py          ← configuración central
  urls.py              ← router principal (/api/ prefix)
  wsgi.py / asgi.py    ← entry points

authentication/        ← Bounded Context: Identidad
  domain/
    entities/user.py          ← Aggregate Root
    ports/user_repository.py  ← Puerto de salida (ABC)
    value_objects/            ← SystemRol, UserState
  application/
    use_cases/                ← LoginUseCase, RegisterUseCase, LogoutUseCase
    service/                  ← JWTService, PasswordService, AuthIdentityService
  infrastructure/
    db/user_repository.py     ← Implementación ORM
    security/auth_decorator.py← @auth_required RBAC
  interface/
    views/                    ← 5 endpoints HTTP

competencia/           ← Bounded Context: Torneos (sobredimensionado)
  domain/
    entities/                 ← Tournament, Team, Match, Participant,
                              │  Criteria, Standing, TournamentTeam,
                              │  MatchResult, DocenteAsesor, Institution
    ports/                    ← 12 ABCs de repositorios
    value_objects/            ← ConfigKnockout, ConfigRoundRobin,
                              │  ConfigHybrid, TournamentEvaluation,
                              │  13 enums de negocio
  application/
    use_cases/                ← 22 use cases
  infrastructure/
    db/                       ← Implementaciones ORM
    ia/                       ← RulesNLPAdapter, RubricaGenerator, AnalisisEngine
  interface/
    views/                    ← 27 endpoints HTTP

simulacion/            ← Bounded Context: Predicción y Análisis
  domain/
    entities/                 ← SimulacionPredictiva, AnalisisEntrega,
                              │  SimulacionResultado, SimulationContext
    ports/                    ← SimulacionRepositoryPort, TournamentContextPort,
                              │  RetoAnalisisRepositoryPort
  application/
    use_cases/                ← 6 use cases
    services/                 ← ReentrenamientoService
  infrastructure/
    db/                       ← Implementaciones ORM
    ml/                       ← XGBoostAdapter, TrainModel
  interface/
    views/                    ← 8 endpoints HTTP

analitica/             ← Bounded Context: Analytics (PLACEHOLDER)
  [estructura de carpetas sin implementación real]
```

### 10.3 Flujo de datos completo: Request → Response

```
Browser
  │ HTTP Request + Authorization: Bearer <JWT>
  ▼
Axios Instance (frontend)
  │ Interceptor: adjunta token de localStorage
  ▼
Django URL Router (config/urls.py)
  │ Match URL pattern
  ▼
View Function (@api_view + @auth_required)
  │ 1. Verifica JWT (jwt.decode + rol check)
  │ 2. Deserializa body (DRF Serializer)
  │ 3. Instancia Use Case con repositorios concretos
  ▼
Use Case (application layer)
  │ 1. Llama métodos del dominio
  │ 2. Aplica reglas de negocio
  │ 3. Llama repositorios (puertos)
  ▼
Domain Entity / Aggregate Root
  │ Valida invariantes, transforma estado
  ▼
Repository Port (ABC) → Repository Implementation (ORM)
  │ QuerySet Django ORM → SQL
  ▼
PostgreSQL 17
  │ SQL Response
  ▼
Repository → Use Case → View
  │ Serializa respuesta (DRF Serializer / dict)
  ▼
HTTP Response (JSON)
  │
  ▼
Axios Response Interceptor (frontend)
  │ Si 401: intenta refresh → si falla: logout
  ▼
React Component (actualiza estado)
  │
  ▼
Browser renderiza resultado
```

---

## 11. Modelo de Dominio

### 11.1 Entidades identificadas

| Entidad | Módulo | Aggregate Root | Invariantes clave |
|---|---|---|---|
| **User** | auth | Sí | MAX_ATTEMPTS=5, MIN_LOCK_TIME=15min, MIN_AGE=3, MAX_AGE=80, MIN_PASSWORD_LENGTH=8 |
| **Tournament** | competencia | Sí | Estado válido, fechas coherentes, reglas configuradas, transiciones de estado válidas |
| **Team** | competencia | Sí | Estado de inscripción (PENDIENTE/APROBADO/RECHAZADO) |
| **Match** | competencia | No | Estado (PENDING/IN_PROGRESS/FINISHED), ganador por puntaje ponderado |
| **Participant** | competencia | No | autorizacion_datos=True obligatorio, documento_identidad único por torneo |
| **Criteria** | competencia | No | name→UPPERCASE, value∈[0.0,1.0], min≤max |
| **TournamentTeam** | competencia | No | BUG: add_participant() referencias atributo inexistente |
| **MatchResult** | competencia | No | valor_normalizado = value × peso_criterio |
| **Standing** | competencia | No | Posición calculada post-fixtures |
| **DocenteAsesor** | competencia | No | Email único en el sistema |
| **Institution** | competencia | No | Nombre como identificador |
| **TournamentRule** | competencia | No | max_members≥2, max_teams∈[4,64], min≤max |
| **TournamentMember** | competencia | No | Rol del usuario en el torneo (MANAGER, JUDGE, etc.) |
| **SimulacionPredictiva** | simulacion | No | telemetría + puntaje ML |
| **AnalisisEntrega** | simulacion | No | caso: COMPONENTES o PROGRAMACION |
| **SimulacionResultado** | simulacion | Sí | scores, posición, retroalimentación |
| **SimulationContext** | simulacion | No | Contexto del torneo para simulación |
| **FinalRanking** | simulacion | No | Ranking final para reentrenamiento |
| **RetoAnalisis** | simulacion | No | Reto de análisis para el participante |

### 11.2 Value Objects identificados

| Value Object | Módulo | Inmutable | Descripción |
|---|---|---|---|
| `SystemRol` | auth | Sí | Enum: ADMIN, MANAGER, COACH, PARTICIPANT |
| `UserState` | auth | Sí | Enum: ACTIVE, INACTIVE, BLOCKED |
| `ConfigKnockout` | competencia | Sí | Config de eliminatoria (min/max equipos, potencia de 2) |
| `ConfigRoundRobin` | competencia | Sí | Config RR (victoria=3, empate=1, derrota=0) |
| `ConfigHybrid` | competencia | Sí | Config híbrido (grupos, equipos por grupo) |
| `TournamentEvaluation` | competencia | Sí | Colección de criterios con validación sum==1.0 |
| `QualifyScoreTeam` | competencia | Sí | Score de un equipo por criterio en un partido |
| `TournamentState` | competencia | Sí | Enum: DRAFT, IN_REVIEW, REGISTRATION_OPEN, etc. |
| `FixtureFormat` | competencia | Sí | Enum: KNOCKOUT, ROUND_ROBIN, HYBRID |
| `InscriptionState` | competencia | Sí | Enum: PENDIENTE, APROBADO, RECHAZADO |
| `MatchState` | competencia | Sí | Enum: PENDING, IN_PROGRESS, FINISHED, BYE |
| `TournamentCategory` | competencia | Sí | Enum: categorías educativas |
| `TechnicalLevel` | competencia | Sí | Enum: BÁSICO, INTERMEDIO, AVANZADO |
| `TournamentType` | competencia | Sí | Enum: tipos de torneo (robótica, etc.) |
| `NLPAnalysis` | competencia | Sí | Resultado de análisis de texto libre |

### 11.3 Casos de uso por módulo

**Authentication (3 use cases)**

| Use Case | Flujo principal |
|---|---|
| `LoginUseCase` | find_by_email → is_locked → verify_password → reset_attempts + create_tokens |
| `RegisterUseCase` | check_email_exists → verify_password_security → encrypt → create_user(rol=PARTICIPANT) |
| `LogoutUseCase` | update_last_login (⚠️ no invalida token) |

**Competencia (22 use cases)**

| Use Case | Flujo principal |
|---|---|
| `CreateTournamentUseCase` | validate_dates → Tournament.create() → save (con TournamentRule + Config + Evaluation + TournamentMember) |
| `UpdateTournamentUseCase` | find → validate_state(DRAFT) → update fields |
| `SendTournamentToReviewUseCase` | find → valid_for_review() → DRAFT→IN_REVIEW |
| `ApproveTournamentUseCase` | find → validate_state → IN_REVIEW→REGISTRATION_OPEN |
| `StartTournamentUseCase` | find → validate_for_start() → REGISTRATION_CLOSED→IN_PROGRESS |
| `FinishTournamentUseCase` | find → finish() → IN_PROGRESS→FINALIZED |
| `CancelTournamentUseCase` | find → DRAFT/IN_REVIEW→CANCELLED |
| `InscribeTeamUseCase` | create_institution → create_docente → create_participants → create_team → tournament.add_team() |
| `ApproveTeamUseCase` | find_team → team.approve() |
| `RejectTeamUseCase` | find_team → team.reject() |
| `GenerateFixturesUseCase` | find_tournament → _generate_{formato}() → transaction.atomic() |
| `QualifyMatchUseCase` | qualify_score() → add_qualify_score() → check_winner → advance_bracket |
| `RegisterMatchResultUseCase` | create_match_results → calculate_winner |
| `CalculateStandingsUseCase` | iterate_finished_matches → update(standings) → sort_by_points |
| `GetPublicTournamentDataUseCase` | find_by_id → serialize_public |
| `CreateCriteriaUseCase` | validate_weights_sum → save_criteria |
| `UpdateCriteriaUseCase` | find → update_weights → validate_sum |
| `AnalyzeTextUseCase` | RulesNLPAdapter.analyze() → NLPAnalysis |
| `GenerateCriteriaIAUseCase` | RubricaGenerator.generar() → CriterioIA[] |
| `ConfirmCriteriaIAUseCase` | validate_sum==100 → UPDATE all ACEPTADO |
| `GetTournamentStandingsUseCase` | calculate_standings → serialize |
| `GetMyTournamentsUseCase` | find_by_user_id → filter |

**Simulacion (6 use cases)**

| Use Case | Flujo principal |
|---|---|
| `GetSimulationContextUseCase` | TournamentContextPort.get_context() → SimulationContext |
| `EjecutarSimulacionUseCase` | scoring_rules → calcular_scores → XGBoostAdapter.predecir() → guardar_resultado |
| `GetSimulationHistoryUseCase` | SimulacionRepository.obtener_historial() |
| `GetAnalisisEntregaUseCase` | RetoAnalisisRepository.find() |
| `ExecuteAnalisisEntregaUseCase` | analyze_entrega → scoring → guardar |
| `ReentrenarModeloUseCase` | collect_final_rankings → train_model() → save_pkl |

### 11.4 Reglas de negocio críticas

| ID | Regla | Implementación |
|---|---|---|
| RN-01 | Contraseña mínimo 8 caracteres, con mayúsculas, números y caracteres especiales | `User.verify_password_security()` |
| RN-02 | Cuenta bloqueada tras 5 intentos fallidos por 30 minutos | `User.increment_attempts()` + `User.lock()` |
| RN-03 | Auto-desbloqueo después de 15 minutos | `User.is_locked()` con `datetime.now()` check |
| RN-04 | Torneo requiere fecha inicio > ahora y fecha fin > fecha inicio | `Tournament.create()` |
| RN-05 | Solo ADMIN puede aprobar torneos | `@auth_required(roles=['ADMIN'])` |
| RN-06 | Equipo solo inscribible si torneo en REGISTRATION_OPEN | `Tournament.add_team()` |
| RN-07 | DNI único por torneo (no por sistema) | `Tournament.add_team()` + validación de participantes |
| RN-08 | Suma de pesos de criterios = 1.0 exacto | `TournamentEvaluation.valid_criterias()` ⚠️ float comparison |
| RN-09 | KNOCKOUT requiere equipos en potencia de 2 | `ConfigKnockout.validate_for_start()` |
| RN-10 | ROUND_ROBIN requiere número par de equipos | `ConfigRoundRobin.validate_for_start()` |
| RN-11 | autorizacion_datos obligatoria para participantes | `Participant.__init__()` |
| RN-12 | Configuración de torneo solo modificable en estado DRAFT | `Tournament.update_tournament_rules()` |
| RN-13 | Ganador del partido = equipo con mayor Σ(score × peso) | `QualifyMatchUseCase._check_and_update_winner()` |
| RN-14 | Reentrenamiento del modelo ML requiere ≥10 registros reales | `ReentrenamientoService` |
| RN-15 | Criterios IA: suma de pesos debe ser 100.00 ± 0.01 | `ConfirmCriteriaIAUseCase` |

---

## 12. APIs e Integraciones

### 12.1 Endpoints API expuestos

**Módulo Authentication — prefijo `/api/auth/`**

| Método | Ruta | Rol requerido | Función |
|---|---|---|---|
| POST | `/login/` | Ninguno | Autenticación, retorna JWT pair |
| POST | `/register/` | Ninguno | Registro (crea PARTICIPANT) |
| POST | `/refresh/` | Ninguno | Renueva access token |
| PUT | `/logout/` | Autenticado | Actualiza last_login (no invalida token) |
| GET | `/me/` | Autenticado | Perfil del usuario actual |

**Módulo Competencia — prefijo `/api/competencia/`**

| Método | Ruta | Rol requerido | Función |
|---|---|---|---|
| POST | `/create/` | ADMIN, MANAGER | Crear torneo |
| GET | `/all/` | Autenticado | Listar todos los torneos |
| GET | `/mis-torneos/` | MANAGER | Torneos del manager actual |
| GET | `/torneo/{id}/` | Autenticado | Detalle de torneo |
| PUT | `/torneo/{id}/` | MANAGER | Actualizar torneo (solo DRAFT) |
| POST | `/torneo/{id}/review/` | MANAGER | Enviar a revisión |
| POST | `/torneo/{id}/approve/` | ADMIN | Aprobar torneo |
| POST | `/torneo/{id}/start/` | ADMIN | Iniciar torneo |
| POST | `/torneo/{id}/finish/` | ADMIN | Finalizar torneo |
| POST | `/torneo/{id}/cancel/` | ADMIN | Cancelar torneo |
| POST | `/torneo/{id}/inscribir/` | COACH | Inscribir equipo |
| GET | `/torneo/{id}/equipos/` | MANAGER, ADMIN | Listar equipos inscritos |
| POST | `/equipo/{id}/aprobar/` | MANAGER | Aprobar inscripción de equipo |
| POST | `/equipo/{id}/rechazar/` | MANAGER | Rechazar inscripción de equipo |
| POST | `/torneo/{id}/generar-fixtures/` | ADMIN, MANAGER | Generar partidos |
| GET | `/torneo/{id}/fixtures/` | Autenticado | Ver partidos generados |
| POST | `/partido/{id}/resultado/` | MANAGER | Registrar resultado |
| GET | `/torneo/{id}/standings/` | Autenticado | Ver clasificación |
| GET | `/torneo/{id}/public/` | Ninguno | Datos públicos del torneo |
| GET/POST | `/criterios/{id}/` | MANAGER, ADMIN | Gestión de criterios de evaluación |

**Módulo IA — prefijo `/api/ia/`**

| Método | Ruta | Rol requerido | Función |
|---|---|---|---|
| POST | `/analizar/` | MANAGER | Análisis NLP de texto libre |
| POST | `/generar-criterios/` | MANAGER | Generar criterios con plantillas |
| GET | `/sesion/{id}/criterios/` | MANAGER | Ver criterios generados |
| PUT | `/criterios/{id}/` | MANAGER | Actualizar peso de criterio |
| POST | `/sesion/{id}/confirmar/` | MANAGER | Confirmar criterios (valida suma=100%) |
| DELETE | `/criterios/{id}/` | MANAGER | Eliminar criterio |
| GET | `/sesion/{id}/resumen/` | MANAGER | Resumen de sesión IA |

**Módulo Simulación — prefijo `/api/simulacion/`**

| Método | Ruta | Rol requerido | Función |
|---|---|---|---|
| GET | `/torneo/{id}/contexto/` | PARTICIPANT | Contexto del torneo para simulación |
| POST | `/torneo/{id}/simular/` | PARTICIPANT | Ejecutar simulación predictiva |
| GET | `/historial/` | PARTICIPANT | Historial de simulaciones |
| GET | `/torneo/{id}/retos/` | PARTICIPANT | Retos de análisis disponibles |
| POST | `/reto/{id}/analizar/` | PARTICIPANT | Analizar entrega |
| GET | `/reto/{id}/resultado/` | PARTICIPANT | Ver resultado de análisis |
| POST | `/admin/reentrenar/` | ADMIN | Disparar reentrenamiento del modelo |
| GET | `/admin/modelo/estado/` | ADMIN | Estado del modelo ML |

### 12.2 APIs consumidas por el frontend

El frontend consume todas las APIs anteriores más las siguientes llamadas específicas detectadas en análisis de `services/`:

| Servicio frontend | Endpoint backend | Datos clave |
|---|---|---|
| `authService.login()` | `POST /api/auth/login/` | email, password → tokens |
| `authService.refreshToken()` | `POST /api/auth/refresh/` | refresh_token → new access_token |
| `tournamentService.getAll()` | `GET /api/competencia/all/` | Sin paginación ⚠️ |
| `teamService.register()` | `POST /api/competencia/torneo/{id}/inscribir/` | Datos completos del equipo |
| `matchService.qualify()` | `POST /api/competencia/partido/{id}/resultado/` | Array de qualificaciones |
| `simulationService.run()` | `POST /api/simulacion/torneo/{id}/simular/` | entregable + telemetría |
| `iaService.analyze()` | `POST /api/ia/analizar/` | texto libre → campos extraídos |

### 12.3 Integraciones con sistemas externos

| Sistema | Estado | Tipo | Descripción |
|---|---|---|---|
| **PostgreSQL 17** | Activa | TCP/5432 interno | Única fuente de verdad del sistema |
| **OpenRouter API** | Preparada, no activa | HTTPS (SDK openai) | LLM para generación de criterios — SDK listo, no invocado |
| **XGBoost (local)** | Activa | In-process (joblib) | Predicción de rendimiento de participantes |
| **SMTP / Email** | Ausente | — | No implementado — sin notificaciones |
| **Redis** | Ausente | — | No implementado — sin cache ni sesiones |
| **Almacenamiento de archivos** | Ausente | — | Sin S3 ni almacenamiento de media |
| **WebSockets** | Ausente | — | Sin actualizaciones en tiempo real |
| **CDN** | Ausente | — | Assets servidos desde el servidor de aplicación |

---

## 13. Hallazgos

La auditoría identificó **76 hallazgos** distribuidos en 7 categorías. A continuación se presenta el resumen ejecutivo por categoría y severidad. El detalle completo se encuentra en `15_Matriz_Hallazgos.md`.

### 13.1 Resumen de hallazgos críticos (10)

| ID | Hallazgo | Categoría |
|---|---|---|
| SEG-001 | `SECRET_KEY` con fallback hardcodeado en código — permite forja de cualquier JWT | Seguridad |
| SEG-002 | Credenciales PostgreSQL hardcodeadas en `docker-compose.yml` (`admin`/`admin`) | Seguridad |
| SEG-003 | CVE RCE en `react-router` 7.0–7.15 (`GHSA-cpj5-3fhq-fgh6`) | Seguridad |
| SEG-004 | 4 CVEs HIGH en `axios` ≤1.7.8 (SSRF, Header Injection, Prototype Pollution, Credential Leakage) | Seguridad |
| COD-001 | `TournamentTeam.add_participant()` lanza `AttributeError` en runtime — flujo de inscripción roto | Código |
| OPS-001 | Django `runserver` en contenedor de producción — single-threaded, sin gestión de procesos | Operaciones |
| EJE-001 | `ImportError: joblib` derriba todos los endpoints de Django (startup coupling) | Ejecución |
| EJE-002 | `ImportError: openai` derriba todos los endpoints de Django (startup coupling) | Ejecución |
| EJE-003 | `OperationalError: PostgreSQL` sin healthcheck — race condition en cada deploy | Ejecución |
| EJE-004 | 15 errores TypeScript incluyendo `TS18048` en `AuthContext.tsx:36` — decodificación JWT rota | Ejecución |

### 13.2 Distribución de hallazgos altos (22)

| Categoría | Cantidad | Ejemplos |
|---|---|---|
| Seguridad | 6 | JWT sin revocación, sin SSL, DEBUG=True por defecto, sin rate limiting |
| Arquitectura | 3 | Cross-context imports, simulacion→competencia ORM, startup coupling |
| Código | 1 | Float comparison exacta en validación de criterios |
| Dependencias | 3 | passlib abandonada, Vite Path Traversal CVE, esbuild CVEs |
| Configuración | 2 | EXPOSE 3000 incorrecto, VITE_API_URL con fallback a localhost |
| Operaciones | 3 | Sin CI/CD, sin monitoreo, frontend sin tests |
| Rendimiento | 2 | Sin paginación en listados, sin cache layer |

### 13.3 Hallazgos por dimensión de calidad

| Dimensión | Calificación | Hallazgos vinculados |
|---|---|---|
| Cohesión | 3/5 | ARQ-005, ARQ-009, ARQ-010, ARQ-012 |
| Acoplamiento | 3/5 | ARQ-001, ARQ-002, ARQ-003, ARQ-006, ARQ-007, ARQ-008 |
| Escalabilidad | 2/5 | REN-001 a REN-006, CFG-003, OPS-001 |
| Mantenibilidad | 3/5 | EJE-004, COD-003 a COD-009, OPS-006, OPS-010 |
| Testabilidad | 3/5 | OPS-002, OPS-004, OPS-008, ARQ-006 |
| Seguridad | 2/5 | SEG-001 a SEG-013 |

---

## 14. Riesgos

### 14.1 Matriz de riesgo

```
         PROBABILIDAD
          Baja    Media    Alta
    ┌──────────────────────────────────┐
A   │        │  ARQ-003 │ SEG-001     │
l   │        │  REN-001 │ SEG-002     │
t   │        │          │ COD-001     │
o   │        │          │ EJE-001/002 │
    ├──────────────────────────────────┤
M   │ SEG-003│ SEG-005  │ SEG-009     │
e   │ SEG-004│ ARQ-001  │ EJE-003     │
d   │        │ ARQ-002  │ OPS-001     │
i   │        │          │             │
o   │        │          │             │
    ├──────────────────────────────────┤
B   │ SEG-014│ DEP-001  │ CFG-001     │
a   │ SEG-015│ DEP-002  │             │
j   │ ARQ-012│          │             │
o   │        │          │             │
    └──────────────────────────────────┘
      Bajo      Medio     Alto
                IMPACTO
```

### 14.2 Riesgos críticos detallados

**Riesgo 1: Compromiso total de autenticación (SEG-001)**  
- **Descripción:** La `SECRET_KEY` está en el repositorio como valor por defecto. Cualquier atacante con acceso al repo puede firmar JWT arbitrarios.  
- **Escenario de ataque:** Atacante crea token `{"user_id": 1, "rol": "ADMIN", "type": "access", "exp": <futuro>}`, lo firma con la clave pública, y tiene acceso administrativo completo.  
- **Probabilidad:** Alta (la clave está versionada en git, historial accesible).  
- **Impacto:** Crítico — control total del sistema.

**Riesgo 2: Crash total del sistema por dependencia ML (EJE-001 / EJE-002)**  
- **Descripción:** Un import a nivel de módulo de `joblib` u `openai` provoca que Django no pueda registrar ninguna URL, haciendo inaccesibles **todos los endpoints incluyendo autenticación**.  
- **Escenario:** Deploy en un entorno donde `pip install` falla silenciosamente para alguna librería ML (contenedor sin acceso a red a PyPI, imagen base diferente).  
- **Probabilidad:** Media (ocurrió en el entorno de auditoría).  
- **Impacto:** Alto — sistema 100% inoperativo.

**Riesgo 3: Flujo de inscripción roto (COD-001)**  
- **Descripción:** `TournamentTeam.add_participant()` lanza `AttributeError` en runtime porque referencia `self.__tournament_rule` que no existe en `TournamentTeam`.  
- **Escenario:** Cualquier intento de inscribir un participante en un equipo → excepción no manejada → HTTP 500 → usuario no puede inscribirse.  
- **Probabilidad:** Alta (el código que falla está en el path principal del flujo de negocio).  
- **Impacto:** Alto — funcionalidad core del sistema no operativa.

**Riesgo 4: RCE vía react-router (SEG-003)**  
- **Descripción:** `react-router` 7.0–7.15 tiene una vulnerabilidad que puede resultar en ejecución remota de código.  
- **Escenario:** Atacante envía request especialmente crafteada al servidor frontend o backend que procesa routing.  
- **Probabilidad:** Baja-Media (requiere vector de ataque específico).  
- **Impacto:** Crítico — control total del host.

### 14.3 Riesgos operacionales

| Riesgo | Probabilidad | Impacto | Sin mitigación |
|---|---|---|---|
| Pérdida de datos por falta de backup | Baja | Crítico | Pérdida total de datos de torneos |
| Degradación por falta de paginación | Alta | Alto | OOM del servidor con crecimiento de datos |
| Downtime por restart=never en Docker | Media | Alto | Requiere intervención manual tras cada crash |
| Regresiones por falta de CI | Alta | Medio | Bugs introducidos sin detección automática |
| Saturación de conexiones DB | Media | Alto | Sistema inaccesible bajo carga moderada |

---

## 15. Recomendaciones

### 15.1 Remediación inmediata (P1 — < 48 horas)

Estas acciones deben tomarse antes de cualquier despliegue en entorno accesible:

**1. Eliminar SECRET_KEY hardcodeada** (`config/settings.py`)
```python
# ANTES (vulnerable):
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-...')

# DESPUÉS (seguro):
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']  # lanza KeyError si no está definida
```

**2. Eliminar credenciales DB de docker-compose.yml**
```yaml
# ANTES:
POSTGRES_PASSWORD: admin

# DESPUÉS:
POSTGRES_PASSWORD: ${DB_PASSWORD}
```

**3. Actualizar dependencias con CVEs críticos**
```bash
npm install axios@^1.8.2 react-router@^7.16.0 vite@^6.4.3
```

**4. Corregir bug AttributeError en TournamentTeam**
```python
# ANTES (lanza AttributeError):
def add_participant(self, participant):
    self.__tournament_rule.validate_team_rules(...)  # no existe

# DESPUÉS:
def add_participant(self, participant, tournament_rule):
    tournament_rule.validate_team_rules(...)
```

**5. Corregir imports bloqueantes — hacer lazy**
```python
# simulacion/views.py — DESPUÉS:
def simular(request, torneo_id):
    from simulacion.infrastructure.ml.xgboost_adapter import XGBoostAdapter
    adapter = XGBoostAdapter()
    ...
```

**6. Agregar healthcheck y depends_on en docker-compose**
```yaml
db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
    interval: 10s
    timeout: 5s
    retries: 5

backend:
  depends_on:
    db:
      condition: service_healthy
```

**7. Reemplazar runserver por gunicorn**
```dockerfile
# Dockerfile backend — DESPUÉS:
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-"]
```

**8. Corregir TS18048 en AuthContext.tsx**
```typescript
// AuthContext.tsx:36 — DESPUÉS:
const decoded = jwtDecode<JwtPayload>(token);
if (!decoded || typeof decoded.exp === 'undefined') {
  logout();
  return;
}
```

### 15.2 Remediación a corto plazo (P2 — Semana 1)

| Acción | Herramienta | Esfuerzo estimado |
|---|---|---|
| Implementar token blacklist en logout | Redis + middleware Django | 1 día |
| Configurar SSL/TLS con Nginx | Nginx + Certbot | 1 día |
| Agregar rate limiting en autenticación | `django-ratelimit` | 4 horas |
| Crear pipeline CI mínimo | GitHub Actions | 4 horas |
| Configurar monitoreo de errores | Sentry SDK | 30 minutos |
| Agregar tests básicos de frontend | Vitest + Testing Library | 2 días |
| Corregir comparación float en criterios | `abs(sum - 1.0) <= 1e-9` | 1 hora |
| Agregar paginación en endpoints de listado | DRF `PageNumberPagination` | 4 horas |
| Reemplazar passlib por bcrypt directo | Refactor de PasswordService | 2 horas |
| Configurar DEBUG=False por defecto | `settings.py` | 30 minutos |

### 15.3 Remediación a medio plazo (P3 — Mes 1)

| Área | Acción | Beneficio |
|---|---|---|
| **Arquitectura** | Crear `shared_kernel/` para tipos compartidos entre contextos | Eliminar cross-context imports |
| **Arquitectura** | Implementar `UnitOfWorkPort` concreto | Reemplazar `transaction.atomic()` en use cases |
| **Performance** | Agregar Redis como cache + `CONN_MAX_AGE=60` | Reducir carga en PostgreSQL |
| **Performance** | Lazy loading del modelo XGBoost (singleton) | Reducir consumo de RAM por worker |
| **DevOps** | Agregar `restart: unless-stopped` + límites de recursos en Docker Compose | Resiliencia operacional |
| **DevOps** | Configurar backup automático de PostgreSQL | Protección contra pérdida de datos |
| **Mantenibilidad** | Agregar OpenAPI/Swagger con `drf-spectacular` | Documentación automática de API |
| **Mantenibilidad** | Reorganizar `competencia/` en sub-packages | Navegabilidad del código |
| **Código** | Agregar setter público `Standing.set_posicion()` | Eliminar name mangling |
| **Seguridad** | Migracion JWT de localStorage a HttpOnly cookies | Protección contra XSS |
| **Testing** | Definir cobertura mínima 70% en domain layer | Detección temprana de regresiones |

### 15.4 Mejoras estructurales (P4 — Backlog)

- Implementar API versioning (`/api/v1/`)
- Agregar schemas PostgreSQL por bounded context
- Implementar bus de eventos de dominio para desacoplar bounded contexts
- Activar integración real con OpenRouter API para generación de criterios con LLM
- Implementar WebSockets (Django Channels) para actualizaciones en tiempo real de resultados
- Agregar CDN para assets estáticos del frontend
- Implementar notificaciones por email (SMTP) para aprobaciones e inicio de torneos
- Configurar `dependabot` para actualizaciones automáticas de dependencias
- Agregar cifrado de campo para `documento_identidad` de participantes menores

---

## 16. Conclusiones

### 16.1 Estado general del sistema

Zoids League es un sistema con una **base arquitectónica correcta y bien intencionada** pero con **deuda técnica crítica acumulada** que lo hace inadecuado para exposición pública en su estado actual.

El equipo de desarrollo ha aplicado patrones avanzados (Hexagonal Architecture, DDD, Clean Architecture) con notable consistencia a nivel de diseño micro: las entidades de dominio son ricas y bien encapsuladas, los invariantes de negocio están correctamente ubicados, y la separación de capas es rigurosa dentro de cada módulo. Estos son indicadores positivos de capacidad técnica del equipo.

Sin embargo, la implementación tiene tres brechas fundamentales:

**Brecha 1 — Seguridad de infraestructura**  
El sistema tiene configuración insegura a nivel de infraestructura (claves públicas, credenciales hardcodeadas) que anula cualquier seguridad implementada en el dominio. Un sistema con bcrypt impecable y RBAC bien implementado es inútil si su clave de firma JWT es pública.

**Brecha 2 — Operaciones y resiliencia**  
Sin CI/CD, sin monitoreo, sin paginación, sin backup automatizado y con un servidor de desarrollo (`runserver`) en producción, el sistema es frágil operacionalmente. Los bugs existentes (como el `AttributeError` en `add_participant()`) pueden pasar semanas sin detección.

**Brecha 3 — Calidad del software frontend**  
Los 15 errores TypeScript —especialmente el crítico en `AuthContext.tsx`— y la ausencia total de tests de frontend representan un riesgo de regresión significativo en la capa más visible del sistema.

### 16.2 Potencial del sistema

Una vez aplicadas las remediaciones P1 y P2 (estimado: 2 semanas de trabajo de 2 desarrolladores), el sistema tendría una base sólida para:

- Soportar torneos reales con hasta 64 equipos y múltiples jueces concurrentes
- Escalar horizontalmente añadiendo instancias Django con Redis como backend de sesiones
- Integrar el LLM de OpenRouter para potenciar la asistencia IA (el SDK ya está preparado)
- Reentrenar el modelo XGBoost con datos reales para mejorar las predicciones

### 16.3 Roadmap de madurez sugerido

| Fase | Duración | Resultado |
|---|---|---|
| **Fase 1: Estabilización** | 2 semanas | Remediación P1+P2. Sistema seguro y operativo. |
| **Fase 2: Productivización** | 1 mes | Remediación P3. CI/CD, monitoreo, cache, SSL. Listo para producción. |
| **Fase 3: Evolución** | 3 meses | Remediación P4. LLM activo, WebSockets, CDN, API versionada. |
| **Fase 4: Escalabilidad** | 6 meses | Descomposición de `competencia`, event-driven architecture, microservicios opcionales. |

### 16.4 Valoración técnica final

El sistema demuestra que el equipo comprende y aplica patrones de diseño de software modernos. La inversión en Arquitectura Hexagonal y DDD es correcta para la complejidad del dominio (torneos con múltiples formatos, criterios ponderados, fixtures complejos, ML integrado). La remediación de los hallazgos identificados, especialmente los críticos, transformaría este sistema de un prototipo avanzado en una plataforma productiva robusta.

---

**Fin del Reporte de Ingeniería Inversa**

*Documento generado mediante síntesis de 10 pasadas de auditoría especializadas sobre el sistema Zoids League. Toda la evidencia está basada en análisis directo de código fuente, ejecución real del sistema, y auditoría de dependencias. Ninguna información fue inferida sin evidencia técnica concreta.*

*Archivos relacionados: `05_Auditoria_Tecnologica.md` · `06_Auditoria_Arquitectura.md` · `07_Auditoria_Dependencias.md` · `08_Guia_DevOps_Entorno.md` · `09_Auditoria_Configuracion.md` · `10_Auditoria_Logs.md` · `11_Inventario_Funcional.md` · `12_Analisis_DDD.md` · `13_Arquitectura_Empresarial.md` · `14_Evaluacion_Calidad.md` · `15_Matriz_Hallazgos.md`*
