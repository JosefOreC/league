# documentacion_competencia — Arquitectura, Endpoints y Persistencia

El módulo de **competencia** contiene las reglas y flujos de negocio fundamentales para administrar los torneos, inscribir equipos y sus participantes, definir rúbricas y criterios, generar el fixture de partidos de forma automática (Round-Robin, Knockout, Híbrido), y registrar los resultados de las llaves competitivas.

---

## 1. Índice de Endpoints (`/api/competencia/` e `/api/ia/`)

### Gestión de Torneos e Inscripciones (`/api/competencia/`)

| Método | Ruta | Rol Requerido | Descripción |
|--------|------|---------------|-------------|
| `GET`  | `all/` | Cualquiera autenticado | Lista todos los torneos |
| `POST` | `create/` | `ADMIN`, `MANAGER` | Crea un torneo básico en borrador |
| `GET`  | `torneo/<str:tournament_id>/` | Público | Detalle de un torneo |
| `GET`  | `torneo/<str:tournament_id>/public/` | Público | Datos consolidados públicos (Fixture, Tabla de Posiciones, Equipos) |
| `PUT`  | `torneo/<str:tournament_id>/rules/` | `ADMIN`, `MANAGER` | Configura reglas de límite de miembros, formato de torneo y criterios |
| `POST` | `torneo/<str:tournament_id>/review/` | `ADMIN`, `MANAGER` | Cambia estado del torneo a listo para revisión (`READY`) |
| `POST` | `torneo/<str:tournament_id>/draft/` | `ADMIN`, `MANAGER` | Devuelve el torneo a estado borrador (`DRAFT`) |
| `POST` | `torneo/<str:tournament_id>/open-registrations/` | `ADMIN`, `MANAGER` | Abre inscripciones de equipos (`REGISTRATION_OPEN`) |
| `POST` | `torneo/<str:tournament_id>/close-registrations/` | `ADMIN`, `MANAGER` | Cierra inscripciones de equipos (`REGISTRATION_CLOSED`) |
| `POST` | `torneo/<str:tournament_id>/start/` | `ADMIN`, `MANAGER` | Inicia la fase activa de partidos del torneo (`LIVE`) |
| `POST` | `torneo/<str:tournament_id>/cancel/` | `ADMIN`, `MANAGER` | Cancela el torneo (`CANCELLED`) |
| `POST` | `torneo/<str:tournament_id>/inscribir/` | `PARTICIPANT`, `COACH` | Realiza el registro completo de un equipo y sus integrantes |
| `POST` | `torneo/<str:tournament_id>/generar-fixtures/` | `ADMIN`, `MANAGER` | Genera y distribuye las llaves o rondas de partidos |
| `POST` | `partido/<str:match_id>/resultado/` | `ADMIN`, `MANAGER` | Registra puntajes obtenidos en el partido y actualiza llaves |
| `GET`  | `torneo/<str:tournament_id>/posiciones/` | Público | Obtiene la tabla general de posiciones de la competencia |
| `GET`  | `torneo/<str:tournament_id>/equipos/` | `ADMIN`, `MANAGER` | Obtiene la lista de equipos registrados para validación del organizador |
| `POST` | `equipo/<str:team_id>/aprobar/` | `ADMIN`, `MANAGER` | Cambia estado de inscripción del equipo a `APROBADO` |
| `POST` | `equipo/<str:team_id>/rechazar/` | `ADMIN`, `MANAGER` | Cambia estado de inscripción del equipo a `RECHAZADO` |
| `GET`  | `mis-torneos/` | Cualquiera autenticado | Lista los torneos donde el usuario participa como representante |

### Endpoints de Asistencia IA (`/api/ia/` / `/api/competencia/ia/`)

| Método | Ruta | Rol Requerido | Descripción |
|--------|------|---------------|-------------|
| `POST` | `analizar` | `ADMIN`, `MANAGER` | Extrae intenciones y parámetros del torneo vía NLP |
| `POST` | `recomendar-dificultad` | `ADMIN`, `MANAGER` | Recomienda nivel sugerido (Básico, Intermedio, Avanzado) |
| `POST` | `recomendar-formato` | `ADMIN`, `MANAGER` | Recomienda Knockout, Round Robin o Híbrido basado en equipos |
| `POST` | `generar-reglas` | `ADMIN`, `MANAGER` | Recomienda reglas operativas (peso, tamaño, tiempo) |
| `POST` | `generar-criterios` | `ADMIN`, `MANAGER` | Sugiere de 3 a 10 criterios de evaluación con rúbricas |
| `PUT`  | `criterios/<str:criterio_id>` | `ADMIN`, `MANAGER` | Edita el peso porcentual del criterio sugerido |
| `POST` | `criterios/<str:sesion_ia_id>/confirmar` | `ADMIN`, `MANAGER` | Aplica formalmente los criterios generados al torneo |

---

## 2. Detalle de Endpoints Destacados

### 2.1. `PUT /api/competencia/torneo/<tournament_id>/rules/`
Establece las reglas y estructura de la competencia.

**Headers:**
`Content-Type: application/json`  
`Authorization: Bearer <access_token>`

**Body:**
```json
{
  "tournament_rule": {
    "min_members": 3,
    "max_members": 6,
    "min_teams": 4,
    "max_teams": 16,
    "access_type": "ABIERTO",
    "validation_list": ["INSCRIPCION_COMPLETA"],
    "date_start_inscription": "2026-05-01T00:00:00",
    "date_end_inscription": "2026-05-25T23:59:59"
  },
  "tournament_config": {
    "formato": "round_robin",
    "config": {
      "num_rounds": 1,
      "point_to_victory": 3,
      "point_to_draw": 1,
      "point_to_defeat": 0
    }
  },
  "tournament_evaluation": [
    {
      "name": "Diseño Mecánico",
      "description": "Estructura física del robot",
      "value": 50.0,
      "min_value_qualification": 0.0,
      "max_value_qualification": 10.0
    }
  ]
}
```

---

### 2.2. `POST /api/competencia/torneo/<tournament_id>/inscribir/`
Registra un equipo, su docente asesor y los participantes en un solo paso.

**Headers:**
`Content-Type: application/json`  
`Authorization: Bearer <access_token>`

**Body:**
```json
{
  "team": {
    "name": "RoboMasters",
    "category": "PRIMARY",
    "institution_id": "inst-uuid-111",
    "nivel_tecnico_declarado": "INTERMEDIO",
    "docente_asesor": {
      "id": "doc-uuid-222",
      "nombre_completo": "Profesor Gómez",
      "email": "gomez@colegio.edu.pe",
      "telefono": "987654321",
      "institution_id": "inst-uuid-111"
    }
  },
  "participants": [
    {
      "nombres": "Carlos",
      "apellidos": "Sánchez",
      "edad": 15,
      "grado_academico": "3ro de secundaria",
      "rol_en_equipo": "Programador",
      "documento_identidad": "77665544",
      "autorizacion_datos": true
    }
  ]
}
```

---

## 3. Esquema de Base de Datos y Modelos INSERT

El módulo persistente consta de las siguientes tablas relacionales en la base de datos de PostgreSQL:

### 3.1. DDL SQL (Tablas Principales)

```sql
-- Reglas de Inscripción y Configuración General
CREATE TABLE IF NOT EXISTS competencia_tournament_rule (
    id                     VARCHAR(36) PRIMARY KEY,
    min_members            INTEGER NOT NULL,
    max_members            INTEGER NOT NULL,
    min_teams              INTEGER NOT NULL,
    max_teams              INTEGER NOT NULL,
    access_type            VARCHAR(20) NOT NULL,
    validation_list        JSONB NOT NULL DEFAULT '[]',
    created_at             TIMESTAMP NOT NULL,
    updated_at             TIMESTAMP NOT NULL,
    date_start_inscription TIMESTAMP NULL,
    date_end_inscription   TIMESTAMP NULL
);

-- Torneos
CREATE TABLE IF NOT EXISTS competencia_tournament (
    id                 VARCHAR(36) PRIMARY KEY,
    name               VARCHAR(255) NOT NULL,
    description        TEXT NOT NULL,
    date_start         TIMESTAMP NOT NULL,
    date_end           TIMESTAMP NOT NULL,
    state              VARCHAR(30) NOT NULL,
    category           VARCHAR(30) NOT NULL,
    creator_user_id    VARCHAR(36) NOT NULL,
    tournament_rule_id VARCHAR(36) NOT NULL UNIQUE REFERENCES competencia_tournament_rule(id) ON DELETE CASCADE,
    config_tournament  JSONB NOT NULL DEFAULT '{}'
);

-- Criterios de Evaluación
CREATE TABLE IF NOT EXISTS competencia_criteria (
    id                      VARCHAR(36) PRIMARY KEY,
    name                    VARCHAR(255) NOT NULL,
    description             TEXT NOT NULL,
    value                   DOUBLE PRECISION NOT NULL,
    min_value_qualification DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    max_value_qualification DOUBLE PRECISION NOT NULL DEFAULT 10.0,
    created_at              TIMESTAMP NOT NULL,
    updated_at              TIMESTAMP NOT NULL,
    tournament_id           VARCHAR(36) NULL REFERENCES competencia_tournament(id) ON DELETE CASCADE
);

-- Instituciones Educativas
CREATE TABLE IF NOT EXISTS competencia_institution (
    id      VARCHAR(36) PRIMARY KEY,
    name    VARCHAR(300) NOT NULL,
    type    VARCHAR(50) NOT NULL,
    city    VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL
);

-- Docente Asesor
CREATE TABLE IF NOT EXISTS competencia_docente_asesor (
    id             VARCHAR(36) PRIMARY KEY,
    nombre_completo VARCHAR(200) NOT NULL,
    email          VARCHAR(254) UNIQUE NOT NULL,
    telefono       VARCHAR(20) NOT NULL,
    institution_id VARCHAR(36) NOT NULL REFERENCES competencia_institution(id) ON DELETE CASCADE
);

-- Equipos
CREATE TABLE IF NOT EXISTS competencia_team (
    id                      VARCHAR(36) PRIMARY KEY,
    name                    VARCHAR(150) NOT NULL,
    category                VARCHAR(50) NOT NULL,
    nivel_tecnico_declarado VARCHAR(50) NOT NULL,
    estado_inscripcion      VARCHAR(50) NOT NULL,
    fecha_inscripcion       TIMESTAMP NOT NULL,
    representante_id        VARCHAR(36) NOT NULL,
    docente_asesor_id       VARCHAR(36) NOT NULL REFERENCES competencia_docente_asesor(id) ON DELETE CASCADE,
    tournament_id           VARCHAR(36) NOT NULL REFERENCES competencia_tournament(id) ON DELETE CASCADE,
    institution_id          VARCHAR(36) NOT NULL REFERENCES competencia_institution(id) ON DELETE CASCADE
);

-- Participantes
CREATE TABLE IF NOT EXISTS competencia_participant (
    id                  VARCHAR(36) PRIMARY KEY,
    nombres             VARCHAR(150) NOT NULL,
    apellidos           VARCHAR(150) NOT NULL,
    edad                INTEGER NOT NULL,
    grado_academico     VARCHAR(50) NOT NULL,
    rol_en_equipo       VARCHAR(100) NULL,
    documento_identidad VARCHAR(50) NOT NULL,
    autorizacion_datos  BOOLEAN NOT NULL,
    team_id             VARCHAR(36) NOT NULL REFERENCES competencia_team(id) ON DELETE CASCADE
);

-- Partidos
CREATE TABLE IF NOT EXISTS competencia_match (
    id                    VARCHAR(36) PRIMARY KEY,
    ronda                 INTEGER NOT NULL,
    posicion_en_ronda     INTEGER NOT NULL,
    es_bye                BOOLEAN NOT NULL DEFAULT FALSE,
    es_descanso           BOOLEAN NOT NULL DEFAULT FALSE,
    fase                  VARCHAR(50) NULL,
    estado                VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    ganador_id            VARCHAR(36) NULL,
    fecha_programada      TIMESTAMP NULL,
    equipo_local_id       VARCHAR(36) NULL REFERENCES competencia_team(id) ON DELETE SET NULL,
    equipo_visitante_id   VARCHAR(36) NULL REFERENCES competencia_team(id) ON DELETE SET NULL,
    partido_siguiente_id  VARCHAR(36) NULL REFERENCES competencia_match(id) ON DELETE SET NULL,
    tournament_id         VARCHAR(36) NOT NULL REFERENCES competencia_tournament(id) ON DELETE CASCADE
);

-- Resultados de Partidos
CREATE TABLE IF NOT EXISTS competencia_match_result (
    id                VARCHAR(36) PRIMARY KEY,
    valor_registrado  NUMERIC(10, 4) NOT NULL,
    valor_normalizado NUMERIC(10, 4) NOT NULL,
    estado_resultado  VARCHAR(50) NOT NULL,
    registrado_por    VARCHAR(36) NOT NULL,
    created_at        TIMESTAMP NOT NULL,
    updated_at        TIMESTAMP NOT NULL,
    criterio_id       VARCHAR(36) NOT NULL REFERENCES competencia_criteria(id) ON DELETE CASCADE,
    equipo_id         VARCHAR(36) NOT NULL REFERENCES competencia_team(id) ON DELETE CASCADE,
    match_id          VARCHAR(36) NOT NULL REFERENCES competencia_match(id) ON DELETE CASCADE
);
```

---

### 3.2. Script INSERT SQL de Ejemplo

```sql
-- 1. Reglas
INSERT INTO competencia_tournament_rule (id, min_members, max_members, min_teams, max_teams, access_type, created_at, updated_at)
VALUES ('rule-1', 3, 6, 4, 16, 'ABIERTO', NOW(), NOW());

-- 2. Torneo
INSERT INTO competencia_tournament (id, name, description, date_start, date_end, state, category, creator_user_id, tournament_rule_id)
VALUES ('torneo-1', 'Liga de Robótica 2026', 'Competencia nacional', NOW() + INTERVAL '10 day', NOW() + INTERVAL '15 day', 'DRAFT', 'constructor', 'admin-id', 'rule-1');

-- 3. Criterio
INSERT INTO competencia_criteria (id, name, description, value, created_at, updated_at, tournament_id)
VALUES ('criterio-1', 'Precisión de recorrido', 'Seguimiento exacto de línea', 100.0, NOW(), NOW(), 'torneo-1');

-- 4. Institución
INSERT INTO competencia_institution (id, name, type, city, country)
VALUES ('inst-1', 'I.E. Mercedes Cabello', 'PUBLICA', 'Lima', 'PE');

-- 5. Docente Asesor
INSERT INTO competencia_docente_asesor (id, nombre_completo, email, telefono, institution_id)
VALUES ('docente-1', 'Carlos Meléndez', 'carlos.melendez@mercedes.edu.pe', '998877665', 'inst-1');

-- 6. Equipo
INSERT INTO competencia_team (id, name, category, nivel_tecnico_declarado, estado_inscripcion, fecha_inscripcion, representante_id, docente_asesor_id, tournament_id, institution_id)
VALUES ('team-1', 'CyberMercedes', 'SECONDARY', 'INTERMEDIO', 'APROBADO', NOW(), 'representante-id', 'docente-1', 'torneo-1', 'inst-1');

-- 7. Participante
INSERT INTO competencia_participant (id, nombres, apellidos, edad, grado_academico, rol_en_equipo, documento_identidad, autorizacion_datos, team_id)
VALUES ('part-1', 'Sofía', 'López', 16, '4to de secundaria', 'Líder Hardware', '66554433', TRUE, 'team-1');
```

---

*Última actualización: PMV2 — competencia*
