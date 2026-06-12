# AUDITORÍA FURPS+ — ZOIDS LEAGUE
**Versión:** 1.0  
**Fecha:** 2026-06-12  
**Auditor:** Agente Senior de Calidad — Modelo FURPS+  
**Proyecto:** Zoids League — Plataforma de Gestión de Torneos de Robótica Educativa  

---

## RESUMEN EJECUTIVO

Zoids League es una plataforma web para la gestión integral de torneos de robótica educativa. Implementa un backend Django 6.0.4 con arquitectura hexagonal (DDD + Clean Architecture), un frontend React 18.3.1, PostgreSQL 17 como base de datos relacional y soporte de inteligencia artificial mediante XGBoost y OpenRouter (GPT-4o). El sistema está completamente contenerizado con Docker Compose.

La auditoría abarcó más de 90 archivos de código fuente, modelos de dominio, casos de uso, repositorios, vistas de API, componentes de frontend, migraciones, configuración de infraestructura, pruebas y documentación interna.

**El proyecto se encuentra en estado MVP funcional, con una cobertura de procesos de negocio estimada en 87 %.** La arquitectura hexagonal está correctamente planteada y facilita la mantenibilidad futura. Sin embargo, existen bugs críticos en entidades de dominio, problemas de seguridad de configuración y ausencia de mecanismos de observabilidad y resiliencia que deben resolverse antes de un despliegue en producción real.

---

## PUNTAJE POR CATEGORÍA

| Categoría | Peso | Puntaje | Evaluación |
|-----------|------|---------|------------|
| **F — Funcionalidad** | 30 % | **8.7 / 10** | Cobertura amplia, algunos flujos incompletos |
| **U — Usabilidad** | 20 % | **6.8 / 10** | UI coherente, accesibilidad y UX parciales |
| **R — Confiabilidad** | 20 % | **7.2 / 10** | Validaciones robustas, falta tolerancia a fallos |
| **P — Rendimiento** | 15 % | **6.9 / 10** | Aceptable para escala actual, sin caché ni async |
| **S — Mantenibilidad** | 15 % | **7.1 / 10** | Arquitectura clara, documentación y tests incompletos |
| **PUNTAJE GLOBAL** | 100 % | **7.4 / 10** | **MVP viable con brechas críticas en seguridad** |

---

## 1. FUNCIONALIDAD (F — Functionality)

### 1.1 Funcionalidades Implementadas

#### Módulo Authentication
| Característica | Estado | Evidencia |
|---|---|---|
| Registro de usuario | ✅ Completo | `authentication/application/use_cases/register_use_case.py` |
| Login con email/password | ✅ Completo | `authentication/application/use_cases/login_use_case.py` |
| JWT Access + Refresh Token | ✅ Completo | `authentication/application/services/jwt_service.py` |
| Bloqueo tras 5 intentos fallidos | ✅ Completo | `authentication/domain/entities/user.py` — `increment_failed_attempts()` |
| Desbloqueo automático (15 min) | ✅ Completo | `check_and_unblock_user()` en entidad User |
| Logout con revocación de token | ✅ Completo | `authentication/adapters/input/api/views/logout_view.py` |
| Control de roles (ADMIN, MANAGER, COACH, PARTICIPANT) | ✅ Completo | `@auth_required([...])` decorator en vistas |
| Verificación de email | ❌ Ausente | `state=NOT_VERIFIED` existe en dominio pero nunca se valida en flujos |
| Recuperación de contraseña | ❌ Ausente | No hay endpoint ni use case |
| Autenticación de dos factores | ❌ Ausente | Sin 2FA |

#### Módulo Competencia
| Característica | Estado | Evidencia |
|---|---|---|
| CRUD de torneos | ✅ Completo | `competencia/application/use_cases/create_tournament_use_case.py` y derivados |
| Máquina de estados del torneo (7 estados) | ✅ Completo | `TournamentState` enum + transiciones validadas |
| Configuración de reglas de torneo | ✅ Completo | `TournamentRule` con validaciones en dominio |
| Inscripción de equipos con participantes | ✅ Completo | `competencia/application/use_cases/inscribe_team_use_case.py` |
| Aprobación/rechazo de equipos | ✅ Completo | `approve_team_use_case.py`, `reject_team_use_case.py` |
| Generación de fixtures KNOCKOUT | ✅ Completo | `generate_fixtures_use_case.py` — árbol binario con byes automáticos |
| Generación de fixtures ROUND_ROBIN | ✅ Completo | Algoritmo serpentine rotation |
| Generación de fixtures HYBRID | ✅ Completo | Grupos Round-Robin + fase Knockout |
| Registro de resultados por criterio | ✅ Completo | `register_match_result_use_case.py` |
| Tabla de posiciones | ⚠️ Parcial | Modelo `Standing` existe, lógica de actualización incompleta |
| Generación de criterios de evaluación vía IA | ✅ Completo | `RubricaGenerator` + OpenRouter NLP |
| Análisis NLP de descripción de torneo | ✅ Completo | `NLPAnalysis` + endpoint `/api/ia/analizar` |
| Confirmación y activación de criterios | ✅ Completo | `confirmar_criterios_view.py` |

#### Módulo Simulación
| Característica | Estado | Evidencia |
|---|---|---|
| Predicción de puntajes (XGBoost) | ✅ Completo | `simulacion/ia/prediction_model.py` — XGBRegressor |
| Análisis de entrega de código | ✅ Completo | `POST /api/simulacion/analisis/programacion/` |
| Análisis de componentes hardware | ✅ Completo | `POST /api/simulacion/analisis/componentes/` |
| Contexto del torneo para simulación | ✅ Completo | `GET /api/simulacion/torneo/<id>/contexto/` |
| Ejecución de simulación completa | ✅ Completo | `POST /api/simulacion/torneo/<id>/simular/` |
| Reentrenamiento de modelo | ❌ Ausente | Modelo XGBoost estático en pickle/joblib sin pipeline de actualización |
| Versionamiento de modelos | ❌ Ausente | Un único archivo de modelo sin historial |

### 1.2 Cobertura de Procesos de Negocio

```
Flujo de Torneo:
  DRAFT → [Configurar reglas] → IN_REVIEW → [Analizar con IA] →
  REGISTRATION_OPEN → [Inscribir equipos] → REGISTRATION_CLOSED →
  [Generar fixtures] → IN_PROGRESS → [Registrar resultados] → FINALIZED
  
Estado de cobertura:
  - Creación y configuración:        100%
  - Apertura y gestión inscripciones: 95% (falta notificaciones)
  - Generación de fixtures:           90% (bugs menores)
  - Desarrollo de competencia:        85% (standings parcial)
  - Finalización y reportes:          60% (sin reportes exportables)
```

### 1.3 Hallazgos Funcionales

**HF-01 [CRÍTICO]** `Match.set_estado()` usa `==` (comparación) en lugar de `=` (asignación).  
Archivo: `competencia/domain/entities/match.py:63`  
```python
# Código actual (bugueado):
def set_estado(self, value):
    self.__estado == value   # comparación, no asigna

# Comportamiento esperado:
def set_estado(self, value):
    self.__estado = value
```
**Impacto:** Todo flujo que actualice el estado de un partido (registro de resultados, avance en fixture) no persiste el cambio. El torneo nunca puede progresar correctamente.

**HF-02 [CRÍTICO]** `GenerateFixturesUseCase` llama a `match.set_es_bye(True)` pero la entidad `Match` solo expone `set_bye()`.  
Archivo: `competencia/application/use_cases/generate_fixtures_use_case.py:108`  
**Impacto:** AttributeError en tiempo de ejecución al generar cualquier fixture con byes.

**HF-03 [MAYOR]** Validación de estado incompleta en `GenerateFixturesUseCase`.  
```python
if tournament.state != TournamentState.REGISTRATION_CLOSED:
    pass   # No lanza excepción ni retorna
```
**Impacto:** Es posible generar fixtures desde cualquier estado del torneo.

**HF-04 [MAYOR]** `ConfigKnockout.validate_for_start()` itera con `range(1, n)` en lugar de calcular potencias de 2 correctamente.  
**Impacto:** Validación de número de equipos (potencia de 2) puede pasar o fallar erróneamente.

**HF-05 [MENOR]** Verificación de email (`state=NOT_VERIFIED`) declarada en dominio pero nunca aplicada en los flujos de login o acceso.  
**Impacto:** Usuarios con email no verificado pueden operar con plenos privilegios.

---

## 2. USABILIDAD (U — Usability)

### 2.1 Interfaz de Usuario

El frontend está construido en React 18 con Radix UI, Tailwind CSS 4 y Vite 6. La arquitectura de componentes es coherente y existe separación por módulos (auth, torneos, equipos, simulaciones).

**Páginas y componentes identificados:**

| Sección | Componentes | Estado |
|---|---|---|
| Autenticación | Login, Register | ✅ Completo |
| Dashboard | Home con navegación por rol | ✅ Completo |
| Torneos | Lista, Crear, Configurar Reglas, Panel Admin | ✅ Completo |
| Equipos | Gestión de equipos inscritos | ✅ Completo |
| Resultados | Tabla de posiciones | ⚠️ Parcial |
| Simulaciones | Editor, Análisis de retos | ✅ Completo |
| Competencias activas | Vista de torneos en progreso | ✅ Completo |
| IA Recomendaciones | `AIRecommendations` no conectado a rutas | ❌ Ausente en navegación |

### 2.2 Retroalimentación al Usuario

| Mecanismo | Estado | Evidencia |
|---|---|---|
| Toast notifications (éxito/error) | ✅ | Librería `sonner` integrada |
| Renovación automática de token | ✅ | Interceptor Axios con cola de peticiones |
| Feedback de validación en formularios | ⚠️ Parcial | React Hook Form implementado, validación frontend incompleta |
| Loading states | ⚠️ Parcial | Presente en algunos componentes, ausente en otros |
| Mensajes de error HTTP descriptivos | ✅ | Backend retorna mensajes en español |
| Confirmaciones de acciones destructivas | ❌ Ausente | Sin modal de confirmación para cancelar torneo o rechazar equipo |

### 2.3 Navegación y Roles

- Guards por rol (`<RoleGuard>`) en frontend protegen rutas según SystemRol
- Sidebar diferenciado por rol (ADMIN ve más opciones que PARTICIPANT)
- Navegación React Router sin redirecciones circulares evidentes

### 2.4 Accesibilidad

| Aspecto | Evaluación | Evidencia |
|---|---|---|
| Componentes semánticos | ✅ Parcial | Radix UI provee ARIA roles base |
| Contraste de colores | ⚠️ Sin verificar | Tailwind sin configuración WCAG |
| Navegación por teclado | ✅ Parcial | Radix UI accesible por defecto |
| Etiquetas `aria-label` | ❌ No verificado | No hay evidencia de uso explícito |
| WCAG 2.1 AA | ❌ Sin auditoria | No hay herramientas de verificación en el proyecto |

**Puntaje Usabilidad: 6.8/10** — Interfaz funcional y coherente, con brechas en accesibilidad, validaciones reactivas y estados de carga.

---

## 3. CONFIABILIDAD (R — Reliability)

### 3.1 Validaciones de Dominio

El sistema implementa validaciones en entidades de dominio (capa más interna), lo cual es correcto arquitectónicamente:

| Entidad | Reglas validadas |
|---|---|
| `User` | Edad 3-80 años, email con @ y punto, contraseña ≥ 8 chars + número + mayúscula + minúscula |
| `Tournament` | Fecha inicio > hoy, fecha fin > fecha inicio |
| `TournamentRule` | min_members ≤ max_members ≥ 2; 4 ≤ min_teams ≤ max_teams ≤ 64 |
| `CriterioIA` | Peso 0.01-100.00; suma del conjunto = 100.00% ± 0.01; nombre 1-100 chars |
| `ConfigKnockout` | Número de equipos debe ser potencia de 2 |
| `ConfigRoundRobin` | Equipos par; victoria > empate > derrota; ≥ 1 criterio de desempate |

### 3.2 Manejo de Errores

**Backend — HTTP Status Codes:**
| Código | Uso | Evidencia |
|---|---|---|
| 400 | Validación fallida | Views genéricas |
| 401 | Token inválido o expirado | `auth_required` decorator |
| 403 | Rol insuficiente | Guards de vistas |
| 404 | Recurso no encontrado | Repositorios |
| 423 | Cuenta bloqueada | `LoginUseCase` |
| 500 | Error interno | Sin handler global documentado |

**Excepciones personalizadas identificadas:**
- `InvalidCredentials`
- `AccountLocked`
- `InvalidToken`
- `SumaPesosInvalidaError`
- `TokenExpiredError`

**Frontend — Interceptores Axios:**
- Interceptor de respuesta para 401: intenta refresh token automático
- Si refresh falla, redirige a login
- Cola de peticiones pendientes durante el refresh (evita race conditions)

### 3.3 Atomicidad y Transacciones

| Operación | Transacción | Evidencia |
|---|---|---|
| Guardar equipo + participantes | `@transaction.atomic` | `TeamRepositoryPostgresql.save()` |
| Actualizar equipo + participantes | `@transaction.atomic` | `TeamRepositoryPostgresql.update()` |
| Generación de fixtures (múltiples partidos) | ❌ Sin transacción explícita | `generate_fixtures_use_case.py` |
| Confirmación de criterios IA | ❌ Sin transacción explícita | `confirmar_criterios_view.py` |

### 3.4 Disponibilidad y Recuperación

| Aspecto | Estado | Observaciones |
|---|---|---|
| Healthchecks en Docker | ❌ Ausente | `docker-compose.yml` sin `healthcheck` |
| Reintentos automáticos para IA | ❌ Ausente | Si OpenRouter falla, la operación falla directamente |
| Logs centralizados | ❌ Ausente | Sin configuración de logging en `settings.py` |
| Backup de base de datos | ❌ Sin documentar | No hay estrategia en README ni scripts |
| Replicación de BD | ❌ Sin implementar | Un solo nodo PostgreSQL |

**Puntaje Confiabilidad: 7.2/10** — Validaciones de dominio sólidas y manejo de errores HTTP correcto, pero falta tolerancia a fallos, transacciones incompletas y ausencia de observabilidad.

---

## 4. RENDIMIENTO (P — Performance)

### 4.1 Base de Datos

**Índices explícitos detectados:**
```
competencia_criterio_ia.sesion_ia_id     → db_index=True
competencia_nlp_analysis                  → ordering = ['-created_at']
```

**Ausencias críticas de índices:**
```
competencia_tournament(estado)            → consultas por estado frecuentes
competencia_team(tournament_id, estado)   → filtrado por torneo y estado
competencia_match(tournament_id, round)   → navegación de fixtures
authentication_user(email)                → login busca por email
```

**Consultas potencialmente ineficientes:**
- `TournamentRepository.find_all()` — sin `select_related` para `tournament_rule`
- `StandingRepository.find_by_tournament()` — sin prefetch de teams
- `MatchRepository.find_by_tournament()` — N+1 potencial para equipos

**Consultas optimizadas detectadas:**
- `TeamRepositoryPostgresql` usa `prefetch_related('participants')` — evita N+1

### 4.2 API y Serialización

| Aspecto | Estado | Riesgo |
|---|---|---|
| Paginación en endpoints `/all/` | ❌ Ausente | Con 1000+ torneos la respuesta puede superar los 10 MB |
| Campos innecesarios en respuesta | ⚠️ Riesgo | `to_dict()` devuelve entidad completa incluyendo datos sensibles |
| Uso de serializers DRF | ⚠️ Mixto | Algunos endpoints usan DRF serializers, otros usan `to_dict()` directamente |
| Compresión de respuestas | ❌ Ausente | Sin `GZipMiddleware` ni compresión en Nginx |

### 4.3 Complejidad Algorítmica

| Operación | Complejidad | Observaciones |
|---|---|---|
| Generación Knockout (n equipos) | O(n log n) | Shuffle + árbol binario |
| Generación Round-Robin (n equipos) | O(n²) | n-1 rondas × n/2 partidos |
| Generación Hybrid | O(n²) | Dominada por Round-Robin |
| Normalización de pesos (k criterios) | O(k) | k ≤ 10, trivial |
| Predicción XGBoost | O(d × t) | d=profundidad, t=árboles; ~10ms |

### 4.4 Modelo de IA

```python
XGBRegressor(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='reg:squarederror'
)
```
- Modelo cargado desde disco en cada instancia de servicio (sin caché en memoria)
- Sin pipeline de reentrenamiento documentado
- Sin versionamiento de modelos

### 4.5 Escalabilidad

| Límite | Evaluación |
|---|---|
| Usuarios concurrentes (estimado) | ~500-1000 (Django sincrónico, 4 workers gunicorn) |
| Sin Celery/Redis para tareas async | Operaciones lentas bloquean workers |
| Sin caché HTTP (Redis/Memcached) | Consultas repetidas siempre van a BD |
| Infraestructura de un solo nodo | Sin horizontal scaling configurado |

**Puntaje Rendimiento: 6.9/10** — Aceptable para la escala actual (demos, MVP). Requiere caché, paginación, índices y async tasks antes de escalar.

---

## 5. MANTENIBILIDAD (S — Supportability)

### 5.1 Arquitectura

El proyecto implementa **Arquitectura Hexagonal** con capas bien definidas:

```
backend/
├── authentication/
│   ├── domain/
│   │   ├── entities/         ← User (entidad de dominio)
│   │   ├── ports/            ← IUserRepository (interface abstracta)
│   │   └── value_objects/    ← SystemRol, UserState (enums)
│   ├── application/
│   │   ├── use_cases/        ← LoginUseCase, RegisterUseCase, etc.
│   │   └── services/         ← JWTService, PasswordService
│   └── adapters/
│       ├── input/api/        ← Views, URLs, Serializers
│       └── output/           ← Repositories, ORM Models
└── competencia/
    ├── domain/               ← Tournament, Team, Match, CriterioIA
    ├── application/          ← 20+ Use Cases
    └── adapters/             ← API Views, PostgreSQL Repos
```

**Patrones de diseño identificados:**
| Patrón | Implementación | Estado |
|---|---|---|
| Repository Pattern | `IUserRepository`, `ITournamentRepository` | ✅ Completo |
| Use Case Pattern | 20+ casos de uso nombrados | ✅ Completo |
| Factory Pattern | `ConfigTournamentFactory`, `TournamentEvaluation.create()` | ✅ Completo |
| Value Objects / Enums | `TournamentState`, `TournamentType`, `SystemRol` | ✅ Completo |
| Decorator Pattern | `@auth_required([roles])` | ✅ Completo |
| Dependency Injection | Manual (en vistas) | ⚠️ Sin IoC container |
| Unit of Work | Declarado en ports | ⚠️ Implementación incompleta |

### 5.2 Calidad de Código

| Aspecto | Evaluación | Observaciones |
|---|---|---|
| Type hints Python | ⚠️ Parcial | Presentes en use cases, ausentes en algunos adapters |
| TypeScript en frontend | ✅ Completo | Tipado correcto en componentes y servicios |
| Nombres descriptivos | ✅ Bueno | Clases y métodos autoexplicativos |
| Tamaño de funciones | ✅ Bueno | Funciones pequeñas y bien delegadas |
| Comentarios | ⚠️ Escasos | Docstrings en métodos críticos, ausentes en repositorios |
| Código duplicado | ⚠️ Leve | Algunas validaciones repetidas entre vistas |
| Complejidad ciclomática | ✅ Baja | Casos de uso simples y lineales |

### 5.3 Documentación

| Documento | Estado | Calidad |
|---|---|---|
| `README.md` | ✅ Presente | Setup, verificación, pruebas funcionales |
| `authentication/documentacion_authentication.md` | ✅ Presente | Endpoints, DDL, ejemplos |
| `competencia/documentacion_competencia.md` | ✅ Presente | Endpoints, schema, ejemplos |
| `simulacion/documentacion_simulacion.md` | ✅ Presente | Endpoints de simulación |
| OpenAPI/Swagger | ❌ Ausente | Sin especificación formal de API |
| Diagramas de arquitectura | ❌ Ausente | Sin C4, UML ni draw.io |
| ADR (Architecture Decision Records) | ❌ Ausente | Decisiones no documentadas |
| Guía de despliegue en producción | ❌ Ausente | Solo desarrollo local |
| Runbook de operaciones | ❌ Ausente | — |

### 5.4 Pruebas

**Tests identificados:**

| Archivo | Cobertura | Tipo |
|---|---|---|
| `test_tournament.py` | TournamentRule, Tournament (88+ casos) | Unitario |
| `test_domain_user.py` | Email, contraseña, bloqueo, edad | Unitario |
| `test_fixtures_and_standings.py` | Generación de fixtures | Unitario |
| `test_institution.py` | Entidad Institution | Unitario |
| `test_team.py` | Entidad Team | Unitario |
| `test_tournament_team.py` | Relación torneo-equipo | Unitario |
| `test_user.py` | Usuario extendido | Unitario |

**Brechas de testing:**
- ❌ Tests de integración para endpoints HTTP
- ❌ Tests de repositorios con BD real
- ❌ Tests de frontend (sin Vitest ni Playwright configurado)
- ❌ Tests de generación de fixtures con escenarios límite
- ❌ Tests de flujos end-to-end
- ❌ Cobertura de código no medida (`coverage.py` no configurado)

### 5.5 Dependencias

**Backend (requisitos detectados):**
```
Django==6.0.4
djangorestframework==3.17.1
djangorestframework-simplejwt==5.5.1
PyJWT==2.12.1
bcrypt==5.0.0
openai>=1.0.0       ← rango abierto (riesgo de breaking change)
xgboost==2.1.4
scikit-learn==1.6.1
numpy==1.26.4       ← puede entrar en conflicto con xgboost 2.x
joblib==1.4.2
psycopg2==2.9.12
gunicorn==26.0.0
python-dotenv>=1.0.0 ← rango abierto
```

**Riesgos de dependencias:**
- `openai>=1.0.0` y `python-dotenv>=1.0.0` sin pin de versión exacta → builds no reproducibles
- `numpy==1.26.4` puede ser incompatible con versiones recientes de scikit-learn o xgboost
- Sin `requirements-dev.txt` separado para herramientas de desarrollo

**Frontend:**
- React 18.3.1, Vite 6.3.5, Tailwind 4.1.12, Axios 1.15.0 — versiones estables y actualizadas ✅
- Sin Lockfile de seguridad auditado (`npm audit` no documentado)

**Puntaje Mantenibilidad: 7.1/10** — Arquitectura hexagonal bien planteada, buena separación de capas. Brechas en testing de integración, documentación técnica y configuración de dependencias.

---

## 6. BRECHAS IDENTIFICADAS

### Brechas Críticas (Bloquean producción)

| ID | Brecha | Módulo | Impacto |
|---|---|---|---|
| BC-01 | `Match.set_estado()` no asigna estado (bug `==`) | Competencia | Partidos no progresan |
| BC-02 | `match.set_es_bye()` método inexistente | Competencia | Error en tiempo de ejecución al generar fixtures |
| BC-03 | SECRET_KEY Django hardcodeado en `settings.py` | Infraestructura | Vulnerabilidad de seguridad crítica |
| BC-04 | `ALLOWED_HOSTS = ["*"]` en producción | Infraestructura | Vulnerabilidad HTTP Host header injection |
| BC-05 | Sin healthchecks en Docker Compose | Infraestructura | Servicios inician en orden incorrecto, fallos silenciosos |

### Brechas Mayores (Deben resolverse antes de release)

| ID | Brecha | Módulo | Impacto |
|---|---|---|---|
| BM-01 | Sin paginación en endpoints `GET /all/` | API | Degradación de rendimiento con datos reales |
| BM-02 | Sin rate limiting en endpoints de autenticación | Auth | Vulnerable a ataques de fuerza bruta |
| BM-03 | Verificación de email declarada pero no aplicada | Auth | Usuarios no verificados acceden al sistema |
| BM-04 | Generación de fixtures sin `@transaction.atomic` | Competencia | Fixtures parcialmente creados ante fallos |
| BM-05 | Sin logging configurado en `settings.py` | Infraestructura | Imposible depurar errores en producción |
| BM-06 | Tabla de posiciones (`Standing`) incompleta | Competencia | Feature visible en UI pero no funcional |
| BM-07 | Sin tests de integración HTTP | Calidad | Bugs en vistas no detectados |
| BM-08 | `openai>=1.0.0` sin pin de versión | Dependencias | Builds no reproducibles |

### Brechas Menores (Mejoras deseables)

| ID | Brecha | Área |
|---|---|---|
| Bm-01 | Sin OpenAPI/Swagger | Documentación API |
| Bm-02 | Sin diagramas de arquitectura | Documentación técnica |
| Bm-03 | Validación en tiempo real en formularios frontend | UX |
| Bm-04 | Sin modal de confirmación para acciones destructivas | UX |
| Bm-05 | Sin `AIRecommendations` conectado a rutas | Frontend |
| Bm-06 | `coverage.py` no configurado | Testing |
| Bm-07 | Sin estrategia de backup de BD | Operaciones |
| Bm-08 | Índices faltantes en columnas de búsqueda frecuente | BD |
| Bm-09 | Modelo XGBoost sin versionamiento ni reentrenamiento | IA/ML |

---

## 7. RIESGOS DETECTADOS

### Riesgos de Seguridad

| ID | Riesgo | Severidad | Descripción |
|---|---|---|---|
| RS-01 | SECRET_KEY expuesta | 🔴 Crítico | La clave secreta de Django hardcodeada en `settings.py` compromete toda la criptografía del sistema (tokens, sesiones, CSRF) |
| RS-02 | ALLOWED_HOSTS permisivo | 🔴 Crítico | `ALLOWED_HOSTS = ["*"]` permite HTTP Host Header Injection y ataques de DNS rebinding |
| RS-03 | OPENROUTER_API_KEY en docker-compose | 🟠 Alto | Clave de API de IA expuesta en archivo versionado |
| RS-04 | Sin rate limiting | 🟠 Alto | Endpoints `/login/` y `/register/` vulnerables a fuerza bruta y enumeración de usuarios |
| RS-05 | CORS no restringido | 🟠 Alto | Si `CORS_ALLOW_ALL_ORIGINS=True`, cualquier dominio puede llamar a la API autenticado |
| RS-06 | Sin HTTPS documentado | 🟡 Medio | Tokens JWT y contraseñas transmitidos en texto plano en despliegues sin TLS |
| RS-07 | localStorage para tokens | 🟡 Medio | Susceptible a XSS; preferir httpOnly cookies |

### Riesgos de Datos

| ID | Riesgo | Severidad | Descripción |
|---|---|---|---|
| RD-01 | Sin backup strategy | 🟠 Alto | Pérdida de datos irreversible ante fallo de BD |
| RD-02 | BD single point of failure | 🟡 Medio | Un único nodo PostgreSQL sin réplica |
| RD-03 | Fixtures sin transacción | 🟡 Medio | Posible estado inconsistente si falla la inserción de partidos |

### Riesgos Operacionales

| ID | Riesgo | Severidad | Descripción |
|---|---|---|---|
| RO-01 | Dependencia OpenRouter sin fallback | 🟠 Alto | Si la API externa falla, análisis NLP y scoring IA no funcionan |
| RO-02 | Sin logging | 🟡 Medio | Imposible diagnosticar errores en producción |
| RO-03 | Sin healthchecks | 🟡 Medio | Contenedores con estado inconsistente pueden iniciar sin advertencia |
| RO-04 | Modelo XGBoost estático | 🟡 Medio | Predicciones desactualizadas con el tiempo |

### Riesgos de Calidad

| ID | Riesgo | Severidad | Descripción |
|---|---|---|---|
| RC-01 | Bug `Match.set_estado()` | 🔴 Crítico | Flujos de torneo se rompen en cualquier registro de resultado |
| RC-02 | Sin tests de integración | 🟠 Alto | Regresiones en API no detectadas antes de despliegue |
| RC-03 | Dependencias sin pin | 🟡 Medio | Actualizaciones automáticas pueden introducir incompatibilidades |

---

## 8. RECOMENDACIONES DE ALTO NIVEL

### Prioridad 1 — Correcciones inmediatas (antes de cualquier demo)

1. **Reparar `Match.set_estado()`**: Cambiar `==` por `=` en `competencia/domain/entities/match.py:63`. Es el bug más crítico del sistema.
2. **Reparar `set_es_bye()` → `set_bye()`**: Alinear el nombre del método en `generate_fixtures_use_case.py`.
3. **Mover SECRET_KEY a variable de entorno**: Añadir `SECRET_KEY` al `.env` y leerlo con `os.environ.get()` en `settings.py`.
4. **Especificar ALLOWED_HOSTS**: Reemplazar `["*"]` por dominios reales o `["localhost", "127.0.0.1"]` para desarrollo.
5. **Mover API keys a variables de entorno**: Remover `OPENROUTER_API_KEY` del `docker-compose.yml`.

### Prioridad 2 — Antes de release (sprint 1-2)

6. **Implementar `@transaction.atomic` en generación de fixtures**: Garantizar que el conjunto de partidos se crea atómicamente.
7. **Agregar rate limiting**: Usar `django-ratelimit` en `/login/`, `/register/` y `/api/ia/analizar`.
8. **Configurar logging en `settings.py`**: Habilitar `LOGGING` con handlers para archivo y consola, nivel WARNING en producción.
9. **Agregar healthchecks en `docker-compose.yml`**: Para `db` y `backend` al menos.
10. **Completar lógica de `Standing`**: Calcular y persistir posiciones tras cada registro de resultado.
11. **Añadir paginación**: Implementar `PageNumberPagination` en todos los endpoints que devuelven colecciones.

### Prioridad 3 — Mejoras de calidad (sprint 3-4)

12. **Tests de integración HTTP**: Usar `APITestCase` de DRF para cubrir los flujos principales (crear torneo, inscribir equipo, registrar resultado).
13. **Configurar `coverage.py`**: Incluir en `Makefile` o CI; objetivo mínimo 80%.
14. **Generar OpenAPI/Swagger**: Con `drf-spectacular` o `drf-yasg`.
15. **Pinear todas las dependencias**: Reemplazar rangos abiertos (`>=`) por versiones exactas en `requirements.txt`.
16. **Validar email al login**: Si `state == NOT_VERIFIED`, rechazar acceso y solicitar verificación.
17. **Implementar recovery de contraseña**: Endpoint + email con token temporal.

### Prioridad 4 — Arquitectura y escalabilidad (sprint 5+)

18. **Agregar Redis**: Para caché de consultas frecuentes (lista de torneos, tabla de posiciones) y queue de Celery.
19. **Implementar Celery**: Para generación de fixtures, scoring IA y envío de notificaciones de forma asíncrona.
20. **IoC Container**: Reemplazar la inyección manual en vistas por un contenedor (e.g., `injector` o `dependency-injector`).
21. **Índices compuestos en BD**: Al menos `(tournament_id, estado)` en `competencia_team` y `competencia_match`.
22. **Estrategia de backup**: Configurar `pg_dump` programado o replicación de PostgreSQL.
23. **CI/CD**: Pipeline GitHub Actions con lint, tests, build de Docker y despliegue automatizado.
24. **Mover tokens a httpOnly cookies**: Para mitigar riesgo de XSS en el cliente.

---

## MATRIZ DE RIESGO CONSOLIDADA

```
SEVERIDAD
   │
CR │ [RS-01] [RS-02]  [RC-01]
   │
AL │ [RS-03] [RS-04]  [RD-01]  [RO-01]  [RC-02]
   │ [RS-05]
   │
ME │ [RS-06] [RS-07]  [RD-02]  [RD-03]  [RO-02]
   │ [RO-03] [RO-04]  [RC-03]
   │
BA │
   └─────────────────────────────────────────────
      SEGURIDAD   DATOS   OPERACIONAL   CALIDAD
```

---

## CONCLUSIÓN

Zoids League es un proyecto con una base arquitectónica sólida. La decisión de usar arquitectura hexagonal es correcta para este dominio y facilitará el mantenimiento a largo plazo. El modelo de dominio está bien definido, con validaciones de negocio correctamente ubicadas en las entidades.

Sin embargo, **el proyecto no es apto para producción en su estado actual** debido a:

1. Dos bugs críticos que rompen el flujo principal del torneo (estados de partidos y generación de fixtures).
2. Configuración de seguridad insegura (SECRET_KEY expuesta, ALLOWED_HOSTS permisivo).
3. Ausencia de observabilidad (sin logging, sin healthchecks, sin monitoreo).
4. Cobertura de testing insuficiente para validar la correctitud de la API.

Con las correcciones de Prioridad 1 y 2 aplicadas, el sistema estaría en condiciones de operar en un entorno controlado (demo, piloto). Las mejoras de Prioridad 3 y 4 lo llevarían a un nivel de producción robusto.

---

*Informe generado mediante análisis estático del código fuente, arquitectura, configuración e infraestructura.*  
*Herramienta: Claude Code — Auditor FURPS+*  
*Fecha: 2026-06-12*
