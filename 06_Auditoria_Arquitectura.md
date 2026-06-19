# Auditoría de Arquitectura de Software — Zoids League
**Auditor:** Arquitecto de Software Senior (Claude Sonnet 4.6)  
**Fecha:** 2026-06-19  
**Rama auditada:** `Auditoria-Furps`  
**Método:** Análisis estático de código fuente, estructura de módulos y grafo de dependencias

---

## Metodología

El análisis se basó en lectura directa de código fuente, no en nombres de carpetas. Se verificaron:

- Contratos entre capas (interfaces, clases abstractas)
- Flujo de dependencias (quién importa a quién)
- Comportamiento de las entidades de dominio
- Acoplamiento entre módulos
- Presencia o ausencia de comunicación asíncrona/eventos

---

## 1. Arquitectura Hexagonal (Ports & Adapters)

### Veredicto: CONFIRMADA — Confianza ALTA

### Evidencia directa del código

**Puerto de salida (Output Port):** `authentication/domain/ports/user_repository.py`
```python
class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User: ...
    @abstractmethod
    def get_by_email(self, email: str) -> User: ...
```
El dominio define un contrato abstracto. No sabe nada de PostgreSQL.

**Adaptador de salida (Output Adapter):** `authentication/infrastructure/repositories/postgresql_repository/user_repository_postgresql.py`
```python
class UserRepositoryPostgresql(UserRepository):   # implementa el puerto
    def _to_domain(self, model: UserModel) -> User: ...   # mapper ORM → dominio
    def _to_model(self, user: User) -> UserModel: ...     # mapper dominio → ORM
```
La implementación concreta vive en infraestructura. El dominio nunca importa Django ORM.

**Adaptador de entrada (Input Adapter):** `authentication/infrastructure/adapters/input/api/views.py`
```python
@api_view(['POST'])
def login(request):
    login_use_case = LoginUseCase(user_repository, password_service, jwt_service)
    response = login_use_case.execute(**request.data)
```
La vista HTTP es el adaptador de entrada. Traduce HTTP → caso de uso → HTTP response.

**Puerto de aplicación (Unit of Work):** `competencia/application/ports/competencia_unit_of_work.py`
```python
class CompetenciaUnitOfWork(ABC):
    @property
    @abstractmethod
    def tournaments(self): ...
    @abstractmethod
    async def commit(self): ...
```
Define operaciones transaccionales como contrato abstracto en la capa de aplicación.

### Carpetas involucradas

```
authentication/
├── domain/ports/                       ← Puertos de dominio (contratos)
├── application/use_cases/              ← Casos de uso (orquestación)
├── infrastructure/adapters/input/api/  ← Adaptador entrada (HTTP)
├── infrastructure/adapters/output/     ← Modelo ORM (separado del dominio)
└── infrastructure/repositories/        ← Adaptador salida (PostgreSQL)

competencia/ simulacion/ analitica/     ← Mismo patrón replicado en 3 módulos más
```

### Grafo de dependencias confirmado

```
[HTTP Request]
      ↓
infrastructure/adapters/input/api/views.py    (Adaptador de entrada)
      ↓ instancia e invoca
application/use_cases/*.py                    (Casos de uso — núcleo)
      ↓ depende de interfaces abstractas
domain/ports/*.py                             (Puertos — contratos)
      ↑ implementado por
infrastructure/repositories/*.py              (Adaptador de salida — PostgreSQL)
```

**Regla de dependencia respetada:** Las capas internas NO importan las capas externas. Verificado en `create_tournament_use_case.py` — solo importa de `domain.*`, nunca de `infrastructure.*`.

### Justificación técnica

La separación entre `UserModel` (Django ORM, en infraestructura) y `User` (entidad de dominio, pura Python) con mappers explícitos `_to_domain()` / `_to_model()` es la implementación canónica del patrón Ports & Adapters. El dominio es completamente testeable sin base de datos.

---

## 2. Clean Architecture

### Veredicto: CONFIRMADA — Confianza ALTA (coexiste con Hexagonal)

### Evidencia directa del código

**Entidad de dominio rica:** `authentication/domain/entities/user.py`
```python
class User:
    __MAX_ATTEMPTS = 5
    __MIN_LOCK_TIME = 15

    def is_locked(self) -> bool: ...
    def increment_attempts(self) -> None:
        self.__attempts += 1
        if self.__attempts >= self.__MAX_ATTEMPTS:
            self.lock(self.__MIN_LOCK_TIME)     # regla de negocio pura
    def verify_password_security(password: str) -> bool:
        # validación de contraseña con reglas explícitas
```

Las reglas de negocio viven **dentro** de la entidad, no en servicios externos ni en vistas.

**Entidad de dominio con máquina de estados:** `competencia/domain/entities/tournament.py`
```python
def validate_state_transition(self, new_state: TournamentState) -> bool:
    valid_transitions = {
        TournamentState.DRAFT: {TournamentState.IN_REVIEW},
        TournamentState.IN_REVIEW: {TournamentState.DRAFT, TournamentState.REGISTRATION_OPEN},
        ...
    }
    allowed = valid_transitions.get(self.__state, set())
    if new_state not in allowed:
        raise ValueError(f"Transición inválida: {self.__state} → {new_state}")
```

La máquina de estados del torneo es una regla de negocio, no lógica de framework.

**Caso de uso como interactor:** `competencia/application/use_cases/create_tournament_use_case.py`
```python
class CreateTournamentUseCase:
    def __init__(self, user: User, tournament_repository: TournamentRepository):
        # recibe dependencias inyectadas
    def execute(self, name, description, date_start, date_end, category, max_teams):
        self._validate_user()
        tournament = Tournament.create(...)
        self.__tournament_repository.save(tournament)
```

Los casos de uso son interactores: coordinan entidades y repositorios sin conocer HTTP ni SQL.

### Anillos de Clean Architecture detectados

```
┌─────────────────────────────────────────────┐
│  FRAMEWORKS & DRIVERS (outer ring)          │
│  Django, DRF, PostgreSQL, Docker            │
├─────────────────────────────────────────────┤
│  INTERFACE ADAPTERS                         │
│  views.py, models.py (ORM), serializers.py  │
├─────────────────────────────────────────────┤
│  APPLICATION BUSINESS RULES                 │
│  use_cases/, services/, ports/ (UoW)        │
├─────────────────────────────────────────────┤
│  ENTERPRISE BUSINESS RULES (inner ring)     │
│  entities/, value_objects/, ports/          │
└─────────────────────────────────────────────┘
```

**Regla de dependencia de Uncle Bob:** Las importaciones siempre apuntan hacia adentro. Verificado en el grafo de imports del proyecto.

### Carpetas involucradas

```
*/domain/entities/          ← Anillo interior (Enterprise Rules)
*/domain/value_objects/     ← Anillo interior
*/domain/ports/             ← Frontera de anillo interior
*/application/use_cases/    ← Anillo Application Rules
*/application/services/     ← Anillo Application Rules
*/infrastructure/           ← Anillo exterior (Frameworks & Drivers)
config/settings.py          ← Framework configuration (outer ring)
```

### Justificación técnica

Clean Architecture y Hexagonal Architecture son complementarias — la primera define los anillos y la dirección de dependencias, la segunda define los mecanismos de conexión (puertos/adaptadores). Este proyecto implementa ambas como un conjunto coherente, que es la práctica más común en DDD moderno.

---

## 3. Domain-Driven Design (DDD)

### Veredicto: CONFIRMADA — Confianza ALTA

> DDD no es una arquitectura de capas, sino un conjunto de patrones tácticos y estratégicos. Se detecta como un patrón transversal que da forma al diseño de las otras arquitecturas.

### Evidencia directa del código

**Aggregate Root:** `competencia/domain/entities/tournament.py`
```python
class Tournament:
    def add_team(self, team: Team):           # controlado por el aggregate root
        self.__tournament_rule.validate_team_rules(team)
        # valida duplicados de DNI en todos los equipos del torneo
        tournament_team = TournamentTeam(...)
        self.__tournament_teams.append(tournament_team)

    def get_teams_accepted(self) -> list[TournamentTeam]:
        return [t for t in self.__tournament_teams if t.state == TournamentTeamState.ACCEPTED]
```
`Tournament` es el Aggregate Root que protege sus invariantes. Nadie puede agregar un equipo sin pasar por `add_team()`.

**Value Objects:** `competencia/domain/value_objects/enums/`, `config_tournament/`
```python
class ConfigKnockout(ConfigTournament):
class ConfigRoundRobin(ConfigTournament):
class ConfigHybrid(ConfigTournament):
class TournamentEvaluation:
```
Los tipos de configuración son Value Objects inmutables que encapsulan reglas de cada formato.

**Factory Method en entidades:**
```python
# User.create_user() — User.py
# Tournament.create() — tournament.py
```
Las entidades controlan su propia creación con validaciones de negocio.

**Repository como contrato de dominio:**
```python
class TournamentRepository(ABC):
    def find_by_id(self, id: str) -> Tournament | None: ...
    def find_my_tournaments(self, user_id: str) -> list[Tournament]: ...
    def recover_tournament_rules(self, tournament_id: int) -> TournamentRule | None: ...
```
El repositorio habla el idioma del dominio, no de la base de datos.

**Lenguaje ubicuo (Ubiquitous Language):** El código usa terminología del dominio de torneos educativos: `TournamentState.REGISTRATION_OPEN`, `TournamentTeamState.DISQUALIFIED`, `TournamentRol.MANAGER`, `docente_asesor`, `inscripcion`.

**Unit of Work Pattern:**
```python
class CompetenciaUnitOfWork(ABC):
    async def commit(self): ...
    async def rollback(self): ...
    async def __aenter__(self): ...
```

### Bounded Contexts detectados

| Bounded Context | Módulo | Responsabilidad |
|-----------------|--------|-----------------|
| Identity & Access | `authentication/` | Usuarios, roles, sesiones |
| Competition Management | `competencia/` | Torneos, equipos, partidas, criterios |
| Simulation & Prediction | `simulacion/` | Predicciones XGBoost, análisis de entregas |
| Analytics & NLP | `analitica/` | Análisis NLP de torneos |

**Coupling entre contextos:** Se detecta acoplamiento directo — `competencia` importa de `authentication.domain`:
```python
# create_tournament_use_case.py
from authentication.domain.value_objects.enum.system_rol import SystemRol
```
Esto es una violación del principio de Bounded Contexts aislados (deberían comunicarse vía contratos, no imports directos).

---

## 4. Arquitectura por Capas (Layered Architecture)

### Veredicto: PARCIALMENTE — Confianza MEDIA

### Evidencia

La estructura de 3 capas existe como consecuencia de Hexagonal + Clean Architecture:

```
Capa         | Carpeta              | Regla de dependencia
-------------|----------------------|---------------------
Presentación | infrastructure/      | Puede importar Application
Aplicación   | application/         | Puede importar Domain
Dominio      | domain/              | No importa nada externo
```

Sin embargo, **no es Layered Architecture clásica** por las siguientes razones:

- En Layered Architecture clásica, cada capa puede importar la capa inmediatamente inferior.
- Aquí, `infrastructure` NO importa `application` directamente — lo instancia desde afuera (inyección de dependencias).
- La inversión de dependencias (DIP) la distingue de la arquitectura en capas pura.

### Justificación técnica

La arquitectura por capas clásica (Presentation → Business → Data Access) produce acoplamiento hacia abajo. Este proyecto invierte esa dependencia en la frontera dominio-infraestructura mediante puertos abstractos, lo que la convierte en Hexagonal, no en Layered clásica. Las capas son un efecto secundario, no el patrón principal.

---

## 5. Modular Monolith

### Veredicto: PARCIAL — Confianza MEDIA-BAJA

### Evidencia a favor

- 4 módulos Django con su propia capa `domain/`, `application/`, `infrastructure/`
- Cada módulo tiene sus propias migraciones, modelos ORM y casos de uso
- Un solo proceso Django, una sola base de datos
- Estructura que facilita extraer módulos en el futuro

### Evidencia en contra

```python
# competencia/application/use_cases/create_tournament_use_case.py
from authentication.domain.value_objects.enum.system_rol import SystemRol
from authentication.domain.value_objects.enum.user_state import UserState
```

Los módulos **no son autónomos**: `competencia` importa directamente del dominio de `authentication`. Un Modular Monolith verdadero requiere que los módulos se comuniquen solo vía API pública (eventos, contratos publicados), no mediante imports directos entre dominios.

### Justificación técnica

El proyecto tiene la **forma** de un Modular Monolith pero no respeta el **contrato**: el aislamiento entre contextos acotados. Es más preciso describirlo como un monolito hexagonal con módulos Django que como un Modular Monolith canónico.

---

## 6. MVC (Model-View-Controller)

### Veredicto: NO predominante — Confianza BAJA

### Evidencia

Django es técnicamente un framework MTV (Model-Template-View), que es una variante de MVC:

- **Model:** Django ORM (`*/infrastructure/adapters/output/models.py`)
- **View (Controller en Django):** funciones en `views.py` anotadas con `@api_view`
- **Template:** No existe — la API devuelve JSON, sin templates HTML

Sin embargo, el proyecto deliberadamente **evita** el patrón MVC:

```python
# views.py NO contiene lógica de negocio
def login(request):
    login_use_case = LoginUseCase(...)   # delega inmediatamente al caso de uso
    response = login_use_case.execute(**request.data)
```

Las vistas son thin controllers — traducen HTTP pero no contienen business logic. El "Model" de Django (`UserModel`) existe pero es un artefacto de infraestructura separado del modelo de dominio (`User`).

### Justificación técnica

MVC es la arquitectura del framework (Django), no del sistema. El equipo de desarrollo eligió explícitamente no usarlo como patrón arquitectónico, reemplazándolo con Hexagonal + Clean Architecture.

---

## 7. Microservicios

### Veredicto: NO ENCONTRADO — Confianza MUY ALTA (ausencia)

### Evidencia de ausencia

| Característica de Microservicios | Estado en el proyecto |
|----------------------------------|----------------------|
| Procesos independientes por servicio | NO — único proceso Django |
| Base de datos por servicio | NO — PostgreSQL compartida |
| Comunicación via red (HTTP/gRPC) entre servicios | NO — imports Python directos |
| Message broker (Kafka, RabbitMQ) | NO — no detectado en requirements.txt ni código |
| Container orquestado por servicio | NO — docker-compose con 3 contenedores (db, backend, frontend), no uno por bounded context |
| API Gateway | NO |
| Service Discovery | NO |
| Circuit Breaker / Resilience patterns | NO |

---

## 8. Event-Driven Architecture (EDA)

### Veredicto: NO ENCONTRADO — Confianza ALTA (ausencia)

### Evidencia de ausencia

Búsqueda exhaustiva de patrones EDA en todo el codebase Python:

- `EventBus`, `MessageBus`, `publish`, `subscribe`: **no encontrado**
- Django `signals`: **no encontrado en código de aplicación** (solo en migraciones como artefacto de Django)
- Celery, Redis Queue, RabbitMQ, Kafka: **no en requirements.txt ni docker-compose.yml**
- WebSocket / Django Channels: **`config/asgi.py` presente pero sin configurar channels**
- Comunicación asíncrona entre módulos: **no encontrada**

Toda comunicación es **sincrónica request-response** a través de llamadas directas a casos de uso.

---

## 9. Frontend — Arquitectura detectada

El frontend React no fue parte del análisis de patrones del enunciado, pero se incluye por completitud.

### Patrón: Feature-Sliced Architecture (informal)

```
src/
├── features/          ← Organización por dominio de negocio
│   ├── auth/
│   ├── tournaments/
│   ├── simulation/
│   └── ...
├── components/        ← Componentes de UI compartidos
├── context/           ← Estado global (React Context API)
├── services/          ← Capa de acceso a API REST
├── hooks/             ← Lógica reutilizable
└── types/             ← Contratos TypeScript
```

**Patrón de estado:** React Context API para autenticación global (`AuthContext.tsx`). No hay Redux ni Zustand.

**Separación de capas:**
- `services/*.ts` → acceso a HTTP (Axios) — equivalente a adaptadores de salida
- `context/` → estado global — equivalente a un Application Service
- `features/` → componentes de UI — equivalente a presentación

---

## 10. Tabla resumen de arquitecturas

| Arquitectura | Encontrada | Carpetas involucradas | Confianza | Justificación |
|-------------|------------|----------------------|-----------|---------------|
| **Hexagonal (Ports & Adapters)** | ✅ SÍ | `*/domain/ports/`, `*/infrastructure/adapters/`, `*/infrastructure/repositories/` | **Alta** | ABCs como puertos, implementaciones concretas en infra, mappers explícitos `_to_domain()`/`_to_model()` |
| **Clean Architecture** | ✅ SÍ | `*/domain/entities/`, `*/application/use_cases/`, `*/infrastructure/` | **Alta** | Anillos concéntricos, regla de dependencia unidireccional, entidades con reglas de negocio puras |
| **DDD (patrones tácticos)** | ✅ SÍ | `*/domain/entities/`, `*/domain/value_objects/`, `*/domain/ports/` | **Alta** | Aggregate Roots, Value Objects, Factory Methods, Repositories como contratos de dominio, UoW |
| **Arquitectura por Capas** | ⚠️ PARCIAL | `domain/`, `application/`, `infrastructure/` | **Media** | Existe como consecuencia de Hexagonal, pero con inversión de dependencias — no es Layered clásica |
| **Modular Monolith** | ⚠️ PARCIAL | `authentication/`, `competencia/`, `simulacion/`, `analitica/` | **Media-Baja** | Tiene la forma (módulos con capas propias) pero no el contrato (cross-module imports directos violan el aislamiento) |
| **MVC** | ⚠️ RESIDUAL | `*/infrastructure/adapters/input/api/views.py`, `*/infrastructure/adapters/output/models.py` | **Baja** | Herencia del framework Django/DRF, activamente evitado en el diseño — vistas son thin controllers |
| **Microservicios** | ❌ NO | — | **N/A** | Proceso único, base de datos compartida, comunicación por imports Python directos |
| **Event-Driven Architecture** | ❌ NO | — | **N/A** | Sin message broker, sin Django signals en dominio, sin comunicación asíncrona |

---

## 11. Conclusión final

### Arquitectura predominante: **Hexagonal Architecture + Clean Architecture + DDD**

Este proyecto implementa deliberada y consistentemente la tríada **Hexagonal + Clean Architecture + DDD**. Los tres patrones son complementarios y el equipo los aplicó de forma integrada:

```
┌──────────────────────────────────────────────────────────────┐
│  CLEAN ARCHITECTURE define los anillos y la regla de         │
│  dependencia unidireccional (inner → outer jamás).           │
│                                                              │
│  HEXAGONAL ARCHITECTURE define los mecanismos de conexión:   │
│  puertos (interfaces abstractas) y adaptadores               │
│  (implementaciones concretas) en el anillo exterior.         │
│                                                              │
│  DDD define el lenguaje y los patrones tácticos del          │
│  núcleo: Aggregate Roots, Value Objects, Repositories,       │
│  Use Cases como Application Services.                        │
└──────────────────────────────────────────────────────────────┘
```

### Lo que el proyecto hace bien

1. **Separación dominio / infraestructura** perfectamente implementada — `User` y `UserModel` son clases diferentes con mappers explícitos.
2. **Reglas de negocio en entidades**, no en vistas ni servicios anémicos — `User.is_locked()`, `Tournament.validate_state_transition()`, `Tournament.add_team()`.
3. **Inversión de dependencias** correctamente aplicada — los casos de uso dependen de interfaces, no de implementaciones.
4. **Testabilidad** alta en el dominio — se puede probar sin base de datos, sin Django, sin HTTP.

### Deuda arquitectónica detectada

| Deuda | Severidad | Descripción |
|-------|-----------|-------------|
| Cross-module coupling | Media | `competencia` importa `authentication.domain` directamente — viola el aislamiento de Bounded Contexts |
| `CompetenciaUnitOfWork` async sin implementación | Media | Definido como ABC async pero no implementado — posible código muerto |
| `analitica` como módulo vacío | Baja | Sus modelos y casos de uso están dispersos en `competencia` — el bounded context no tiene forma propia |
| Ausencia de Anti-Corruption Layer | Baja | La integración con OpenRouter/OpenAI no tiene ACL — cambiar de proveedor LLM requeriría modificar código de infraestructura |
| Vistas Django con instanciación manual de dependencias | Baja | `user_repository = UserRepositoryPostgresql()` en el módulo — sin inyección de dependencias automática (DI container) |

### Recomendación arquitectónica

El núcleo del sistema está bien diseñado. Las mejoras prioritarias son:

1. **Eliminar imports directos entre bounded contexts** — crear contratos compartidos (`shared_kernel`) o comunicar vía DTOs a través de la capa de aplicación.
2. **Implementar DI container** (ej. `dependency-injector`) para reemplazar la instanciación manual en vistas.
3. **Formalizar el Anti-Corruption Layer** para la integración con OpenRouter — ya existe el puerto `nlp_analyzer_port.py` pero no está completamente cableado.

---

*Auditoría generada mediante análisis estático de código. Todos los fragmentos citados corresponden a archivos leídos directamente del repositorio.*
