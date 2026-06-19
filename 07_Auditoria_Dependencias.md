# Auditoría de Dependencias — Zoids League
**Auditor:** Especialista en Auditoría de Dependencias (Claude Sonnet 4.6)  
**Fecha:** 2026-06-19  
**Archivos analizados:** `requirements.txt`, `frontend/react/package.json`, `frontend/react/package-lock.json`, `frontend/react/tsconfig.json`, `frontend/react/vite.config.ts`, `.coveragerc`  
**Método:** Análisis estático directo de archivos de dependencias

---

## 1. Inventario completo

### 1.1 Backend Python — `requirements.txt` (22 paquetes)

| # | Paquete | Versión declarada | Tipo de pin |
|---|---------|-------------------|-------------|
| 1 | `asgiref` | `==3.11.1` | Exacto |
| 2 | `bcrypt` | `==5.0.0` | Exacto |
| 3 | `coverage` | `==7.13.5` | Exacto |
| 4 | `Django` | `==6.0.4` | Exacto |
| 5 | `django-cors-headers` | `==4.9.0` | Exacto |
| 6 | `djangorestframework` | `==3.17.1` | Exacto |
| 7 | `djangorestframework_simplejwt` | `==5.5.1` | Exacto |
| 8 | `gunicorn` | `==26.0.0` | Exacto |
| 9 | `joblib` | `==1.4.2` | Exacto |
| 10 | `numpy` | `==1.26.4` | Exacto |
| 11 | `openai` | `>=1.0.0,<2.0.0` | Rango |
| 12 | `packaging` | `==26.2` | Exacto |
| 13 | `passlib` | `==1.7.4` | Exacto |
| 14 | `psycopg2` | `==2.9.12` | Exacto |
| 15 | `psycopg2-binary` | `==2.9.12` | Exacto |
| 16 | `PyJWT` | `==2.12.1` | Exacto |
| 17 | `python-dotenv` | `>=1.0.0,<2.0.0` | Rango |
| 18 | `scikit-learn` | `==1.6.1` | Exacto |
| 19 | `sqlparse` | `==0.5.5` | Exacto |
| 20 | `tzdata` | `==2026.1` | Exacto |
| 21 | `whitenoise` | `==6.12.0` | Exacto |
| 22 | `xgboost` | `==2.1.4` | Exacto |

### 1.2 Frontend Node.js — `package.json`

#### Dependencias de producción (69 paquetes directos)

| # | Paquete | Versión |
|---|---------|---------|
| 1 | `@emotion/react` | `11.14.0` |
| 2 | `@emotion/styled` | `11.14.1` |
| 3 | `@mui/icons-material` | `7.3.5` |
| 4 | `@mui/material` | `7.3.5` |
| 5 | `@popperjs/core` | `2.11.8` |
| 6 | `@radix-ui/react-accordion` | `1.2.3` |
| 7 | `@radix-ui/react-alert-dialog` | `1.1.6` |
| 8 | `@radix-ui/react-aspect-ratio` | `1.1.2` |
| 9 | `@radix-ui/react-avatar` | `1.1.3` |
| 10 | `@radix-ui/react-checkbox` | `1.1.4` |
| 11 | `@radix-ui/react-collapsible` | `1.1.3` |
| 12 | `@radix-ui/react-context-menu` | `2.2.6` |
| 13 | `@radix-ui/react-dialog` | `1.1.6` |
| 14 | `@radix-ui/react-dropdown-menu` | `2.1.6` |
| 15 | `@radix-ui/react-hover-card` | `1.1.6` |
| 16 | `@radix-ui/react-label` | `2.1.2` |
| 17 | `@radix-ui/react-menubar` | `1.1.6` |
| 18 | `@radix-ui/react-navigation-menu` | `1.2.5` |
| 19 | `@radix-ui/react-popover` | `1.1.6` |
| 20 | `@radix-ui/react-progress` | `1.1.2` |
| 21 | `@radix-ui/react-radio-group` | `1.2.3` |
| 22 | `@radix-ui/react-scroll-area` | `1.2.3` |
| 23 | `@radix-ui/react-select` | `2.1.6` |
| 24 | `@radix-ui/react-separator` | `1.1.2` |
| 25 | `@radix-ui/react-slider` | `1.2.3` |
| 26 | `@radix-ui/react-slot` | `1.1.2` |
| 27 | `@radix-ui/react-switch` | `1.1.3` |
| 28 | `@radix-ui/react-tabs` | `1.1.3` |
| 29 | `@radix-ui/react-toggle` | `1.1.2` |
| 30 | `@radix-ui/react-toggle-group` | `1.1.2` |
| 31 | `@radix-ui/react-tooltip` | `1.1.8` |
| 32 | `axios` | `^1.15.0` |
| 33 | `canvas-confetti` | `1.9.4` |
| 34 | `class-variance-authority` | `0.7.1` |
| 35 | `clsx` | `2.1.1` |
| 36 | `cmdk` | `1.1.1` |
| 37 | `date-fns` | `3.6.0` |
| 38 | `embla-carousel-react` | `8.6.0` |
| 39 | `input-otp` | `1.4.2` |
| 40 | `lucide-react` | `0.487.0` |
| 41 | `motion` | `12.23.24` |
| 42 | `next-themes` | `0.4.6` |
| 43 | `react` | `^18.3.1` |
| 44 | `react-day-picker` | `8.10.1` |
| 45 | `react-dnd` | `16.0.1` |
| 46 | `react-dnd-html5-backend` | `16.0.1` |
| 47 | `react-dom` | `^18.3.1` |
| 48 | `react-hook-form` | `7.55.0` |
| 49 | `react-popper` | `2.3.0` |
| 50 | `react-resizable-panels` | `2.1.7` |
| 51 | `react-responsive-masonry` | `2.7.1` |
| 52 | `react-router` | `7.13.0` |
| 53 | `react-slick` | `0.31.0` |
| 54 | `recharts` | `2.15.2` |
| 55 | `sonner` | `^2.0.3` |
| 56 | `tailwind-merge` | `3.2.0` |
| 57 | `tw-animate-css` | `1.3.8` |
| 58 | `vaul` | `1.1.2` |

#### Dependencias de desarrollo (8 paquetes)

| # | Paquete | Versión |
|---|---------|---------|
| 1 | `@tailwindcss/vite` | `4.1.12` |
| 2 | `@types/node` | `^25.6.0` |
| 3 | `@types/react` | `18` |
| 4 | `@types/react-dom` | `18` |
| 5 | `@vitejs/plugin-react` | `4.7.0` |
| 6 | `tailwindcss` | `4.1.12` |
| 7 | `typescript` | `^6.0.2` |
| 8 | `vite` | `6.3.5` |

---

## 2. Dependencias de producción

### 2.1 Backend — producción

De los 22 paquetes declarados, **21 son de producción** (uno es herramienta de testing):

| Paquete | Propósito en producción |
|---------|------------------------|
| `Django==6.0.4` | Framework web principal |
| `djangorestframework==3.17.1` | API REST |
| `djangorestframework_simplejwt==5.5.1` | Autenticación JWT |
| `django-cors-headers==4.9.0` | Middleware CORS |
| `gunicorn==26.0.0` | Servidor WSGI para producción |
| `whitenoise==6.12.0` | Servir archivos estáticos |
| `psycopg2==2.9.12` | Driver PostgreSQL (producción) |
| `psycopg2-binary==2.9.12` | Driver PostgreSQL binario (debería ser solo dev) |
| `bcrypt==5.0.0` | Hashing de contraseñas |
| `passlib==1.7.4` | Librería de hashing (redundante con bcrypt, abandonada) |
| `PyJWT==2.12.1` | Generación/validación de tokens JWT |
| `openai>=1.0.0,<2.0.0` | Cliente para OpenRouter/OpenAI |
| `python-dotenv>=1.0.0,<2.0.0` | Carga de variables de entorno |
| `xgboost==2.1.4` | Modelo ML para predicciones |
| `scikit-learn==1.6.1` | Herramientas ML auxiliares |
| `numpy==1.26.4` | Computación numérica (requerida por scikit-learn/xgboost) |
| `asgiref==3.11.1` | Soporte async Django (dependencia indirecta) |
| `sqlparse==0.5.5` | Parseo SQL (dependencia indirecta de Django) |
| `joblib==1.4.2` | Paralelismo (dependencia indirecta de scikit-learn) |
| `packaging==26.2` | Utilidades de packaging (dependencia indirecta) |
| `tzdata==2026.1` | Datos de zona horaria |

### 2.2 Frontend — producción (58 paquetes)

Los 58 paquetes del bloque `"dependencies"` en `package.json`. Los más críticos:

| Paquete | Propósito |
|---------|-----------|
| `react@^18.3.1` + `react-dom` | Framework UI principal |
| `react-router@7.13.0` | Enrutamiento SPA |
| `axios@^1.15.0` | Cliente HTTP hacia la API |
| `@mui/material@7.3.5` | Sistema de componentes Material Design |
| `react-hook-form@7.55.0` | Gestión de formularios |
| `recharts@2.15.2` | Gráficos y visualizaciones |
| `react-dnd@16.0.1` | Drag and drop |

---

## 3. Dependencias de desarrollo

### 3.1 Backend — problema: NO HAY separación

> **Hallazgo crítico:** El archivo `requirements.txt` es un archivo único que mezcla dependencias de producción y de desarrollo. No existe `requirements-dev.txt`, `requirements-test.txt` ni `pyproject.toml` con grupos opcionales.

| Paquete de desarrollo encontrado en requirements.txt | Propósito |
|------------------------------------------------------|-----------|
| `coverage==7.13.5` | Medición de cobertura de tests (herramienta de CI/dev) |

**Dependencias de producción que deberían ser solo de desarrollo:**

| Paquete | Razón |
|---------|-------|
| `psycopg2-binary==2.9.12` | La versión binaria es para desarrollo/testing; en producción se recomienda compilar `psycopg2` desde fuente |

### 3.2 Frontend — separación correcta

El `package.json` usa correctamente `dependencies` y `devDependencies`:

| Paquete | Propósito de desarrollo |
|---------|------------------------|
| `vite@6.3.5` | Bundler y servidor de desarrollo |
| `@vitejs/plugin-react@4.7.0` | Plugin React para Vite |
| `typescript@^6.0.2` | Compilador TypeScript |
| `tailwindcss@4.1.12` | Framework CSS (procesado en build) |
| `@tailwindcss/vite@4.1.12` | Plugin Tailwind para Vite |
| `@types/react@18` | Definiciones de tipos React |
| `@types/react-dom@18` | Definiciones de tipos React DOM |
| `@types/node@^25.6.0` | Definiciones de tipos Node.js |

> **Ausencia notable:** No hay ningún framework de testing en `devDependencies` (ni Vitest, ni Jest, ni React Testing Library). El frontend no tiene infraestructura de tests declarada.

---

## 4. Dependencias críticas

Dependencias cuya falla, eliminación o compromiso causaría la caída total del sistema:

### 4.1 Backend

| Dependencia | Versión | Criticidad | Impacto si falla |
|-------------|---------|------------|-----------------|
| `Django` | `6.0.4` | **CRÍTICA** | Caída total del backend |
| `djangorestframework` | `3.17.1` | **CRÍTICA** | Sin API REST, sin respuestas JSON |
| `psycopg2` | `2.9.12` | **CRÍTICA** | Sin acceso a PostgreSQL, sin persistencia |
| `djangorestframework_simplejwt` | `5.5.1` | **CRÍTICA** | Sin autenticación JWT, sistema inutilizable |
| `bcrypt` | `5.0.0` | **ALTA** | Sin verificación de contraseñas |
| `gunicorn` | `26.0.0` | **ALTA** | Sin servidor productivo (solo `runserver` fallaría en carga) |
| `xgboost` | `2.1.4` | **ALTA** | Módulo de simulación/predicción inoperativo |
| `openai` | `>=1.0.0` | **ALTA** | Sin generación de criterios IA |
| `asgiref` | `3.11.1` | **MEDIA** | Django no arranca sin ella (dependencia oculta) |

### 4.2 Frontend

| Dependencia | Versión | Criticidad | Impacto si falla |
|-------------|---------|------------|-----------------|
| `react` + `react-dom` | `^18.3.1` | **CRÍTICA** | Sin UI |
| `react-router` | `7.13.0` | **CRÍTICA** | Sin navegación, SPA inutilizable |
| `axios` | `^1.15.0` | **CRÍTICA** | Sin comunicación con la API |
| `@mui/material` | `7.3.5` | **ALTA** | Sin sistema de diseño, UI degradada |
| `recharts` | `2.15.2` | **MEDIA** | Sin gráficos/visualizaciones |
| `react-hook-form` | `7.55.0` | **MEDIA** | Sin gestión de formularios |
| `react-dnd` | `16.0.1` | **BAJA** | Sin drag-and-drop (feature puntual) |

---

## 5. Dependencias obsoletas

### 5.1 Backend

| Paquete | Versión actual | Estado | Detalles |
|---------|---------------|--------|---------|
| `passlib` | `1.7.4` | **ABANDONADA** | Última versión publicada en junio 2020. El autor anunció el abandono del proyecto en 2024. No recibirá parches de seguridad. |
| `numpy` | `1.26.4` | **Desactualizada** | La serie 2.x (numpy 2.0+) está disponible. La 1.26.x sigue recibiendo parches críticos pero está en modo mantenimiento. |
| `passlib` + `bcrypt` | ambas | **Redundante** | El proyecto usa `bcrypt` directamente para hashing y `passlib` para la API de alto nivel. Con `bcrypt==5.0.0`, `passlib` es prescindible. |
| `packaging==26.2` | `26.2` | **Dependencia fantasma** | `packaging` es una dependencia indirecta de pip/setuptools. Pinearla explícitamente crea una falsa expectativa de que es requerida directamente. |
| `joblib==1.4.2` | `1.4.2` | **Dependencia fantasma** | Es una dependencia transitiva de `scikit-learn`. No debería estar explícita en `requirements.txt`. |
| `sqlparse==0.5.5` | `0.5.5` | **Dependencia fantasma** | Dependencia transitiva de Django. No debería estar explícita. |
| `asgiref==3.11.1` | `3.11.1` | **Dependencia fantasma** | Dependencia transitiva de Django. No debería estar explícita. |

### 5.2 Frontend

| Paquete | Versión | Estado | Detalles |
|---------|---------|--------|---------|
| `@popperjs/core@2.11.8` | `2.11.8` | **Posiblemente obsoleta** | MUI v7 migró internamente de Popper.js a Floating UI. Esta dependencia puede ser un artefacto de una migración incompleta. |
| `react-popper@2.3.0` | `2.3.0` | **Posiblemente obsoleta** | Wrapper de Popper.js para React. Con MUI v7 y sin uso explícito detectado en código, puede ser una ghost dependency. |
| `react-slick@0.31.0` | `0.31.0` | **Redundante** | Hay dos librerías de carrusel: `react-slick` y `embla-carousel-react`. Una de las dos debería eliminarse. |
| `@types/react@18` | `18` (sin patch) | **Pin impreciso** | La especificación `"18"` (sin `^` ni patch version) puede desincronizarse con la versión real de React usada (`^18.3.1`). |
| `next-themes@0.4.6` | `0.4.6` | **Semánticamente extraña** | Es una librería orientada a Next.js usada en un proyecto Vite. Funciona, pero introduce una dependencia con nombre confuso. |

---

## 6. Vulnerabilidades potenciales

### 6.1 Backend — riesgo ALTO

| # | Dependencia | CVE/Riesgo | Severidad | Descripción |
|---|-------------|-----------|-----------|-------------|
| 1 | `passlib==1.7.4` | **Abandono de mantenimiento** | ALTA | Librería sin mantenimiento desde 2020 y oficialmente abandonada en 2024. No recibirá correcciones ante futuros CVEs en algoritmos de hashing soportados. La presencia junto a `bcrypt` confirma que es prescindible. |
| 2 | `psycopg2-binary==2.9.12` | **Uso no recomendado en producción** | MEDIA | La distribución binaria de psycopg2 está explícitamente desaconsejada para entornos de producción por los mantenedores. Puede contener builds desactualizados de libpq sin parches de seguridad recientes. |
| 3 | `openai>=1.0.0,<2.0.0` | **Pin flotante** | MEDIA | El rango `>=1.0.0,<2.0.0` permite que cualquier versión 1.x sea instalada. Una versión 1.x comprometida en PyPI sería instalada automáticamente en el siguiente `pip install`. Debe fijarse con `==`. |
| 4 | `python-dotenv>=1.0.0,<2.0.0` | **Pin flotante** | BAJA | Mismo riesgo que `openai`: ataque de cadena de suministro posible en actualizaciones menores no controladas. |
| 5 | `numpy==1.26.4` | **Serie en mantenimiento** | BAJA | La serie 1.26.x no recibe nuevas funcionalidades. Vulnerabilidades graves podrían no ser backporteadas si los mantenedores las priorizan en la 2.x. |

### 6.2 Backend — riesgo de configuración (no de paquete)

| # | Hallazgo | Severidad |
|---|----------|-----------|
| 1 | `coverage` en `requirements.txt` de producción | MEDIA — puede exponer información de cobertura si se ejecuta en producción |
| 2 | Ambos `psycopg2` y `psycopg2-binary` instalados simultáneamente | BAJA — instalación redundante, posible conflicto de librerías nativas |
| 3 | `django.conf.settings.SECRET_KEY` con fallback inseguro en `settings.py` | CRÍTICA (ya documentada en auditorías previas) — no es del paquete sino de su configuración |

### 6.3 Frontend — riesgo

| # | Dependencia | Riesgo | Severidad |
|---|-------------|--------|-----------|
| 1 | `react-slick@0.31.0` | Depende de `slick-carousel` que ha tenido CVEs de XSS en versiones antiguas. En `0.31.0` el riesgo es menor pero la librería tiene mantenimiento irregular. | BAJA |
| 2 | `axios@^1.15.0` | Rango flotante — `^` permite actualizaciones de minor. En versiones anteriores de Axios hubo CVEs de CSRF/SSRF. La versión 1.15.x es reciente y probablemente segura. | BAJA |
| 3 | Sin framework de testing en frontend | No permite detectar regresiones de seguridad en componentes que manejan tokens o datos de usuario. | MEDIA (riesgo indirecto) |
| 4 | `canvas-confetti@1.9.4` | Librería cosmética sin relación con datos. Sin riesgo de seguridad conocido. | NINGUNO |

---

## 7. Dependencias relacionadas con seguridad

### 7.1 Backend

| Paquete | Versión | Rol de seguridad | Estado |
|---------|---------|-----------------|--------|
| `bcrypt` | `5.0.0` | Hashing de contraseñas con salt automático (Blowfish) | ✅ Activa y mantenida |
| `passlib` | `1.7.4` | API de alto nivel para hashing (bcrypt, argon2, scrypt) | ⚠️ Abandonada — reemplazar |
| `djangorestframework_simplejwt` | `5.5.1` | Emisión y validación de tokens JWT (access + refresh) | ✅ Activa y mantenida |
| `PyJWT` | `2.12.1` | Librería base de JWT (dependencia de simplejwt) | ✅ Activa y mantenida |
| `django-cors-headers` | `4.9.0` | Control de CORS — whitelist de orígenes permitidos | ✅ Activa y mantenida |
| `whitenoise` | `6.12.0` | Servir archivos estáticos de forma segura sin Nginx | ✅ Activa y mantenida |
| `Django` | `6.0.4` | CSRF protection, XSS headers, clickjacking protection (middlewares built-in) | ✅ Activa y mantenida |

**Relación entre dependencias de seguridad:**
```
Autenticación:
  bcrypt (hashing) ← usado directamente en password_service.py
  passlib (wrapper) ← redundante, debería eliminarse
  PyJWT (tokens) ← usado por simplejwt
  djangorestframework_simplejwt (JWT lifecycle)

Transporte/API:
  django-cors-headers (CORS)
  Django CSRF middleware (built-in)
  whitenoise (static files)
```

### 7.2 Frontend

| Paquete | Versión | Rol de seguridad |
|---------|---------|-----------------|
| `axios` | `^1.15.0` | Interceptors para adjuntar JWT en cada request; manejo de 401 para logout automático |
| `react-router` | `7.13.0` | Protección de rutas mediante `RoleGuard` + `useAuth` |

---

## 8. Dependencias relacionadas con persistencia

### 8.1 Backend

| Paquete | Versión | Rol en persistencia | Notas |
|---------|---------|---------------------|-------|
| `psycopg2` | `2.9.12` | Driver nativo C para PostgreSQL — usado en producción | ✅ Correcto para producción |
| `psycopg2-binary` | `2.9.12` | Driver binario precompilado para PostgreSQL | ⚠️ Redundante con `psycopg2`; debería estar solo en dev |
| `Django` (ORM) | `6.0.4` | ORM incluido en Django — gestión de modelos, migraciones y queries | Accedido via `django.db.models` |
| `sqlparse` | `0.5.5` | Parser SQL (dependencia interna de Django para pretty-printing de queries en DEBUG) | Dep. transitiva — no necesita listarse |
| `asgiref` | `3.11.1` | Soporte async para ORM Django (operaciones de BD en contexto async) | Dep. transitiva de Django |

**Stack de persistencia efectivo:**
```
Django ORM (modelos, migraciones, QuerySet API)
    └── psycopg2 / psycopg2-binary (driver)
        └── PostgreSQL 17 (motor de BD — via Docker)
```

**Tablas gestionadas:** 20+ tablas en 3 esquemas de aplicación (authentication, competencia, simulacion). Detallado en `06_Auditoria_Arquitectura.md`.

### 8.2 Frontend

No hay dependencias de persistencia directa en el frontend. El estado se gestiona mediante:
- `React Context API` (estado en memoria, sin persistencia)
- `localStorage` (via `authService.ts` para tokens JWT — no es una dependencia NPM)

---

## 9. Dependencias relacionadas con APIs

### 9.1 Backend — Exposición de API

| Paquete | Versión | Rol en API | Notas |
|---------|---------|------------|-------|
| `djangorestframework` | `3.17.1` | Framework REST: serializers, viewsets, decoradores `@api_view`, respuestas JSON | Core de la API |
| `djangorestframework_simplejwt` | `5.5.1` | Endpoints de autenticación JWT (`/api/auth/`) | Seguridad de la API |
| `django-cors-headers` | `4.9.0` | Middleware que controla el acceso cross-origin a la API REST | Seguridad de la API |
| `gunicorn` | `26.0.0` | Servidor WSGI que expone la API Django al exterior | Transporte |
| `asgiref` | `3.11.1` | Soporte para servir Django via ASGI (preparación para WebSocket) | Transporte async |
| `whitenoise` | `6.12.0` | Sirve assets estáticos de la API directamente sin proxy | Operaciones |

### 9.2 Backend — Consumo de API externa

| Paquete | Versión | API consumida | Notas |
|---------|---------|---------------|-------|
| `openai` | `>=1.0.0,<2.0.0` | OpenRouter (compatible con API de OpenAI) — generación de criterios de evaluación via GPT-4o | Pin flotante — riesgo supply chain |

**Configuración de la API externa (`.env.example`):**
```
OPENROUTER_API_KEY=tu-api-key-de-openrouter
```
La clave se inyecta via variable de entorno. No hay clave hardcodeada en el código fuente. ✅

### 9.3 Frontend — Consumo de API

| Paquete | Versión | Rol |
|---------|---------|-----|
| `axios` | `^1.15.0` | Cliente HTTP principal. Incluye interceptors para JWT y manejo de errores centralizados en `src/services/api.ts` |
| `react-hook-form` | `7.55.0` | Gestión de formularios que interactúan con la API (login, registro, creación de torneos) |

---

## 10. Hallazgos críticos y recomendaciones

### 10.1 Resumen de problemas por severidad

| Severidad | # | Descripción |
|-----------|---|-------------|
| 🔴 CRÍTICA | 1 | `passlib==1.7.4` en producción — librería abandonada sin parches de seguridad |
| 🟠 ALTA | 2 | Sin separación `requirements.txt` / `requirements-dev.txt` — `coverage` en producción |
| 🟠 ALTA | 3 | `psycopg2` + `psycopg2-binary` ambos declarados — binario no debe ir a producción |
| 🟠 ALTA | 4 | `openai>=1.0.0,<2.0.0` con rango flotante — riesgo de cadena de suministro |
| 🟡 MEDIA | 5 | `python-dotenv>=1.0.0,<2.0.0` con rango flotante |
| 🟡 MEDIA | 6 | Sin framework de testing en frontend — ningún `devDependency` de test |
| 🟡 MEDIA | 7 | `numpy==1.26.4` en serie 1.x — serie 2.x disponible |
| 🟡 MEDIA | 8 | Dependencias fantasma explícitas: `packaging`, `joblib`, `sqlparse`, `asgiref` |
| 🟢 BAJA | 9 | Dos librerías de carrusel: `embla-carousel-react` + `react-slick` — redundancia |
| 🟢 BAJA | 10 | `@popperjs/core` + `react-popper` — posibles ghost dependencies en MUI v7 |
| 🟢 BAJA | 11 | `next-themes` — librería Next.js en proyecto Vite (funciona pero nombre confuso) |
| 🟢 BAJA | 12 | `@types/react@18` sin version patch — puede desincronizarse |

### 10.2 Acciones recomendadas

```bash
# 1. Eliminar passlib — reemplazarla con uso directo de bcrypt
pip uninstall passlib

# 2. Separar dependencias de desarrollo
# Mover al nuevo requirements-dev.txt:
#   coverage==7.13.5
#   psycopg2-binary==2.9.12

# 3. Fijar openai a versión exacta
openai==1.93.0  # o la versión más reciente verificada

# 4. Eliminar dependencias fantasma de requirements.txt
# Remover: packaging, joblib, sqlparse, asgiref
# (son gestionadas transitivamente por pip)

# 5. Frontend — agregar testing
npm install -D vitest @testing-library/react @testing-library/user-event

# 6. Frontend — auditar ghost dependencies
npm ls @popperjs/core react-popper
# Si no aparecen en el árbol de uso real → eliminar

# 7. Frontend — elegir un solo sistema de carrusel
# Eliminar react-slick O embla-carousel-react
```

### 10.3 Matriz de riesgo final

```
IMPACTO
  │
A │  [passlib abandonada]
L │
T │  [openai pin flotante]    [psycopg2-binary en prod]
O │
  │  [sin tests frontend]     [coverage en prod]
M │
E │                            [numpy 1.x]
D │  [ghost deps]
I │
O │             [2 carousels]  [next-themes en Vite]
  │
B │
A │
J │
O └─────────────────────────────────────────────────────► PROBABILIDAD
       BAJA          MEDIA              ALTA
```

---

*Auditoría generada mediante análisis estático directo de `requirements.txt`, `package.json` y `package-lock.json`. No se ejecutó `pip audit`, `npm audit` ni `safety check` — los hallazgos se basan en conocimiento de versiones a fecha de auditoría (2026-06-19).*
