# Evaluación de Calidad del Sistema — Zoids League
**Auditor:** Arquitecto de Software / Analista de Calidad  
**Fecha:** 2026-06-19  
**Metodología:** Inspección estática de código · Análisis de dependencias · Revisión de logs de ejecución · Trazado de flujos de datos

---

## Resumen ejecutivo

| Dimensión | Calificación | Nivel |
|---|---|---|
| **Cohesión** | 3 / 5 | Aceptable |
| **Acoplamiento** | 3 / 5 | Aceptable |
| **Escalabilidad** | 2 / 5 | Deficiente |
| **Mantenibilidad** | 3 / 5 | Aceptable |
| **Testabilidad** | 3 / 5 | Aceptable |
| **Seguridad** | 2 / 5 | Deficiente |
| **PROMEDIO** | **2.67 / 5** | **Requiere mejora** |

---

## 1. Cohesión — 3 / 5

### Definición aplicada
Grado en que los elementos de un módulo trabajan juntos para un único propósito bien definido. Se evalúa en tres niveles: entidad, caso de uso, y módulo/bounded context.

### Evidencia positiva

**Nivel de entidad — ALTO (4/5)**

Las entidades de dominio exhiben cohesión funcional alta. Cada entidad encapsula exactamente los datos y comportamientos que le corresponden:

```
Tournament (tournament.py)
  ├── add_team()          → gestión de inscripciones
  ├── validate_state_transition() → ciclo de vida
  ├── update_tournament_rules()   → configuración propia
  ├── valid_for_review()          → invariante de negocio
  └── validate_for_start()        → invariante de negocio

User (user.py)
  ├── is_locked() / lock()        → seguridad de cuenta
  ├── increment_attempts()        → antifuerza bruta
  ├── time_to_unlock()            → estado temporal
  └── verify_password_security()  → política de contraseñas
```

Cada entidad tiene una sola razón para cambiar (principio SRP a nivel de clase).

**Nivel de caso de uso — ALTO (4/5)**

Los use cases siguen el patrón Single Responsibility:
- `LoginUseCase` → solo autenticación
- `GenerateFixturesUseCase` → solo generación de bracket/RR/híbrido
- `CalculateStandingsUseCase` → solo cálculo de posiciones
- `RegisterUseCase` → solo registro

**Nivel de Value Object — MUY ALTO (5/5)**

Los VOs son inmutables y cohesivos: `ConfigKnockout`, `ConfigRoundRobin`, `TournamentEvaluation` tienen responsabilidades perfectamente delimitadas.

### Evidencia negativa

**Módulo `competencia` sobredimensionado — BAJO (2/5)**

El bounded context `competencia` concentra responsabilidades de al menos 4 subdominios que deberían separarse:

```
competencia/
  ├── Tournament lifecycle (gestión de estado)
  ├── Fixture generation (algoritmos KNOCKOUT/RR/HYBRID)
  ├── Match qualification (calificación + puntaje + avance de bracket)
  ├── Team inscription (inscripción, aprobación, participantes)
  ├── Standing calculation (clasificaciones)
  ├── Evaluation/Criteria management (rúbricas, pesos)
  └── IA/NLP (análisis de texto, generación de criterios)
        → ubicado en competencia/infrastructure/ia/
        → conceptualmente es un subdomain propio
```

Con 22 casos de uso, ~30 entidades y VOs, y 27 endpoints, `competencia` viola la cohesión a nivel de módulo.

**`QualifyMatchUseCase` — cohesión comunicacional**

Un único use case realiza cinco operaciones distintas:
1. Valida y registra scores por criterio
2. Verifica si todos los criterios están calificados
3. Calcula el ganador ponderado
4. Avanza el bracket (asigna equipo al siguiente partido)
5. Finaliza el torneo si es la final

Esto es cohesión secuencial en el mejor caso; debería descomponerse.

**`analitica` — cohesión nula**

El bounded context `analitica` es un módulo vacío (placeholder con 1 endpoint stub). Tiene carpetas de estructura pero sin implementación real — contribuye a la organización pero no a la funcionalidad.

### Calificación: 3 / 5

> El diseño a nivel micro (entidades, VOs, use cases) es sólido y disciplinado. La pérdida de puntos viene del nivel macro: `competencia` agrupa demasiados subdominios, y la cohesión entre bounded contexts no está suficientemente aislada.

### Recomendaciones de cohesión

| # | Recomendación | Prioridad |
|---|---|---|
| COH-01 | Extraer `MatchQualification` como sub-módulo independiente dentro de `competencia` con su propio set de use cases, separando scoring de avance de bracket | Alta |
| COH-02 | Mover `competencia/infrastructure/ia/` a un bounded context `asistencia_ia` propio con puerto de dominio `CriteriaGeneratorPort` | Media |
| COH-03 | Descomponer `QualifyMatchUseCase` en al menos 3 use cases: `RecordMatchScoresUseCase`, `DetermineMatchWinnerUseCase`, `AdvanceTournamentBracketUseCase` | Alta |
| COH-04 | Implementar o eliminar `analitica` — un placeholder en producción introduce ruido arquitectónico | Baja |

---

## 2. Acoplamiento — 3 / 5

### Definición aplicada
Grado de interdependencia entre módulos. Se evalúa en acoplamiento estructural, de datos, y de despliegue.

### Evidencia positiva

**Ports & Adapters correctamente implementados — ALTO (4/5)**

El patrón hexagonal está genuinamente implementado. El dominio define 15 ABCs (Abstract Base Classes) como puertos de salida:

```python
# authentication/domain/ports/user_repository.py
class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User: ...
    @abstractmethod
    def find_by_email(self, email: str) -> User | None: ...
```

Los use cases reciben repositorios como dependencias:
```python
class LoginUseCase:
    def __init__(self, user_repository: UserRepository, jwt_service: JWTService):
        ...
```

El dominio no importa ningún módulo de Django ORM, psycopg2 ni ningún framework. Verificado en `authentication/domain/` y `competencia/domain/`.

**Frontend desacoplado del backend — ALTO (4/5)**

La SPA React se comunica exclusivamente mediante REST/JSON. Sin importaciones directas del backend. Sin estado compartido fuera del protocolo HTTP.

**DI explícita en las vistas Django**

Las vistas instancian los use cases inyectando las implementaciones concretas:
```python
repo = DjangoUserRepository()
jwt_svc = JWTService()
use_case = LoginUseCase(repo, jwt_svc)
```

Esto centraliza el wiring y lo hace visible.

### Evidencia negativa

**Acoplamiento transversal entre bounded contexts**

El módulo `competencia` importa Value Objects del dominio de `authentication`:

```python
# competencia/... imports from authentication/domain/value_objects/
from authentication.domain.value_objects.system_rol import SystemRol
```

Esto viola la independencia de bounded contexts. Un cambio en la jerarquía de roles de `authentication` puede romper `competencia`.

**`simulacion` accede a modelos ORM de `competencia`**

La implementación del puerto `TournamentContextPort` en `simulacion/infrastructure/` importa directamente los modelos ORM de `competencia`:

```python
# simulacion/infrastructure/db/tournament_context_repo.py
from competencia.infrastructure.db.models import TournamentDjangoModel
```

En lugar de cruzar por una API de dominio o un evento, `simulacion` tiene dependencia directa a la implementación de infraestructura de otro bounded context. Si `competencia` renombra o reestructura sus modelos ORM, `simulacion` falla silenciosamente.

**Startup coupling: importaciones eager que bloquean todo Django**

La cadena de importación en `simulacion/views.py` → `xgboost_adapter.py` → `joblib` y `analisis_engine.py` → `openai` significa que la ausencia de cualquiera de estas librerías impide que **todos los endpoints del sistema** respondan:

```
simulacion/urls.py ──► views.py ──► analisis_engine.py
                                        └── from openai import OpenAI
                                            (ImportError = Django muerto)
```

Esto es acoplamiento de despliegue máximo: un módulo ML opcional bloquea la autenticación.

**`calculate_standings_use_case.py` rompe encapsulación**

```python
# Acceso a atributo privado mediante name mangling
s._Standing__posicion = i + 1
```

Este pattern crea acoplamiento frágil — cualquier renombrado de `__posicion` en `Standing` no es detectado por el typechecker y falla en runtime.

**Schema PostgreSQL compartido**

Todos los módulos escriben en el mismo schema `public` de PostgreSQL. No hay aislamiento a nivel de base de datos. Un `DROP TABLE` o migración fallida en un módulo puede corromper datos de otro.

### Calificación: 3 / 5

> El acoplamiento a nivel de dominio es bueno gracias a los ports bien definidos. El 3 en lugar de 4 refleja violaciones concretas y medibles: imports cross-context, startup coupling que afecta disponibilidad total, y acceso a privados con name mangling.

### Recomendaciones de acoplamiento

| # | Recomendación | Prioridad |
|---|---|---|
| ACO-01 | Definir un `SharedKernel` o módulo de tipos compartidos (como `SystemRol`) en lugar de importar de otro bounded context | Alta |
| ACO-02 | Reemplazar el import directo de modelos ORM de `competencia` en `simulacion` por un Anti-Corruption Layer o un evento de dominio | Alta |
| ACO-03 | Hacer lazy las importaciones de ML/IA en `views.py` (importar dentro de la función o en `ready()` de AppConfig) para que un fallo de ML no bloquee autenticación | Alta |
| ACO-04 | Agregar setter público `Standing.set_posicion(int)` en lugar de acceso via name mangling | Media |
| ACO-05 | Crear schemas PostgreSQL separados por bounded context (`auth`, `competencia`, `simulacion`) para aislamiento a nivel de DB | Baja |

---

## 3. Escalabilidad — 2 / 5

### Definición aplicada
Capacidad del sistema para mantener rendimiento aceptable al aumentar la carga (usuarios concurrentes, volumen de datos, torneos simultáneos).

### Evidencia positiva

**JWT stateless — habilitador de escalabilidad horizontal**

Los tokens JWT son autocontenidos (user_id, email, rol). El backend no necesita session store compartido. Esto es el único habilitador real de escalabilidad horizontal en el diseño actual.

**Contenerización con Docker**

La separación en 3 contenedores Docker permite en teoría escalar cada servicio de forma independiente.

### Evidencia negativa

**Sin pool de conexiones configurado**

Django gestiona conexiones a PostgreSQL sin pool explícito. Con Django `runserver` (single-threaded) el problema no se manifiesta, pero con cualquier servidor WSGI multi-worker (Gunicorn con 4 workers) se abrirían N conexiones simultáneas sin límite. No hay configuración de `CONN_MAX_AGE` ni pgBouncer.

**Sin cache**

Toda request que consulta datos de torneo ejecuta queries SQL completas. Un torneo con 64 equipos consultado simultáneamente por 100 usuarios genera 100 queries idénticas a PostgreSQL. No hay Redis, Memcached, ni cache a nivel de vista Django.

```python
# Ejemplo: cada GET /api/competencia/all/ ejecuta
Tournament.objects.select_related(...).prefetch_related(...).all()
# Sin cache TTL, sin invalidación
```

**Django `runserver` — no apto para carga**

El servidor de desarrollo de Django es single-threaded. Una request lenta (generación de fixtures para 64 equipos con `transaction.atomic()`) bloquea todas las demás. Gunicorn está instalado pero no se usa.

**Sin paginación en endpoints de listado**

```
GET /api/competencia/all/        → retorna TODOS los torneos
GET /api/competencia/mis-torneos/ → retorna TODOS sin límite
```

Con 1000 torneos en base de datos, estas llamadas devuelven payload completo y ejecutan queries sin LIMIT.

**`transaction.atomic()` síncrono en operaciones costosas**

`GenerateFixturesUseCase` ejecuta una transacción que puede crear cientos de registros `Match` en una sola atomic block. Durante esta transacción, la tabla de partidos queda bloqueada.

**Modelo XGBoost cargado en startup — sin lazy loading**

```python
class XGBoostAdapter:
    def __init__(self):
        self.model = joblib.load('xgboost_model.pkl')  # en __init__
```

Cada worker Gunicorn cargaría el modelo .pkl en memoria en el startup. Con 4 workers × modelo de 50MB = 200MB de RAM fija solo para ML.

**PostgreSQL instancia única — single point of failure y bottleneck**

Sin read replicas, sin standby, sin connection pooling externo. Toda la carga de lectura y escritura converge en un único proceso PostgreSQL.

**Sin CDN para assets estáticos**

El frontend sirve assets desde el servidor de aplicación. Sin CDN, los assets se recargan desde el mismo host en cada usuario nuevo.

### Calificación: 2 / 5

> El sistema está diseñado para una única instancia, con recursos compartidos sin pool, sin cache, y con el servidor de desarrollo Django. Soporta la carga de un ambiente de pruebas/demo (< 20 usuarios concurrentes), pero fallaría bajo carga real de un torneo con múltiples jueces calificando simultáneamente.

### Recomendaciones de escalabilidad

| # | Recomendación | Prioridad | Impacto estimado |
|---|---|---|---|
| ESC-01 | Reemplazar `runserver` por `gunicorn --workers 4 --timeout 120` | Crítica | 4× throughput inmediato |
| ESC-02 | Agregar Redis como cache + `CONN_MAX_AGE = 60` en settings | Alta | -80% queries a DB en reads |
| ESC-03 | Implementar paginación cursor-based en todos los endpoints de listado | Alta | Previene OOM con datos reales |
| ESC-04 | Hacer lazy el `XGBoostAdapter` (cargar model solo en primera predicción, compartir con singleton) | Media | -N×50MB de RAM en multi-worker |
| ESC-05 | Agregar pgBouncer o `django-db-geventpool` para connection pooling | Media | Soporta 100+ conexiones simultáneas |
| ESC-06 | Mover generación de fixtures a tarea asíncrona (Celery + Redis) | Media | Libera thread HTTP durante operación larga |
| ESC-07 | Agregar `Cache-Control` headers y CDN (Cloudflare/CloudFront) para assets frontend | Baja | -60% latencia para usuarios geográficamente distribuidos |

---

## 4. Mantenibilidad — 3 / 5

### Definición aplicada
Facilidad para comprender, modificar, extender y corregir el sistema sin introducir regresiones.

### Evidencia positiva

**Arquitectura auto-documentada**

La estructura de carpetas por capas hace explícita la arquitectura. Un desarrollador nuevo puede orientarse:

```
authentication/
  domain/entities/      → reglas de negocio
  application/use_cases/ → flujos de aplicación
  infrastructure/       → detalles técnicos
  interface/            → HTTP layer
```

**Entidades ricas — reglas de negocio localizadas**

Todas las validaciones del dominio están en las entidades, no dispersas en views ni use cases:
```python
# tournament.py — invariante localizada
def add_team(self, team: Team):
    if self.estado != TournamentState.REGISTRATION_OPEN:
        raise ValueError("Cannot add team: tournament not in REGISTRATION_OPEN state")
```

Un cambio en la regla se hace en un solo lugar.

**Factory methods con invariantes**

`Tournament.create()`, `User.create_user()`, `Criteria.__init__()` garantizan que ningún objeto del dominio puede existir en estado inválido. Esto simplifica el mantenimiento preventivo.

**Use cases nombrados semánticamente**

`GenerateFixturesUseCase`, `InscribeTeamUseCase`, `QualifyMatchUseCase` — el nombre es el requerimiento. Un analista puede mapear historias de usuario a código sin intermediarios.

### Evidencia negativa

**15 errores TypeScript en el frontend**

```
TS18048: 'decoded' is possibly 'undefined'  [AuthContext.tsx:36]
TS2339: Property 'X' does not exist on type ... [múltiples]
```

Los errores TypeScript suprimen el valor del sistema de tipos. El compilador pierde confiabilidad como herramienta de mantenimiento — un desarrollador que refactoriza tipos no puede confiar en `tsc` para detectar regresiones.

**Dos use cases para el mismo propósito**

`QualifyMatchUseCase` y `RegisterMatchResultUseCase` parecen realizar tareas solapadas (ambos registran resultados de partidos). Esta ambigüedad obliga a leer ambas implementaciones para entender cuál usar y cuándo.

**Sin documentación de API (OpenAPI/Swagger)**

44 endpoints sin contrato documentado. Para saber qué recibe `POST /api/competencia/torneo/{id}/inscribir/` hay que leer el view + el serializer + el use case + la entidad. No hay swagger-ui ni redoc generado.

**Configuración con fallbacks inseguros en código**

```python
# settings.py
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-v50ee...')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
```

Cuando `.env` no existe (nuevo desarrollador, CI sin secrets), el sistema arranca en modo inseguro silenciosamente. Debería `raise ImproperlyConfigured()`.

**`competencia` difícil de navegar por tamaño**

22 use cases, ~30 entidades y VOs, 27 endpoints. Sin subdirectorios por subdomain dentro del módulo, la búsqueda de un archivo específico requiere conocer la convención de nombres exacta.

**Ruta del modelo ML hardcodeada**

```python
joblib.load('xgboost_model.pkl')  # ruta relativa al CWD
```

Si el directorio de trabajo cambia (CI/CD, Docker con diferente WORKDIR), el sistema falla en runtime con `FileNotFoundError` en lugar de error de configuración claro.

**passlib 1.7.4 — librería abandonada**

El proyecto usa una librería de seguridad sin mantenimiento activo desde 2021. Mantener código dependiente de librerías abandonadas aumenta el costo de futuras auditorías de seguridad.

### Calificación: 3 / 5

> La arquitectura facilita la mantenibilidad a largo plazo (hexagonal, use cases, factory methods), pero el estado actual del proyecto tiene deuda técnica específica que dificulta el trabajo cotidiano: errores TypeScript que inhabilitan el compilador como guardia, falta de documentación de API, y módulo `competencia` sobredimensionado.

### Recomendaciones de mantenibilidad

| # | Recomendación | Prioridad |
|---|---|---|
| MAN-01 | Corregir los 15 errores TypeScript y activar `strict: true` en tsconfig para que el compilador sea confiable | Alta |
| MAN-02 | Agregar `drf-spectacular` para generar OpenAPI 3.0 automáticamente desde el código DRF | Alta |
| MAN-03 | Reemplazar fallbacks de `SECRET_KEY` y `DEBUG` por `raise ImproperlyConfigured(...)` cuando la variable no está definida | Alta |
| MAN-04 | Reorganizar `competencia/` en sub-packages: `tournament/`, `fixtures/`, `qualification/`, `inscription/` | Media |
| MAN-05 | Resolver ambigüedad entre `QualifyMatchUseCase` y `RegisterMatchResultUseCase` — unificar o documentar explícitamente cuándo usar cada uno | Media |
| MAN-06 | Configurar la ruta del modelo ML via variable de entorno: `ML_MODEL_PATH = os.environ.get('XGBOOST_MODEL_PATH', ...)` | Media |
| MAN-07 | Reemplazar `passlib` por `bcrypt` directamente (ya está instalado y en uso) | Baja |
| MAN-08 | Eliminar `coverage` de `requirements.txt` de producción (mover a `requirements-dev.txt`) | Baja |

---

## 5. Testabilidad — 3 / 5

### Definición aplicada
Facilidad para escribir, ejecutar y mantener pruebas automatizadas que verifiquen el comportamiento correcto del sistema.

### Evidencia positiva

**Arquitectura hexagonal — máxima testabilidad del dominio**

Las entidades de dominio son clases Python puras sin dependencias de framework:

```python
# test unitario posible sin Django, sin DB, sin Mock complejo:
def test_tournament_add_team_fails_when_not_open():
    tournament = Tournament.create(...)
    team = Team(...)
    # estado != REGISTRATION_OPEN
    with pytest.raises(ValueError):
        tournament.add_team(team)
```

Los puertos (ABCs) permiten crear mocks simples para use cases:

```python
class FakeUserRepository(UserRepository):
    def find_by_email(self, email): return test_user
    def update(self, user): self.updated = user

def test_login_increments_attempts_on_wrong_password():
    repo = FakeUserRepository()
    use_case = LoginUseCase(repo, FakeJWTService())
    use_case.execute("test@test.com", "wrong_password")
    assert repo.updated.intentos_fallidos == 1
```

**DI explícita en todas las capas de aplicación**

Ningún use case usa `import` de implementaciones concretas. Todo viene por constructor. Esto es condición necesaria para unit testing sin efectos secundarios.

**64 archivos de test encontrados en el proyecto**

Los tests existen y están estructurados siguiendo la misma arquitectura de capas.

**Factory methods facilitan la construcción de fixtures de test**

`User.create_user(email, hashed_pass, rol)` y `Tournament.create(...)` encapsulan la creación válida, evitando que los tests construyan objetos inválidos.

### Evidencia negativa

**Tests no ejecutables sin PostgreSQL**

Los tests de integración requieren una instancia PostgreSQL activa. En el entorno de auditoría (sin Docker disponible) fue imposible ejecutar la suite. En un pipeline CI estándar sin servicios configurados, fallarían igualmente.

Los tests de Django que usan `TestCase` de Django crean y destruyen una BD de test, pero requieren que el driver `psycopg2` pueda conectarse.

**Sin CI/CD — los tests nunca se ejecutan automáticamente**

No hay `.github/workflows/`, `.gitlab-ci.yml`, ni ningún pipeline configurado. La suite de 64 tests existe pero su ejecución es manual y opcional. En la práctica, nadie sabe si pasan o fallan en el estado actual del código.

**Cobertura desconocida**

`coverage` está en `requirements.txt` pero no hay reporte de cobertura generado, objetivo de cobertura definido, ni evidencia de que se haya ejecutado.

**Frontend sin tests**

No hay configuración de `vitest`, `jest`, ni `@testing-library/react` en el frontend. Las 21 páginas y 10 formularios no tienen pruebas automatizadas de ningún tipo.

**`transaction.atomic()` importado directamente en use cases**

```python
# competencia/application/use_cases/generate_fixtures_use_case.py
from django.db import transaction

class GenerateFixturesUseCase:
    def execute(self, tournament_id):
        with transaction.atomic():
            ...
```

Esto acopla el use case a Django. Para testear `GenerateFixturesUseCase` sin Django hay que mockear `django.db.transaction`, lo que rompe el principio de que los use cases son Python puro.

**`QualifyMatchUseCase` mezcla I/O con lógica**

La lógica de calcular el ganador, avanzar el bracket y potencialmente finalizar el torneo está entrelazada con persistencia (llamadas a repositorios) dentro del mismo método. Para testear solo el algoritmo de cálculo de ganador hay que mockear 4 repositorios distintos.

### Calificación: 3 / 5

> La arquitectura hexagonal brinda la base correcta para tests unitarios del dominio. Pero en la práctica: no hay CI, el frontend tiene cero tests, los tests de integración requieren infra externa no orquestada, y el acoplamiento de `transaction.atomic()` en use cases complica el aislamiento. El potencial es 4/5; el estado actual entrega 3/5.

### Recomendaciones de testabilidad

| # | Recomendación | Prioridad |
|---|---|---|
| TST-01 | Crear GitHub Actions workflow mínimo: instalar deps → `python -m pytest` con `--tb=short` | Crítica |
| TST-02 | Usar `pytest-django` con `@pytest.mark.django_db` + fixture de PostgreSQL en contenedor (GitHub Actions `services:`) | Alta |
| TST-03 | Extraer la lógica de avance de bracket de `QualifyMatchUseCase` a un `BracketService` puro (sin I/O) testeable en aislamiento | Alta |
| TST-04 | Reemplazar `transaction.atomic()` directo en use cases por un `UnitOfWork` port inyectable (patrón ya definido pero no implementado en el dominio) | Media |
| TST-05 | Agregar Vitest + Testing Library al frontend; comenzar con los 3 flujos críticos: Login, inscripción de equipo, calificación de partido | Alta |
| TST-06 | Definir objetivo de cobertura mínima (sugerido 70% domain layer, 50% application layer) y reportar en CI | Media |
| TST-07 | Crear `tests/factories/` con funciones `create_tournament()`, `create_team()`, etc. para simplificar setup de tests de integración | Media |

---

## 6. Seguridad — 2 / 5

### Definición aplicada
Capacidad del sistema para proteger datos y operaciones contra acceso no autorizado, manipulación y vulnerabilidades conocidas. Se evalúa en confidencialidad, integridad, disponibilidad y gestión de vulnerabilidades.

### Evidencia positiva

**Hashing de contraseñas con bcrypt correctamente implementado**

```python
# password_service.py
def encrypt(self, password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify(self, plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

bcrypt con salt generado aleatoriamente por cada contraseña. Resistente a ataques de rainbow table.

**Mecanismo de bloqueo de cuenta funcional**

```python
# user.py
MAX_ATTEMPTS = 5
MIN_LOCK_TIME = 15  # minutos

def is_locked(self) -> bool:
    if not self.bloqueado: return False
    if datetime.now() > self.tiempo_bloqueo + timedelta(minutes=MIN_LOCK_TIME):
        self.__bloqueado = False  # auto-desbloqueo
        return False
    return True
```

Protección funcional contra ataques de fuerza bruta a nivel de dominio.

**RBAC implementado con verificación en cada endpoint**

El decorador `@auth_required(roles=[...])` verifica:
1. Presencia del token Bearer
2. Validez criptográfica del JWT (HS256)
3. No expiración
4. Rol del usuario en la lista de roles permitidos

**Validación del consentimiento de datos en dominio**

```python
# participant.py
if not autorizacion_datos:
    raise ValueError("Se requiere autorización de datos para registrar participante")
```

Cumplimiento de principio de consentimiento explícito aplicado en la capa de dominio.

**Política de contraseñas en dominio**

```python
MIN_PASSWORD_LENGTH = 8
# verify_password_security() también verifica: mayúsculas, números, caracteres especiales
```

### Evidencia negativa

**[CRÍTICO] SECRET_KEY con fallback hardcodeado en código fuente**

```python
# config/settings.py
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-v50ee$v908kp8p)$_dx87tw39y##gb)=bwg872q@txgf=4no2g'
)
```

Si `.env` no existe o la variable no está definida, Django usa esta clave pública. Consecuencia directa: **cualquier atacante puede forjar tokens JWT válidos para cualquier usuario con cualquier rol**. La clave es pública porque está versionada en git. Este hallazgo invalida toda la seguridad de autenticación.

**[CRÍTICO] Credenciales de base de datos hardcodeadas en docker-compose.yml**

```yaml
db:
  environment:
    POSTGRES_PASSWORD: admin   # versionado en git
    POSTGRES_USER: admin
```

Si el puerto 5432 es accesible (en desarrollo o por error de configuración de firewall), cualquier persona con acceso al repositorio conoce las credenciales de la base de datos.

**[CRÍTICO] CVEs activos en dependencias de producción**

*Frontend — axios ≤1.7.8 (4 CVEs HIGH):*
- `CVE-2024-39338` — SSRF: permite al atacante hacer requests a URLs internas desde el servidor
- `CVE-2023-45857` — Credential Leakage vía header `X-XSRF-TOKEN`  
- `CVE-2024-28849` — Header Injection en redirects
- `CVE-2024-48932` — Prototype Pollution

*Frontend — react-router 7.0–7.15 (1 CVE CRÍTICO):*
- `GHSA-cpj5-3fhq-fgh6` — RCE potencial via TYPE_ERROR deserialization

**[ALTO] Tokens JWT no revocables**

```
PUT /api/auth/logout/ 
→ Solo actualiza last_login en DB
→ No hay blacklist de tokens
→ Token sigue siendo válido hasta expiración natural (15 min / 7 días)
```

Después de logout, robo de sesión, o cambio de contraseña, el token anterior sigue funcionando. En el caso del refresh token: 7 días de ventana de ataque.

**[ALTO] Django `runserver` expone información de debug**

`runserver` muestra stack traces en HTML con variables de entorno y estado interno cuando `DEBUG=True`. Los fallbacks de settings.py hacen que `DEBUG` sea `True` por defecto.

**[ALTO] Sin rate limiting en endpoints de autenticación**

Aunque existe el bloqueo por cuenta (`MAX_ATTEMPTS=5`), no hay limitación a nivel de red. Un atacante puede intentar 5 contraseñas por cuenta con miles de cuentas diferentes sin ninguna limitación de velocidad.

**[ALTO] Sin configuración SSL/TLS**

Las comunicaciones entre browser↔frontend, frontend↔backend, y backend↔PostgreSQL son todas en texto claro en la configuración actual. Los JWT y contraseñas viajan sin cifrado en tránsito.

**[MEDIO] Django check --deploy: 6 advertencias de seguridad**

```
WARN SecurityMiddleware: SECURE_SSL_REDIRECT is not set to True
WARN SessionMiddleware: SESSION_COOKIE_SECURE is not True
WARN SessionMiddleware: SESSION_COOKIE_HTTPONLY is not True
WARN CsrfViewMiddleware: CSRF_COOKIE_SECURE is not set to True
WARN X-Content-Type: X_CONTENT_TYPE_OPTIONS_NOSNIFF not configured
WARN X-Frame-Options: X_FRAME_OPTIONS not configured
```

El propio verificador de Django identifica estas configuraciones como inseguras para producción.

**[MEDIO] JWT almacenado en localStorage**

```javascript
// AuthContext.tsx
localStorage.setItem('access_token', token)
```

`localStorage` es accesible por JavaScript. Si hay XSS (incluida la cadena de dependencias npm), los tokens pueden ser exfiltrados. La alternativa segura es `HttpOnly cookies`.

### Calificación: 2 / 5

> El diseño de seguridad a nivel de dominio es correcto (bcrypt, lockout, RBAC). Sin embargo, tres vulnerabilidades críticas lo invalidan para cualquier entorno accesible: SECRET_KEY pública que permite forjar cualquier JWT, credenciales DB en git, y CVEs activos en dependencias de frontend incluyendo un RCE potencial. Para un sistema académico en red local puede ser aceptable; para cualquier exposición pública es inaceptable.

### Recomendaciones de seguridad

| # | Recomendación | Severidad | Esfuerzo |
|---|---|---|---|
| SEC-01 | Eliminar el fallback de `SECRET_KEY` — `raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set")` | Crítica | 30 min |
| SEC-02 | Eliminar credenciales hardcodeadas de docker-compose.yml — usar `${DB_PASSWORD}` y requerir `.env` | Crítica | 1 hora |
| SEC-03 | Actualizar `axios` a ≥1.8.2 y `react-router` a ≥7.16.0 | Crítica | 1 hora |
| SEC-04 | Implementar token blacklist para logout (Redis Set con TTL = tiempo de expiración del token) | Alta | 1 día |
| SEC-05 | Configurar Gunicorn + Nginx con SSL termination; habilitar `SECURE_SSL_REDIRECT=True` | Alta | 1 día |
| SEC-06 | Agregar `django-ratelimit` a endpoints `/auth/login/` y `/auth/register/` (ej: 5 req/min por IP) | Alta | 4 horas |
| SEC-07 | Migrar tokens JWT de `localStorage` a `HttpOnly Secure SameSite=Strict cookies` | Alta | 2 días |
| SEC-08 | Configurar `SECURE_HSTS_SECONDS`, `X_FRAME_OPTIONS`, `SECURE_CONTENT_TYPE_NOSNIFF` en settings.py | Media | 2 horas |
| SEC-09 | Ejecutar `npm audit fix` en CI y bloquear el build si hay CVEs HIGH sin fix disponible | Media | 4 horas |
| SEC-10 | Separar `requirements.txt` en `base.txt` + `prod.txt` y remover herramientas de dev del contenedor de producción | Baja | 2 horas |

---

## Cuadro de síntesis final

```
COHESIÓN          ████████████░░░░░░░░  3/5  Módulo competencia sobredimensionado
                                              Entidades y use cases excelentes

ACOPLAMIENTO      ████████████░░░░░░░░  3/5  Ports & Adapters bien implementados
                                              Cross-context imports y startup coupling

ESCALABILIDAD     ████████░░░░░░░░░░░░  2/5  JWT stateless es la única fortaleza
                                              Sin cache, sin pool, sin paginación

MANTENIBILIDAD    ████████████░░░░░░░░  3/5  Arquitectura auto-documentada, buena
                                              15 errores TS, sin OpenAPI, sin CI

TESTABILIDAD      ████████████░░░░░░░░  3/5  Hexagonal permite unit tests puros
                                              Sin CI, sin tests frontend, sin cobertura

SEGURIDAD         ████████░░░░░░░░░░░░  2/5  bcrypt, RBAC, lockout correctos
                                              SECRET_KEY pública, CVEs activos, no SSL

─────────────────────────────────────────────────────────────
PROMEDIO          ██████████░░░░░░░░░░  2.67/5

Nivel actual: Prototipo / Demo — NO apto para producción pública
Nivel objetivo: Sistema productivo hardened (4/5 en todas las dimensiones)
```

### Prioridad de remediación

```
SEMANA 1 — Críticos (evitan acceso a producción)
  ├── SEC-01: Eliminar SECRET_KEY hardcodeada
  ├── SEC-02: Eliminar credenciales DB de docker-compose
  ├── SEC-03: Actualizar axios + react-router
  ├── ACO-03: Lazy import de ML/IA en views.py
  └── ESC-01: Reemplazar runserver por gunicorn

SEMANA 2 — Altos (afectan operación real)
  ├── TST-01: Pipeline CI mínimo con pytest
  ├── MAN-01: Corregir errores TypeScript + strict mode
  ├── SEC-05: SSL/TLS + configuración HTTPS
  ├── SEC-06: Rate limiting en endpoints de autenticación
  └── ESC-03: Paginación en todos los endpoints de listado

SEMANA 3-4 — Medios (mejoran calidad estructural)
  ├── COH-03: Descomponer QualifyMatchUseCase
  ├── ACO-01: SharedKernel para tipos compartidos
  ├── MAN-02: OpenAPI/Swagger con drf-spectacular
  ├── TST-05: Tests de frontend con Vitest
  └── ESC-02: Redis cache
```

---

*Evaluación realizada mediante análisis estático completo del código fuente, dependencias (requirements.txt + package.json), configuración (settings.py, docker-compose.yml, .env.template), logs de ejecución real, y síntesis de las 8 auditorías previas del proyecto.*
