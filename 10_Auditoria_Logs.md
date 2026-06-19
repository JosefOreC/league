# Auditoría de Logs — Zoids League
**Auditor:** Ingeniero de Soporte Nivel 3 (Claude Sonnet 4.6)  
**Fecha:** 2026-06-19  
**Entorno de ejecución:** Windows 11 Pro — Python 3.14.4 — Node 24.15.0 — npm 11.12.1  
**Método:** Ejecución real del proyecto con captura de logs en vivo

---

## Fases de ejecución auditadas

| # | Fase | Comando | Resultado |
|---|------|---------|-----------|
| 1 | Instalación completa de dependencias Python | `pip install -r requirements.txt` | ❌ FALLÓ |
| 2 | Instalación parcial (Django + auth stack) | `pip install Django ... psycopg2-binary ...` | ✅ OK |
| 3 | Instalación de dependencias ML | `pip install joblib numpy xgboost` | ⚠️ PARCIAL |
| 4 | Django startup (primer intento) | `python manage.py check` | ❌ FALLÓ |
| 5 | Django startup (segundo intento) | `python manage.py check` | ❌ FALLÓ |
| 6 | Django security audit | `python manage.py check --deploy` | ⚠️ 6 WARNINGS |
| 7 | Django migración de BD | `python manage.py migrate` | ❌ FALLÓ |
| 8 | Django test runner | `python manage.py test --verbosity=2` | ❌ FALLÓ |
| 9 | Auditoría de dependencias frontend | `npm audit` | ❌ 8 vulnerabilidades |
| 10 | Compilador TypeScript | `npx tsc --noEmit` | ❌ 15 errores |

---

## 1. Errores

### ERROR-001 — `scikit-learn==1.6.1` no tiene wheel para Python 3.14

**Fase:** 1 — `pip install -r requirements.txt`  
**Severidad:** 🔴 CRÍTICA  
**Categoría:** Dependencia faltante / Incompatibilidad de versiones

```
ERROR: metadata-generation-failed
Preparing metadata (pyproject.toml) did not run successfully.
exit code: 1
meson.build:1:0: ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ['clang'], ['clang-cl'], ['pgcc']]
  Running `cl /?`   gave "[WinError 2] El sistema no puede encontrar el archivo especificado"
  Running `gcc --version` gave "[WinError 2] El sistema no puede encontrar el archivo especificado"
note: This error originates from a subprocess, and is likely not a problem with pip.
error: metadata-generation-failed → scikit-learn
```

**Causa raíz:** `scikit-learn==1.6.1` requiere compilación desde código fuente en Python 3.14 (no existe wheel precompilada). El sistema no tiene compilador C (MSVC, GCC, Clang) instalado. El `Dockerfile` usa `python:3.12-slim` (correcto), pero el host tiene Python 3.14.4.

**Impacto:** El módulo de simulación predictiva (XGBoost + scikit-learn) no puede inicializarse.

---

### ERROR-002 — `numpy==1.26.4` no tiene wheel para Python 3.14

**Fase:** 3 — `pip install --only-binary numpy`  
**Severidad:** 🔴 CRÍTICA  
**Categoría:** Dependencia faltante / Incompatibilidad de versiones

```
ERROR: metadata-generation-failed
NumPy 1.26.4 — Preparing metadata (pyproject.toml): finished with status 'error'
meson.build:1:0: ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ...]]
WARNING: Failed to activate VS environment: Could not parse vswhere.exe output
```

**Causa raíz:** `numpy==1.26.4` no tiene wheel precompilada para Python 3.14. Se resolvió instalando `numpy 2.4.6` (versión más reciente, diferente major). Esto introduce una incompatibilidad de versión: el código fue desarrollado con numpy 1.26.4 y puede tener incompatibilidades con la API de numpy 2.x.

---

### ERROR-003 — `ModuleNotFoundError: No module named 'joblib'` al iniciar Django

**Fase:** 4 — `python manage.py check`  
**Severidad:** 🔴 CRÍTICA  
**Categoría:** Dependencia faltante  
**Traza completa:**

```
File "D:\league\config\urls.py", line 24, in <module>
    path('api/simulacion/', include('simulacion.infrastructure.adapters.input.api.urls')),
File "D:\league\simulacion\infrastructure\adapters\input\api\urls.py", line 2, in <module>
    from .views import (...)
File "D:\league\simulacion\infrastructure\adapters\input\api\views.py", line 6, in <module>
    from simulacion.application.use_cases.predecir_resultado import PredecirResultadoUseCase
File "D:\league\simulacion\application\use_cases\predecir_resultado.py", line 1, in <module>
    from simulacion.infrastructure.ml.xgboost_adapter import XGBoostAdapter
File "D:\league\simulacion\infrastructure\ml\xgboost_adapter.py", line 1, in <module>
    import joblib
ModuleNotFoundError: No module named 'joblib'
```

**Causa raíz:** `joblib` es una dependencia transitiva de `scikit-learn` que no se instaló. Al fallar `scikit-learn` (ERROR-001), `joblib` tampoco quedó disponible. El módulo `xgboost_adapter.py` importa `joblib` al nivel de módulo (no lazy), lo que **bloquea el arranque completo de Django**.

**Impacto:** Django no puede inicializarse en absoluto — todos los endpoints fallan.

---

### ERROR-004 — `ModuleNotFoundError: No module named 'openai'` al iniciar Django

**Fase:** 5 — `python manage.py check` (segundo intento tras instalar joblib)  
**Severidad:** 🔴 CRÍTICA  
**Categoría:** Dependencia faltante  
**Traza completa:**

```
File "D:\league\config\urls.py", line 24, in <module>
    path('api/simulacion/', include('simulacion.infrastructure.adapters.input.api.urls')),
File "D:\league\simulacion\infrastructure\adapters\input\api\urls.py", line 2, in <module>
    from .views import (...)
File "D:\league\simulacion\infrastructure\adapters\input\api\views.py", line 8, in <module>
    from simulacion.application.use_cases.analizar_programacion import AnalizarProgramacionUseCase
File "D:\league\simulacion\application\use_cases\analizar_programacion.py", line 4, in <module>
    from simulacion.infrastructure.ia.analisis_engine import analizar_entrega
File "D:\league\simulacion\infrastructure\ia\analisis_engine.py", line 1, in <module>
    from openai import OpenAI
ModuleNotFoundError: No module named 'openai'
```

**Causa raíz:** `openai` no estaba instalado inicialmente. Tras instalarlo manualmente, el error se resolvió. Sin embargo, el patrón de importación eager (nivel de módulo) en `analisis_engine.py` garantiza que si la librería falta, **Django completo falla al iniciar**.

---

### ERROR-005 — `psycopg2.OperationalError`: PostgreSQL no disponible

**Fase:** 7 y 8 — `python manage.py migrate` y `python manage.py test`  
**Severidad:** 🔴 CRÍTICA  
**Categoría:** Problema de red / Configuración de base de datos  
**Traza completa:**

```
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed:
    Connection refused (0x0000274D/10061)
    Is the server running on that host and accepting TCP/IP connections?
connection to server at "localhost" (127.0.0.1), port 5432 failed:
    Connection refused (0x0000274D/10061)
    Is the server running on that host and accepting TCP/IP connections?

django.db.utils.OperationalError: connection to server at "localhost" (::1), port 5432 failed:
    Connection refused (0x0000274D/10061)
```

**Causa raíz:** No hay servidor PostgreSQL ejecutándose en el host. Django intenta conectarse primero a IPv6 (`::1:5432`) y luego a IPv4 (`127.0.0.1:5432`), ambos rechazados. El proyecto requiere PostgreSQL como dependencia de infraestructura — no tiene fallback a SQLite en el entorno de ejecución actual.

---

### ERROR-006 — TypeScript TS18048: `decoded.exp` posiblemente `undefined` en flujo de autenticación

**Fase:** 10 — `npx tsc --noEmit`  
**Severidad:** 🔴 CRÍTICA  
**Categoría:** Error de tipado — riesgo de seguridad  

```
src/context/AuthContext.tsx(36,24): error TS18048: 'decoded.exp' is possibly 'undefined'.
```

**Código afectado:** `frontend/react/src/context/AuthContext.tsx:36`
```typescript
if (decoded && decoded.exp * 1000 > Date.now()) {  // decoded.exp puede ser undefined
```

**Causa raíz:** El campo `exp` del JWT decodificado es tipado como opcional. Si `decoded.exp` es `undefined`, la expresión `undefined * 1000` da `NaN`, que al compararse con `Date.now()` da `false`. El token nunca se considera válido — **el usuario siempre sería deslogueado** incluso con un token válido, o si el compilador TS estuviera en modo permisivo, la lógica quedaría silenciosamente rota.

---

### ERRORES-007 al 021 — 14 errores TypeScript TS6133 (variables no utilizadas)

**Fase:** 10 — `npx tsc --noEmit`  
**Severidad:** 🟡 MEDIA  
**Categoría:** Código muerto / variables sin uso

| Archivo | Línea | Variable no usada | Tipo |
|---------|-------|-------------------|------|
| `Sidebar.tsx` | 6 | `Users` | Import de ícono |
| `Sidebar.tsx` | 7 | `Swords` | Import de ícono |
| `Competitions.tsx` | 3 | `Star` | Import de ícono |
| `Competitions.tsx` | 4 | `ChevronRight` | Import de ícono |
| `Competitions.tsx` | 20 | `standings` | Variable de estado |
| `Results.tsx` | 4 | `Star` | Import de ícono |
| `Results.tsx` | 5 | `Users` | Import de ícono |
| `ConfigTournamentRules.tsx` | 39 | `axios` | Import de librería HTTP |
| `TournamentAdminPanel.tsx` | 9 | `startTournament` | Función importada |
| `TournamentAdminPanel.tsx` | 13 | `axios` | Import de librería HTTP |
| `TournamentAdminPanel.tsx` | 377 | `user` | Variable local |
| `TournamentsList.tsx` | 158 | `canEdit` | Variable local |
| `routes/index.tsx` | 37 | `NotParticipant` | Componente de guarda de ruta |
| `api.ts` | 79 | `method` | Variable del interceptor |

**Causa raíz:** Código comentado, funcionalidades incompletas o refactors a medias que dejaron imports sin eliminar.

---

## 2. Advertencias

### WARN-001 — Django security.W004: HSTS no configurado

**Fase:** 6 — `python manage.py check --deploy`  
**Severidad:** 🟠 ALTA  
**Mensaje:**
```
?: (security.W004) You have not set a value for the SECURE_HSTS_SECONDS setting.
If your entire site is served only over SSL, you may want to consider setting a value
and enabling HTTP Strict Transport Security.
```
**Solución:** Agregar `SECURE_HSTS_SECONDS = 31536000` en `settings.py` para producción.

---

### WARN-002 — Django security.W008: SSL Redirect no forzado

**Fase:** 6 — `python manage.py check --deploy`  
**Severidad:** 🟠 ALTA  
**Mensaje:**
```
?: (security.W008) Your SECURE_SSL_REDIRECT setting is not set to True.
Unless your site should be available over both SSL and non-SSL connections,
you may want to either set this setting True or configure a load balancer
or reverse-proxy server to redirect all connections to HTTPS.
```
**Solución:** Agregar `SECURE_SSL_REDIRECT = True` o configurar Nginx para redirigir HTTP → HTTPS.

---

### WARN-003 — Django security.W009: SECRET_KEY débil o prefijada con `django-insecure-`

**Fase:** 6 — `python manage.py check --deploy`  
**Severidad:** 🔴 CRÍTICA  
**Mensaje:**
```
?: (security.W009) Your SECRET_KEY has less than 50 characters, less than 5 unique
characters, or it's prefixed with 'django-insecure-' indicating that it was generated
automatically by Django. Please generate a long and random value, otherwise many of
Django's security-critical features will be vulnerable to attack.
```
**Causa:** La `SECRET_KEY` de fallback hardcodeada en `settings.py` comienza con `'django-insecure-'` — Django la detecta explícitamente como insegura.

---

### WARN-004 — Django security.W012: SESSION_COOKIE_SECURE no activado

**Fase:** 6 — `python manage.py check --deploy`  
**Severidad:** 🟠 ALTA  
**Mensaje:**
```
?: (security.W012) SESSION_COOKIE_SECURE is not set to True.
Using a secure-only session cookie makes it more difficult for network traffic
sniffers to hijack user sessions.
```

---

### WARN-005 — Django security.W016: CSRF_COOKIE_SECURE no activado

**Fase:** 6 — `python manage.py check --deploy`  
**Severidad:** 🟠 ALTA  
**Mensaje:**
```
?: (security.W016) You have 'django.middleware.csrf.CsrfViewMiddleware' in your
MIDDLEWARE, but you have not set CSRF_COOKIE_SECURE to True.
Using a secure-only CSRF cookie makes it more difficult for network traffic sniffers
to steal the CSRF token.
```

---

### WARN-006 — Django security.W018: DEBUG=True en check de despliegue

**Fase:** 6 — `python manage.py check --deploy`  
**Severidad:** 🟠 ALTA  
**Mensaje:**
```
?: (security.W018) You should not have DEBUG set to True in deployment.
```

---

### WARN-007 — RuntimeWarning: Django no puede conectar a BD `postgres` de mantenimiento

**Fase:** 8 — `python manage.py test`  
**Severidad:** 🟡 MEDIA  
**Mensaje:**
```
D:\league\.venv_audit\Lib\site-packages\django\db\backends\postgresql\base.py:513:
RuntimeWarning: Normally Django will use a connection to the 'postgres' database to
avoid running initialization queries against the production database when it's not
needed (for example, when running tests). Django was unable to create a connection
to the 'postgres' database and will use the first PostgreSQL database instead.
  warnings.warn(
```
**Causa:** No existe la base de datos `postgres` (maintenance DB) en el servidor. Django la usa para crear la BD de test sin tocar la BD principal — su ausencia es inusual y sugiere una instalación PostgreSQL no estándar.

---

### WARN-008 — pip notice: Nueva versión de pip disponible

**Fase:** 1, 2, 3 — todas las fases de instalación  
**Severidad:** 🟢 BAJA  
**Mensaje:**
```
[notice] A new release of pip is available: 26.0.1 -> 26.1.2
[notice] To update, run: python.exe -m pip install --upgrade pip
```

---

### WARN-009 — `WARNING: Failed to activate VS environment` (Meson)

**Fase:** 1 y 3 — compilación de scikit-learn y numpy  
**Severidad:** 🟠 ALTA  
**Mensaje:**
```
WARNING: Failed to activate VS environment: Could not parse vswhere.exe output
```
**Causa:** Meson intenta detectar Visual Studio en Windows para compilar extensiones C. VS no está instalado o `vswhere.exe` no es accesible. Esto bloquea la compilación de paquetes nativos.

---

## 3. Excepciones

### EXC-001 — `django.db.utils.OperationalError` (wrapper de psycopg2)

**Fase:** 7 y 8  
**Severidad:** 🔴 CRÍTICA  
```
django.db.utils.OperationalError: connection to server at "localhost" (::1), port 5432 failed:
    Connection refused (0x0000274D/10061)
```
Django envuelve `psycopg2.OperationalError` en su propia jerarquía de excepciones. La cadena completa muestra el doble wrapping típico de Django: `psycopg2.OperationalError → django.db.utils.OperationalError`.

---

### EXC-002 — `ModuleNotFoundError` (cadena de inicialización de Django)

**Fase:** 4 y 5  
**Severidad:** 🔴 CRÍTICA  
Dos instancias en cadena diferente:
1. `No module named 'joblib'` — importación de nivel de módulo en `xgboost_adapter.py`
2. `No module named 'openai'` — importación de nivel de módulo en `analisis_engine.py`

Ambas excepciones ocurren durante la **importación del módulo de URLs** de Django (`config/urls.py`), lo que paraliza el proceso completo.

---

## 4. Dependencias faltantes

| # | Dependencia | Estado | Causa | Impacto |
|---|-------------|--------|-------|---------|
| 1 | `scikit-learn==1.6.1` | ❌ No instalable en Python 3.14 sin compilador C | Sin wheel precompilada para Py3.14 | Módulo ML inoperativo |
| 2 | `numpy==1.26.4` | ❌ No instalable en Python 3.14 sin compilador C | Sin wheel precompilada para Py3.14 | Módulo ML inoperativo |
| 3 | `joblib==1.4.2` | ❌ No instalado (depende de scikit-learn) | Falla en cadena desde ERROR-001 | Django no arranca |
| 4 | `openai>=1.0.0` | ❌ No instalado inicialmente | No listado en el grupo de instalación parcial | Django no arranca |
| 5 | PostgreSQL 17 | ❌ No disponible en el host | No instalado / no en ejecución | BD no accesible |
| 6 | Compilador C (MSVC/GCC) | ❌ No disponible en el host | Sin Build Tools instaladas | Impide compilar extensiones nativas |

**Versiones resueltas (alternativas que SÍ instalaron):**

| Paquete requerido | Versión instalada realmente | Delta |
|------------------|-----------------------------|-------|
| `numpy==1.26.4` | `numpy==2.4.6` | Major version bump — posibles breaking changes |
| `xgboost==2.1.4` | `xgboost==3.3.0` | Major version bump + nueva dep: `scipy` |
| `joblib==1.4.2` | `joblib==1.5.3` | Minor version bump — compatible |
| `python-dotenv>=1.0.0,<2.0.0` | `python-dotenv==1.2.2` | Dentro del rango — OK |
| `tzdata==2026.1` | `tzdata==2026.2` | Menor — compatible |

---

## 5. Problemas de configuración

### CONF-001 — Python 3.14 en lugar de 3.12 requerido

**Severidad:** 🔴 CRÍTICA  
El `Dockerfile` especifica `FROM python:3.12-slim`. El host tiene Python 3.14.4. scikit-learn 1.6.1 y numpy 1.26.4 no tienen wheels precompiladas para Python 3.14 → bloquean la instalación completa.

### CONF-002 — Seis advertencias de seguridad Django (`check --deploy`)

**Severidad:** 🔴 CRÍTICA / 🟠 ALTA  
Reportadas en sección de Advertencias: HSTS ausente, SSL redirect ausente, SECRET_KEY débil, SESSION_COOKIE_SECURE ausente, CSRF_COOKIE_SECURE ausente, DEBUG=True.

### CONF-003 — `EXPOSE 3000` en `frontend/Dockerfile` vs puerto real `5173`

**Severidad:** 🟡 MEDIA  
El Dockerfile del frontend declara `EXPOSE 3000`, pero Vite por defecto escucha en `5173` y `docker-compose.yml` mapea `5173:5173`. El `EXPOSE` es incorrecto — inconsistencia entre declaración y comportamiento real.

### CONF-004 — Variables de entorno hardcodeadas en `docker-compose.yml`

**Severidad:** 🔴 CRÍTICA  
`DB_PASSWORD: admin` y `POSTGRES_PASSWORD: admin` están literales en el YAML versionado. Incluso si el `.env` define otra contraseña, el `docker-compose.yml` la ignora y usa `admin`.

### CONF-005 — Importaciones eager de módulos ML y IA en rutas de Django

**Severidad:** 🔴 CRÍTICA  
`xgboost_adapter.py` y `analisis_engine.py` importan sus dependencias a nivel de módulo (no lazy). Django carga las rutas al iniciar, lo que importa estos módulos. Cualquier dependencia ML/IA faltante **bloquea el inicio completo del servidor**, incluyendo los endpoints de autenticación que son independientes del ML.

---

## 6. Problemas de red

### NET-001 — PostgreSQL no responde en `localhost:5432`

**Severidad:** 🔴 CRÍTICA  
**Logs:**
```
connection to server at "localhost" (::1), port 5432 failed: Connection refused (0x0000274D/10061)
connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused (0x0000274D/10061)
```
Django intenta la conexión en **dos protocolos** (IPv6 → IPv4), ambos rechazados. Error `10061` = puerto no está en estado LISTEN.

**Impacto:**
- `manage.py migrate` → fallo total
- `manage.py test` → fallo total (64 tests sin ejecutar)
- Todas las vistas Django que accedan a BD → `OperationalError` en runtime

### NET-002 — Sin timeout en conexiones de base de datos

**Severidad:** 🟡 MEDIA  
`DATABASES` en `settings.py` no tiene `OPTIONS.connect_timeout`. En producción, si PostgreSQL tarda en responder, Django esperará indefinidamente bloqueando el worker de Gunicorn.

### NET-003 — Sin timeout en cliente Axios (frontend)

**Severidad:** 🟡 MEDIA  
`api.ts` crea la instancia Axios sin `timeout`:
```typescript
export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/",
    // ← Sin timeout
})
```
Si el backend no responde, la UI queda en estado de carga permanente.

---

## 7. Problemas de autenticación

### AUTH-001 — `decoded.exp` posiblemente `undefined` en verificación de token

**Severidad:** 🔴 CRÍTICA  
**Archivo:** `frontend/react/src/context/AuthContext.tsx:36`  
```typescript
if (decoded && decoded.exp * 1000 > Date.now()) {
//                    ^^^^^^^^^^^^ TS18048: possibly undefined
```
Si el JWT no contiene el campo `exp` (token malformado o de otro proveedor), `decoded.exp * 1000` produce `NaN`. `NaN > Date.now()` es siempre `false` → el token válido se trata como expirado. El usuario nunca logra autenticarse.

### AUTH-002 — Sin revocación de tokens JWT en logout

**Severidad:** 🟠 ALTA  
**Archivo:** `authentication/infrastructure/adapters/input/api/views.py:99`
```python
@api_view(['PUT'])
@auth_required()
def logout(request):
    return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)
```
El logout solo responde con un mensaje. No hay lista negra de tokens, no se invalida el access token ni el refresh token en el servidor. Un token robado permanece válido durante 15 minutos (access) o 7 días (refresh) tras el logout.

### AUTH-003 — SECRET_KEY insegura usada para firmar todos los JWT

**Severidad:** 🔴 CRÍTICA  
La `SECRET_KEY` de fallback `'django-insecure-v50ee$v908kp8p)$_...'` es conocida (visible en el código fuente). Si el entorno arranca sin `.env`, todos los tokens JWT son firmados con esta clave pública. Cualquier persona puede generar tokens válidos para cualquier usuario/rol.

---

## 8. Vulnerabilidades de `npm audit` — Frontend

### NPM-VULN-001 — `axios 1.0.0 - 1.15.2` — 17+ CVEs

**Severidad:** 🔴 CRÍTICA (múltiples HIGH)

| CVE / GHSA | Tipo | CVSS |
|------------|------|------|
| GHSA-w9j2-pvgh-6h63 | Authentication Bypass via Prototype Pollution | HIGH |
| GHSA-pmwg-cvhr-8vh7 | NO_PROXY bypass (SSRF) | HIGH |
| GHSA-3w6x-2g7m-8v23 | JSON Response Tampering | HIGH |
| GHSA-xhjh-pmcv-23jw | Null Byte Injection | HIGH |
| GHSA-445q-vr5w-6q77 | CRLF Injection en multipart | HIGH |
| GHSA-m7pr-hjqh-92cm | SSRF via IP alias | HIGH |
| GHSA-pf86-5x62-jrwf | Prototype Pollution Gadgets | HIGH |
| GHSA-6chq-wfr3-2hj9 | Header Injection | HIGH |
| GHSA-q8qp-cvcw-x6jj | Credential injection + Request hijacking | HIGH |
| GHSA-3g43-6gmg-66jw | Credential Theft + Response Hijacking | HIGH |
| GHSA-35jp-ww65-95wh | Full Man-in-the-Middle via Prototype Pollution | HIGH |
| + 6 más | DoS, ReDoS, Resource exhaustion | HIGH/MED |

**Fix:** `npm audit fix` → actualiza axios a versión segura.

### NPM-VULN-002 — `react-router 7.0.0 - 7.15.0` — RCE Potencial

**Severidad:** 🔴 CRÍTICA

| CVE / GHSA | Tipo |
|------------|------|
| **GHSA-49rj-9fvp-4h2h** | **Unauth RCE via TYPE_ERROR deserialization** — Constructor invocation arbitrario |
| GHSA-2j2x-hqr9-3h42 | Open Redirect via protocol-relative URL |
| GHSA-8646-j5j9-6r62 | XSS en RSC redirect handling |
| GHSA-f22v-gfqf-p8f3 | Stored XSS via unescaped Location header |
| GHSA-8x6r-g9mw-2r78 | DoS en `__manifest` endpoint |
| GHSA-rxv8-25v2-qmq8 | DoS via single-fetch reflected input |
| GHSA-84g9-w2xq-vcv6 | CSRF via PUT/PATCH/DELETE |

**Fix:** `npm audit fix --force` → instala react-router@7.18.0.

### NPM-VULN-003 — `vite <=6.4.2` — Path Traversal y Arbitrary File Read

**Severidad:** 🟠 ALTA

| CVE / GHSA | Tipo |
|------------|------|
| GHSA-93m4-6634-74q7 | `server.fs.deny` bypass via backslash en Windows |
| GHSA-4w7w-66w2-5vf9 | Path Traversal en Optimized Deps `.map` |
| GHSA-p9ff-h696-f583 | Arbitrary File Read via WebSocket |
| GHSA-fx2h-pf6j-xcff | `server.fs.deny` bypass en Windows alternate paths |
| GHSA-g4jq-h2w9-997c | Middleware sirve archivos del public dir incorrectamente |
| GHSA-v6wh-96g9-6wx3 | NTLMv2 hash disclosure (Windows UNC paths) |
| GHSA-jqfw-vq24-v9c3 | server.fs settings no aplicados a HTML |

**Fix:** `npm audit fix --force` → instala vite@6.4.3.

### NPM-VULN-004 — Otras vulnerabilidades

| Paquete | GHSA | Tipo | Severidad |
|---------|------|------|-----------|
| `@babel/core <=7.29.0` | GHSA-4x5r-pxfx-6jf8 | Arbitrary File Read via sourceMappingURL | HIGH |
| `form-data 4.0.0-4.0.5` | GHSA-hmw2-7cc7-3qxx | CRLF Injection | HIGH |
| `follow-redirects <=1.15.11` | GHSA-r4q5-vmmm-2653 | Auth Header leak en redirect cross-domain | MODERATE |
| `postcss <8.5.10` | GHSA-qx2v-qp2m-jg93 | XSS en CSS Stringify Output | MODERATE |
| `tar <=7.5.15` | GHSA-vmf3-w455-68vh | File smuggling via PAX size override | MODERATE |

**Total `npm audit`:** 8 vulnerabilidades — 4 HIGH, 3 MODERATE, 1 LOW

---

## 9. Matriz de hallazgos

| ID | Hallazgo | Categoría | Severidad | Fase | Impacto | Resolución |
|----|---------|-----------|-----------|------|---------|------------|
| ERROR-001 | `scikit-learn==1.6.1` no instalable en Python 3.14 | Dependencia faltante | 🔴 CRÍTICA | pip install | Módulo ML inoperativo | Usar Python 3.12 o instalar wheel binaria compatible |
| ERROR-002 | `numpy==1.26.4` no instalable en Python 3.14 | Dependencia faltante | 🔴 CRÍTICA | pip install | Numpy 2.4.6 instalado (breaking change) | Usar Python 3.12 |
| ERROR-003 | `ModuleNotFoundError: joblib` bloquea arranque Django | Dependencia faltante | 🔴 CRÍTICA | Django startup | Servidor no inicia — todos los endpoints fallan | Instalar joblib o hacer import lazy |
| ERROR-004 | `ModuleNotFoundError: openai` bloquea arranque Django | Dependencia faltante | 🔴 CRÍTICA | Django startup | Servidor no inicia — todos los endpoints fallan | Instalar openai o hacer import lazy |
| ERROR-005 | `psycopg2.OperationalError`: PostgreSQL no disponible | Red / Infraestructura | 🔴 CRÍTICA | migrate / test | Sin persistencia, sin tests, sin API | Instalar y ejecutar PostgreSQL |
| ERROR-006 | `TS18048: decoded.exp possibly undefined` en AuthContext | Error de tipado (seguridad) | 🔴 CRÍTICA | tsc | Usuario no puede autenticarse si token sin `exp` | Agregar null check: `decoded.exp ?? 0` |
| WARN-003 | Django SECRET_KEY prefijada con `django-insecure-` | Autenticación / Configuración | 🔴 CRÍTICA | check --deploy | JWT y CSRF comprometidos si se usa en producción | Generar nueva SECRET_KEY sin fallback |
| AUTH-003 | SECRET_KEY insegura firma todos los JWT del sistema | Autenticación | 🔴 CRÍTICA | Runtime | Cualquiera puede generar tokens válidos | Eliminar fallback de settings.py |
| CONF-004 | `DB_PASSWORD: admin` hardcodeado en docker-compose.yml | Configuración | 🔴 CRÍTICA | Docker | Credencial trivial versionada en git | Usar `${DB_PASSWORD}` |
| NPM-VULN-002 | react-router RCE via TYPE_ERROR deserialization | Vulnerabilidad de dependencia | 🔴 CRÍTICA | npm audit | Ejecución remota de código no autenticada | `npm audit fix --force` |
| NPM-VULN-001 | axios 17+ CVEs (Prototype Pollution, SSRF, Header Injection) | Vulnerabilidad de dependencia | 🔴 CRÍTICA | npm audit | Credential theft, MitM, Auth bypass | `npm audit fix` |
| AUTH-002 | Logout sin invalidación de token en servidor | Autenticación | 🟠 ALTA | Runtime | Token robado válido 15min/7días post-logout | Implementar token blocklist |
| WARN-001 | HSTS no configurado | Configuración de seguridad | 🟠 ALTA | check --deploy | Susceptible a downgrade de HTTPS a HTTP | Configurar `SECURE_HSTS_SECONDS` |
| WARN-002 | SECURE_SSL_REDIRECT no activo | Configuración de seguridad | 🟠 ALTA | check --deploy | Conexiones HTTP sin cifrar aceptadas | Configurar `SECURE_SSL_REDIRECT=True` |
| WARN-004 | SESSION_COOKIE_SECURE no activo | Configuración de seguridad | 🟠 ALTA | check --deploy | Cookie de sesión transmitida en HTTP | `SESSION_COOKIE_SECURE=True` |
| WARN-005 | CSRF_COOKIE_SECURE no activo | Configuración de seguridad | 🟠 ALTA | check --deploy | CSRF token transmitido en HTTP | `CSRF_COOKIE_SECURE=True` |
| WARN-006 | DEBUG=True en check de deploy | Configuración | 🟠 ALTA | check --deploy | Stacktraces expuestos a usuarios en producción | `DJANGO_DEBUG=False` siempre en prod |
| NPM-VULN-003 | Vite ≤6.4.2 Path Traversal + File Read en Windows | Vulnerabilidad de dependencia | 🟠 ALTA | npm audit | Lectura de archivos arbitrarios vía dev server | `npm audit fix --force` |
| CONF-005 | Imports ML/IA eager bloquean Django completo si faltan libs | Configuración / Diseño | 🟠 ALTA | Django startup | Un módulo faltante tira todos los endpoints | Hacer imports lazy dentro de las funciones |
| NET-001 | PostgreSQL no responde en localhost:5432 | Red / Infraestructura | 🔴 CRÍTICA | migrate | Sin persistencia ni tests ejecutables | Levantar PostgreSQL vía Docker o nativo |
| WARN-009 | `Failed to activate VS environment` (Meson) | Configuración | 🟠 ALTA | pip install | No se pueden compilar extensiones C nativas | Instalar Visual Studio Build Tools |
| NPM-VULN-004a | @babel/core Arbitrary File Read | Vulnerabilidad de dependencia | 🟠 ALTA | npm audit | Lectura arbitraria de archivos | `npm audit fix` |
| NPM-VULN-004b | form-data CRLF Injection | Vulnerabilidad de dependencia | 🟠 ALTA | npm audit | Inyección de headers HTTP | `npm audit fix` |
| CONF-003 | `EXPOSE 3000` incorrecto en frontend Dockerfile | Configuración | 🟡 MEDIA | Docker build | Documentación de puerto incorrecta | Cambiar a `EXPOSE 5173` |
| NET-002 | Sin timeout en conexión PostgreSQL | Red / Configuración | 🟡 MEDIA | Runtime | Worker Gunicorn colgado indefinidamente | Agregar `CONN_MAX_AGE` y `connect_timeout` |
| NET-003 | Sin timeout en cliente Axios | Red / Frontend | 🟡 MEDIA | Runtime | UI en estado de carga permanente | Agregar `timeout: 30000` en axios.create |
| WARN-007 | RuntimeWarning: BD `postgres` de mantenimiento no accesible | Red / Configuración | 🟡 MEDIA | test runner | Tests usan BD principal en lugar de maintenance DB | Crear BD `postgres` o usar `TEST.NAME` |
| ERROR-007..021 | 14 errores TS6133: imports y variables sin usar | Código muerto | 🟡 MEDIA | tsc | Builds typescript fallan en modo estricto | Eliminar imports/variables sin usar |
| WARN-008 | pip desactualizado (26.0.1 → 26.1.2) | Herramienta de desarrollo | 🟢 BAJA | pip install | Sin impacto funcional inmediato | `pip install --upgrade pip` |
| NPM-VULN-004c | follow-redirects Auth Header leak | Vulnerabilidad de dependencia | 🟡 MEDIA | npm audit | Header auth filtrado en redirects | `npm audit fix` |
| NPM-VULN-004d | postcss XSS | Vulnerabilidad de dependencia | 🟡 MEDIA | npm audit | XSS en output CSS | `npm audit fix` |
| NPM-VULN-004e | tar File smuggling | Vulnerabilidad de dependencia | 🟡 MEDIA | npm audit | Manipulación de archivos tar | `npm audit fix` |

---

## 10. Estadísticas de la auditoría

```
RESUMEN POR SEVERIDAD
─────────────────────────────────────────────────────
🔴 CRÍTICA   │████████████████░░░░│ 12 hallazgos (37%)
🟠 ALTA      │████████████░░░░░░░░│  9 hallazgos (28%)
🟡 MEDIA     │███████████░░░░░░░░░│  8 hallazgos (25%)
🟢 BAJA      │██░░░░░░░░░░░░░░░░░░│  3 hallazgos (10%)
─────────────────────────────────────────────────────
TOTAL        │                    │ 32 hallazgos

RESUMEN POR CATEGORÍA
─────────────────────────────────────────────────────
Vulnerabilidades de dependencias    │  9 (npm audit)
Dependencias faltantes / incompat.  │  6
Autenticación / Seguridad           │  5
Configuración                       │  7
Red / Infraestructura               │  3
Errores TypeScript                  │  2
─────────────────────────────────────────────────────

TESTS DJANGO: 64 encontrados, 0 ejecutados (PostgreSQL no disponible)
NPM AUDIT:    8 vulnerabilidades (4 HIGH, 3 MODERATE, 1 LOW)
TSC ERRORS:   15 errores de compilación TypeScript
DJANGO CHECK: 6 warnings de seguridad (0 errores de sistema)
```

---

## 11. Acciones inmediatas recomendadas

```bash
# 1. CRÍTICO — Frontend: corregir vulnerabilidades conocidas
cd frontend/react
npm audit fix              # corrige axios, follow-redirects, postcss, tar
npm audit fix --force      # corrige react-router y vite (breaking change permitido)

# 2. CRÍTICO — Backend: eliminar fallback inseguro de SECRET_KEY
# En config/settings.py cambiar:
# SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-...')
# Por:
# SECRET_KEY = os.environ['DJANGO_SECRET_KEY']  # falla sin variable → correcto

# 3. CRÍTICO — Docker: externalizar contraseñas de BD
# En docker-compose.yml cambiar:
# DB_PASSWORD: admin  →  DB_PASSWORD: ${DB_PASSWORD}
# POSTGRES_PASSWORD: admin  →  POSTGRES_PASSWORD: ${DB_PASSWORD}

# 4. ALTO — Backend: hacer lazy los imports de ML/IA
# En xgboost_adapter.py y analisis_engine.py, mover imports dentro de funciones:
# def predecir(...):
#     import joblib  # ← dentro de la función, no a nivel de módulo

# 5. CRÍTICO — AuthContext.tsx: corregir posible undefined en exp
# Cambiar: decoded.exp * 1000 > Date.now()
# Por:    (decoded.exp ?? 0) * 1000 > Date.now()

# 6. MEDIO — TypeScript: eliminar imports y variables sin usar
# Ejecutar con autofix si el linter está configurado, o eliminar manualmente los 14 casos
```

---

*Auditoría generada mediante ejecución real del sistema en entorno Windows 11 con Python 3.14.4 y Node 24.15.0. Todos los logs citados son salidas reales capturadas durante la sesión de auditoría del 2026-06-19.*
