# Inventario Funcional del Sistema — Zoids League
**Auditor:** Analista Funcional (Claude Sonnet 4.6)  
**Fecha:** 2026-06-19  
**Método:** Análisis estático del código fuente (Backend Django + Frontend React/TypeScript)

---

## Resumen ejecutivo

| Métrica | Valor |
|---------|-------|
| Módulos funcionales | 6 |
| Pantallas (rutas frontend) | 21 |
| Formularios | 10 |
| Endpoints API expuestos | 44 |
| Endpoints API consumidos (frontend) | 38 |
| Roles de usuario | 4 |
| Procesos de negocio principales | 7 |
| Flujos con IA | 5 |

---

## 1. Módulos funcionales

### 1.1 Autenticación y Gestión de Usuarios

Gestiona el ciclo de vida de la sesión: registro, login, renovación de token y perfil. Implementa JWT con access token (15 min) y refresh token (7 días). Control de acceso basado en roles (RBAC) con 4 roles: **admin**, **manager**, **coach**, **participant**.

Incluye protecciones: bloqueo de cuenta tras 5 intentos fallidos, bloqueo mínimo de 15 minutos, validaciones de contraseña (mínimo 8 caracteres), restricción de edad (3–80 años).

### 1.2 Gestión de Torneos (Competencia)

Módulo central del sistema. Maneja el ciclo de vida completo de un torneo desde su creación hasta la finalización. Implementa una máquina de estados formal con las siguientes transiciones válidas:

```
DRAFT → IN_REVIEW → REGISTRATION_OPEN → REGISTRATION_CLOSED → IN_PROGRESS → FINALIZED
                                                                            → CANCELLED
DRAFT ← IN_REVIEW  (vuelta a borrador)
```

Gestiona torneos por categoría (explorador, innovador, constructor), formato (KNOCKOUT, ROUND_ROBIN, HYBRID), y configuración detallada de reglas operativas y criterios de evaluación.

### 1.3 Gestión de Equipos

Subdominio de Competencia. Maneja el registro de equipos por parte de participantes/coaches, y la aprobación/rechazo por parte de administradores/managers. Cada equipo incluye: nombre, categoría, nivel técnico, institución educativa, docente asesor y lista de participantes con datos personales y autorización de datos.

### 1.4 Simulación y Análisis

Permite a los participantes practicar antes del torneo real. Cubre dos flujos:
- **Predicción ML**: XGBoost evalúa métricas de telemetría del robot (velocidad, errores, colisiones, complejidad de código).
- **Análisis de entregables**: Evaluación de código fuente y diseño de componentes mediante reglas NLP.

### 1.5 Inteligencia Artificial / Asistente de Configuración

Asiste a administradores en la configuración de torneos mediante procesamiento de lenguaje natural (reglas NLP, sin LLM real). Genera automáticamente: análisis de torneo, recomendación de dificultad, recomendación de formato, reglas operativas, criterios de evaluación con pesos porcentuales normalizados a 100%.

### 1.6 Analítica y Reportes

Módulo en estado parcial. El endpoint `/api/analitica/` es un placeholder. La UI de Reportes y Calendario usa datos mockeados. El módulo de posiciones (standings) sí está funcional vía endpoint público del torneo.

---

## 2. Menús y navegación

### 2.1 Menú principal — Sidebar (autenticado)

Organizado por rol. El sidebar se adapta al rol del usuario logueado:

| Ítem de menú | Ruta | Roles con acceso |
|---|---|---|
| Dashboard | `/dashboard` | Todos |
| Torneos | `/dashboard/torneos` | Todos |
| Mis Torneos | `/dashboard/mis-torneos` | PARTICIPANT, COACH |
| Simulaciones | `/dashboard/simulaciones` | PARTICIPANT |
| Inteligencia Artificial | `/dashboard/ia` | ADMIN, MANAGER |
| Calendario | `/dashboard/calendario` | Todos |
| Resultados | `/dashboard/resultados` | Todos |
| Instituciones | `/dashboard/instituciones` | ADMIN |
| Reportes | `/dashboard/reportes` | ADMIN, MANAGER |
| Soporte | `/dashboard/soporte` | Todos |

### 2.2 Menú público (sin autenticación)

| Ítem | Ruta |
|---|---|
| Inicio / Login | `/` |
| Registro | `/registro` |
| Vista pública de torneo | `/t/:id` |

### 2.3 Navegación contextual — dentro de un torneo

Al estar dentro de un torneo (`/dashboard/torneos/:id/...`), aparecen submenús:

| Submenú | Ruta | Roles |
|---|---|---|
| Panel Admin | `/dashboard/torneos/:id/admin` | ADMIN, MANAGER |
| Reglas y Criterios | `/dashboard/torneos/:id/reglas` | ADMIN, MANAGER |
| Gestión de Equipos | `/dashboard/torneos/:id/equipos` | ADMIN, MANAGER |
| Fixtures / Partidos | `/dashboard/torneos/:id/competencias` | ADMIN, MANAGER |
| Posiciones | `/dashboard/torneos/:id/posiciones` | Todos |
| Inscribir Equipo | `/dashboard/torneos/:id/inscribir-equipo` | PARTICIPANT, COACH |

---

## 3. Formularios

### FORM-01 — Login

**Ruta:** `/`  
**Componente:** `Login.tsx`

| Campo | Tipo | Obligatorio | Validaciones |
|---|---|---|---|
| Email | email input | Sí | Formato email |
| Password | password (toggle visible) | Sí | — |
| Recordarme | checkbox | No | — |

**Comportamiento especial:** Muestra tiempo de bloqueo restante en minutos si la cuenta está bloqueada.

---

### FORM-02 — Registro de usuario

**Ruta:** `/registro`  
**Componente:** `Register.tsx`

| Campo | Tipo | Obligatorio | Validaciones |
|---|---|---|---|
| Nombre completo | text | Sí | — |
| Email | email | Sí | Formato email, único en sistema |
| Contraseña | password (toggle) | Sí | Mínimo 8 caracteres |
| Fecha de nacimiento | date | Sí | Edad 3–80 años |
| Rol | select | Sí | Participant, Coach, Manager |

---

### FORM-03 — Crear Torneo

**Ruta:** `/dashboard/torneos/nuevo`  
**Componente:** `CreateTournament.tsx`

| Sección | Campo | Tipo | Obligatorio |
|---|---|---|---|
| Datos principales | Nombre | text | Sí |
| | Categorías habilitadas | multiselect (explorador, innovador, constructor) | Sí |
| | Máx. equipos | number | Sí |
| | Mín. equipos | number | No |
| | Tipo torneo | select (KNOCKOUT, ROUND_ROBIN, HYBRID) | Sí |
| Cronograma | Fecha inicio | datetime | Sí |
| | Fecha fin | datetime | Sí |
| Descripción | Descripción | textarea | No |
| Asistente IA | Texto libre en español | textarea | No |

**Comportamiento especial:** El campo de texto libre del Asistente IA llama a `POST /ia/analizar` y auto-completa campos del formulario con los resultados.

---

### FORM-04 — Configuración de Reglas del Torneo

**Ruta:** `/dashboard/torneos/:id/reglas`  
**Componente:** `ConfigTournamentRules.tsx`

| Sección | Campo | Tipo | Obligatorio |
|---|---|---|---|
| Reglas operativas | Mín. miembros por equipo | number | No |
| | Máx. miembros por equipo | number | No |
| | Mín. equipos | number | No |
| | Máx. equipos | number | No |
| | Tipo de acceso | select (abierto, cerrado, invitación) | No |
| | Fecha apertura inscripciones | datetime | No |
| | Fecha cierre inscripciones | datetime | No |
| | Instituciones permitidas | tags/lista | No |
| Formato | Tipo de torneo | select | Sí |
| (KNOCKOUT) | Número de rondas | number | — |
| | Partidos por serie | number | — |
| (ROUND_ROBIN) | Puntos por victoria | number | — |
| | Puntos por empate | number | — |
| | Puntos por derrota | number | — |
| (HYBRID) | Combinación KO+RR | — | — |
| Criterios evaluación | Lista dinámica de criterios | tabla editable | Sí |
| | — nombre criterio | text | Sí |
| | — peso (0.0–1.0) | number | Sí |
| | — valor mínimo | number | No |
| | — valor máximo | number | No |

**Comportamiento especial:** Botón "Generar con IA" llama a `POST /ia/generar-criterios` y añade criterios automáticamente.

---

### FORM-05 — Inscripción de Equipo

**Ruta:** `/dashboard/torneos/:id/inscribir-equipo`  
**Componente:** `RegisterTeam.tsx`

| Sección | Campo | Tipo | Obligatorio |
|---|---|---|---|
| Equipo | Nombre del equipo | text | Sí |
| | Categoría | select | Sí |
| | Nivel técnico | select | No |
| Institución | Nombre institución | text | Sí |
| | Tipo (pública/privada) | select | Sí |
| | Ciudad | text | Sí |
| | País | text | Sí |
| Docente asesor | Nombre completo | text | Sí |
| | Email | email | Sí |
| | Teléfono | tel | Sí |
| Participantes (dinámico) | Nombres | text | Sí |
| | Apellidos | text | Sí |
| | Edad | number | Sí |
| | Grado académico | text | Sí |
| | Documento identidad | text | Sí |
| | Rol en equipo | select | Sí |
| | Autorización datos | checkbox | Sí |

**Comportamiento especial:** Lista de participantes dinámica (añadir/eliminar filas). El botón "Añadir participante" genera una nueva fila de campos.

---

### FORM-06 — Arbitraje (Registro de resultado de partido)

**Componente:** `Competitions.tsx` (modal interno)

| Campo | Tipo | Descripción |
|---|---|---|
| Calificaciones (dinámico) | number por criterio | Una puntuación numérica por cada criterio definido en el torneo |

**Comportamiento:** Modal que aparece al hacer clic en "Registrar resultado" sobre un partido activo. Los campos se generan dinámicamente según los criterios de evaluación configurados.

---

### FORM-07 — Recomendaciones IA (criterios)

**Ruta:** `/dashboard/ia`  
**Componente:** `AIRecommendations.tsx`

| Campo | Tipo | Descripción |
|---|---|---|
| Torneo | select | Selecciona el torneo a configurar |
| Nivel de dificultad | select (básico, intermedio, avanzado) | Nivel técnico objetivo |
| Criterios sugeridos | sliders dinámicos | Pesos ajustables (0–100%) por criterio generado por IA |

---

### FORM-08 — Editor de Simulación

**Ruta:** `/dashboard/simulaciones/torneo/:id`  
**Componente:** `SimulationEditor.tsx`

| Campo | Tipo | Descripción |
|---|---|---|
| Entregable | textarea (mín. 100 chars) | Descripción de la solución implementada |

**Comportamiento:** Muestra contador de caracteres. Al enviar, recibe resultados con puntuaciones por criterio en gráfico de barras.

---

### FORM-09 — Soporte / Contacto

**Ruta:** `/dashboard/soporte`  
**Componente:** `Support.tsx`

| Campo | Tipo | Obligatorio |
|---|---|---|
| Asunto | select (tipos de problema) | Sí |
| Mensaje | textarea | Sí |
| Adjuntar captura | checkbox | No |

**Nota:** Formulario no conectado al backend (sin endpoint implementado).

---

### FORM-10 — Registrar Institución (modal)

**Ruta:** `/dashboard/instituciones`  
**Componente:** `Institutions.tsx`

| Campo | Tipo | Obligatorio |
|---|---|---|
| Nombre | text | Sí |
| Tipo (pública/privada) | select | Sí |
| Ciudad | text | Sí |
| Representante | text | No |
| Teléfono | tel | No |
| Email | email | No |

**Nota:** Formulario no conectado al backend (sin endpoint implementado).

---

## 4. Procesos de negocio

### PNeg-01 — Ciclo de vida de un torneo

```
[Administrador/Manager]
        │
        ▼
  1. Crear Torneo (DRAFT)
        │
        ▼
  2. Configurar reglas y criterios
     (opcionalmente con asistencia IA)
        │
        ▼
  3. Enviar a Revisión (IN_REVIEW)
        │
     [Revisión]──────► Volver a DRAFT (si hay correcciones)
        │
        ▼
  4. Abrir Inscripciones (REGISTRATION_OPEN)
        │
  [Participantes inscriben equipos]
  [Manager aprueba/rechaza equipos]
        │
        ▼
  5. Cerrar Inscripciones (REGISTRATION_CLOSED)
        │
        ▼
  6. Generar Fixtures (brackets automáticos)
        │
        ▼
  7. Iniciar Torneo (IN_PROGRESS)
        │
  [Se juegan partidos ronda por ronda]
  [Árbitro registra resultados por criterio]
  [Sistema actualiza posiciones automáticamente]
        │
        ▼
  8. Finalizar (FINALIZED) o Cancelar (CANCELLED)
```

---

### PNeg-02 — Inscripción de equipo

```
[Participante / Coach]
        │
        ▼
  1. Buscar torneo con inscripciones abiertas
        │
        ▼
  2. Completar formulario de inscripción
     (datos equipo + institución + docente + participantes)
        │
        ▼
  3. Enviar solicitud → Estado: PENDIENTE
        │
        ▼
  [Manager/Admin revisa]
     │              │
     ▼              ▼
  APROBADO       RECHAZADO
     │
     ▼
  Equipo habilitado para competir
```

---

### PNeg-03 — Registro y gestión de resultados de partido

```
[Admin / Manager]
        │
        ▼
  1. Seleccionar partido activo en la vista de Fixtures
        │
        ▼
  2. Abrir modal de Arbitraje
        │
        ▼
  3. Ingresar puntuación por cada criterio de evaluación
     (los criterios son los configurados para ese torneo)
        │
        ▼
  4. Confirmar resultados → POST /api/competencia/partido/{id}/resultado/
        │
        ▼
  5. Sistema aplica lógica de avance:
     - Determina ganador del partido
     - Actualiza standings / posiciones
     - Avanza equipos en el bracket (si KNOCKOUT)
     - Acumula puntos (si ROUND_ROBIN)
        │
        ▼
  6. Resultado visible en vista pública del torneo
```

---

### PNeg-04 — Generación de criterios con IA

```
[Admin / Manager]
        │
        ▼
  1. Acceder a configuración del torneo o módulo IA
        │
        ▼
  2. Seleccionar tipo de torneo, nivel técnico, categoría
        │
        ▼
  3. POST /api/ia/generar-criterios
     → Sistema devuelve lista de criterios con pesos sugeridos
       (pesos normalizados internamente a suma = 100%)
        │
        ▼
  4. Revisar y ajustar pesos manualmente
     → PUT /api/ia/criterios/{criterioId}
        │
        ▼
  5. Confirmar criterios
     → POST /api/ia/criterios/{sesionIaId}/confirmar
       (valida suma = 100%, guarda la sesión)
        │
        ▼
  6. Criterios vinculados al torneo para evaluación de partidos
```

---

### PNeg-05 — Flujo de simulación de participante

```
[Participante con equipo APROBADO]
        │
        ▼
  1. Acceder a "Mis Simulaciones"
     → GET /api/competencia/mis-torneos/
        │
        ▼
  2. Seleccionar torneo → Cargar contexto
     → GET /api/simulacion/torneo/{id}/contexto/
        │
        ▼
  3. Consultar retos del torneo
     → GET /api/simulacion/retos/{torneoId}/
        │
        ▼
  4. Analizar código / componentes
     → POST /api/simulacion/analisis/programacion/
     → POST /api/simulacion/analisis/componentes/
        │
        ▼
  5. Escribir entregable (mínimo 100 caracteres)
     → POST /api/simulacion/torneo/{id}/simular/
        │
        ▼
  6. Recibir puntuaciones por criterio (gráfico de barras)
```

---

### PNeg-06 — Registro y autenticación de usuario

```
[Usuario nuevo]
        │
        ▼
  1. Registro → POST /api/auth/register/
     (nombre, email, contraseña, fecha nacimiento, rol)
        │
        ▼
  2. Login → POST /api/auth/login/
     (email, contraseña)
     ← access_token (15 min) + refresh_token (7 días)
        │
        ▼
  3. Acceso al dashboard según rol
        │
  [Token a punto de expirar]
        │
        ▼
  4. Refresh automático → POST /api/auth/refresh/
     (interceptor Axios, transparente para el usuario)
        │
        ▼
  5. Logout → PUT /api/auth/logout/
     (limpia tokens en localStorage)
```

---

### PNeg-07 — Vista pública de torneo (sin login)

```
[Visitante no autenticado]
        │
        ▼
  1. Acceder a /t/:id
        │
        ▼
  2. GET /api/competencia/torneo/{id}/public/
     → Retorna: info del torneo, equipos, partidos, posiciones, ganador
        │
        ▼
  3. Navegar por tabs: Info | Equipos | Partidos | Posiciones
     (solo lectura, sin autenticación requerida)
```

---

## 5. APIs consumidas (Frontend → Backend)

### 5.1 Servicio de Autenticación

| Método | URL | Llamada desde | Propósito |
|---|---|---|---|
| POST | `auth/login/` | `Login.tsx` | Autenticar usuario |
| POST | `auth/register/` | `Register.tsx` | Registrar nuevo usuario |
| POST | `auth/refresh/` | `api.ts` (interceptor) | Renovar access token automáticamente |
| GET | `auth/me/` | `AuthContext.tsx` | Obtener perfil del usuario actual |
| PUT | `auth/logout/` | `AuthContext.tsx` | Cerrar sesión |

### 5.2 Servicio de Torneos

| Método | URL | Llamada desde | Propósito |
|---|---|---|---|
| GET | `competencia/all/` | `TournamentsList.tsx`, `AIRecommendations.tsx` | Listar todos los torneos |
| POST | `competencia/create/` | `CreateTournament.tsx` | Crear nuevo torneo |
| GET | `competencia/torneo/{id}/` | `TournamentAdminPanel.tsx`, `ConfigTournamentRules.tsx`, `RegisterTeam.tsx`, `TournamentTeamsManagement.tsx` | Detalle de un torneo |
| GET | `competencia/torneo/{id}/public/` | `PublicTournament.tsx`, `Competitions.tsx`, `Results.tsx` | Datos públicos (equipos, partidos, posiciones) |
| PUT | `competencia/torneo/{id}/rules/` | `ConfigTournamentRules.tsx` | Guardar reglas y criterios |
| POST | `competencia/torneo/{id}/review/` | `TournamentsList.tsx`, `ConfigTournamentRules.tsx` | Enviar a revisión |
| POST | `competencia/torneo/{id}/draft/` | `TournamentsList.tsx` | Volver a borrador |
| POST | `competencia/torneo/{id}/open-registrations/` | `TournamentsList.tsx`, `TournamentAdminPanel.tsx` | Abrir inscripciones |
| POST | `competencia/torneo/{id}/close-registrations/` | `TournamentsList.tsx`, `TournamentAdminPanel.tsx` | Cerrar inscripciones |
| POST | `competencia/torneo/{id}/start/` | `TournamentsList.tsx`, `TournamentAdminPanel.tsx` | Iniciar torneo |
| POST | `competencia/torneo/{id}/generar-fixtures/` | `Competitions.tsx` | Generar brackets |
| GET | `competencia/torneo/{id}/equipos/` | `TournamentAdminPanel.tsx`, `TournamentTeamsManagement.tsx` | Listar equipos inscritos |
| POST | `competencia/torneo/{id}/inscribir/` | `RegisterTeam.tsx` | Inscribir equipo |
| POST | `competencia/equipo/{id}/aprobar/` | `TournamentAdminPanel.tsx`, `TournamentTeamsManagement.tsx` | Aprobar equipo |
| POST | `competencia/equipo/{id}/rechazar/` | `TournamentAdminPanel.tsx`, `TournamentTeamsManagement.tsx` | Rechazar equipo |
| POST | `competencia/partido/{id}/resultado/` | `Competitions.tsx` | Registrar resultado de partido |
| GET | `competencia/mis-torneos/` | `MyTournaments.tsx`, `MySimulations.tsx` | Torneos del participante |

### 5.3 Servicio de IA

| Método | URL | Llamada desde | Propósito |
|---|---|---|---|
| POST | `ia/analizar` | `CreateTournament.tsx` | Analizar texto libre → autocompletar formulario |
| POST | `ia/generar-criterios` | `ConfigTournamentRules.tsx`, `AIRecommendations.tsx` | Generar criterios de evaluación |
| PUT | `ia/criterios/{id}` | `AIRecommendations.tsx` | Ajustar peso de un criterio |
| POST | `ia/criterios/{sesion}/confirmar` | `AIRecommendations.tsx` | Confirmar criterios finales |

### 5.4 Servicio de Simulación

| Método | URL | Llamada desde | Propósito |
|---|---|---|---|
| GET | `simulacion/torneo/{id}/contexto/` | `SimulationEditor.tsx` | Cargar contexto de simulación |
| POST | `simulacion/torneo/{id}/simular/` | `SimulationEditor.tsx` | Ejecutar simulación con entregable |
| GET | `simulacion/retos/{id}/` | `RetoAnalyzer.tsx` | Obtener retos del torneo |
| POST | `simulacion/analisis/programacion/` | `RetoAnalyzer.tsx` | Analizar código fuente |
| POST | `simulacion/analisis/componentes/` | `RetoAnalyzer.tsx` | Analizar componentes de solución |

---

## 6. APIs expuestas (Backend)

### 6.1 Módulo Autenticación — `/api/auth/`

| Método | Endpoint | Auth | Roles | Descripción |
|---|---|---|---|---|
| POST | `/api/auth/login/` | No | Público | Login → access + refresh token |
| POST | `/api/auth/register/` | No | Público | Crear cuenta de usuario |
| POST | `/api/auth/refresh/` | No | Público | Renovar access token |
| GET | `/api/auth/me/` | Sí | Todos | Perfil del usuario actual |
| PUT | `/api/auth/logout/` | Sí | Todos | Logout (sin invalidación server-side) |

### 6.2 Módulo Competencia — `/api/competencia/`

| Método | Endpoint | Auth | Roles | Descripción |
|---|---|---|---|---|
| GET | `/api/competencia/all/` | Sí | Todos | Listar todos los torneos |
| POST | `/api/competencia/create/` | Sí | ADMIN, MANAGER | Crear torneo |
| GET | `/api/competencia/torneo/{id}/` | No | Público | Detalle del torneo |
| GET | `/api/competencia/torneo/{id}/public/` | No | Público | Datos públicos (equipos, partidos, standings) |
| PUT | `/api/competencia/torneo/{id}/rules/` | Sí | ADMIN, MANAGER | Configurar reglas y criterios |
| POST | `/api/competencia/torneo/{id}/review/` | Sí | ADMIN, MANAGER | Enviar a revisión |
| POST | `/api/competencia/torneo/{id}/draft/` | Sí | ADMIN, MANAGER | Volver a borrador |
| POST | `/api/competencia/torneo/{id}/open-registrations/` | Sí | ADMIN, MANAGER | Abrir inscripciones |
| POST | `/api/competencia/torneo/{id}/close-registrations/` | Sí | ADMIN, MANAGER | Cerrar inscripciones |
| POST | `/api/competencia/torneo/{id}/start/` | Sí | ADMIN, MANAGER | Iniciar torneo |
| POST | `/api/competencia/torneo/{id}/cancel/` | Sí | ADMIN, MANAGER | Cancelar torneo |
| POST | `/api/competencia/torneo/{id}/inscribir/` | Sí | PARTICIPANT, COACH | Inscribir equipo |
| POST | `/api/competencia/torneo/{id}/generar-fixtures/` | Sí | ADMIN, MANAGER | Generar brackets |
| GET | `/api/competencia/torneo/{id}/posiciones/` | Sí | Todos | Posiciones / standings |
| GET | `/api/competencia/torneo/{id}/equipos/` | Sí | ADMIN, MANAGER | Equipos inscritos |
| POST | `/api/competencia/partido/{id}/resultado/` | Sí | ADMIN, MANAGER | Registrar resultado de partido |
| POST | `/api/competencia/equipo/{id}/aprobar/` | Sí | ADMIN, MANAGER | Aprobar equipo |
| POST | `/api/competencia/equipo/{id}/rechazar/` | Sí | ADMIN, MANAGER | Rechazar equipo |
| GET | `/api/competencia/mis-torneos/` | Sí | Todos | Torneos del usuario actual |

### 6.3 Módulo Simulación — `/api/simulacion/`

| Método | Endpoint | Auth | Roles | Descripción |
|---|---|---|---|---|
| POST | `/api/simulacion/predecir/` | Sí | Todos | Predicción ML con métricas de telemetría |
| GET | `/api/simulacion/historial/{participante_id}/` | Sí | Todos | Historial de predicciones |
| GET | `/api/simulacion/retos/{torneo_id}/` | Sí | Todos | Retos del torneo |
| POST | `/api/simulacion/analisis/programacion/` | Sí | Todos | Análisis de código fuente |
| POST | `/api/simulacion/analisis/componentes/` | Sí | Todos | Análisis de diseño/componentes |
| GET | `/api/simulacion/analisis/{part_id}/{torneo_id}/` | Sí | Todos | Listar análisis previos |
| GET | `/api/simulacion/torneo/{id}/contexto/` | Sí | Todos | Contexto de simulación del torneo |
| POST | `/api/simulacion/torneo/{id}/simular/` | Sí | Todos | Ejecutar simulación con entregable |

### 6.4 Módulo IA — `/api/ia/`

| Método | Endpoint | Auth | Roles | Descripción |
|---|---|---|---|---|
| POST | `/api/ia/analizar` | Sí | ADMIN, MANAGER | NLP sobre texto libre del torneo |
| POST | `/api/ia/recomendar-dificultad` | Sí | ADMIN, MANAGER | Recomendar dificultad |
| POST | `/api/ia/recomendar-formato` | Sí | ADMIN, MANAGER | Recomendar formato (KO/RR/Hybrid) |
| POST | `/api/ia/generar-reglas` | Sí | ADMIN, MANAGER | Generar reglas operativas |
| POST | `/api/ia/generar-criterios` | Sí | ADMIN, MANAGER | Generar criterios de evaluación |
| PUT | `/api/ia/criterios/{id}` | Sí | ADMIN, MANAGER | Actualizar peso de criterio |
| POST | `/api/ia/criterios/{sesion}/confirmar` | Sí | ADMIN, MANAGER | Confirmar sesión de criterios |

### 6.5 Módulo Analítica — `/api/analitica/`

| Método | Endpoint | Auth | Roles | Descripción |
|---|---|---|---|---|
| GET | `/api/analitica/` | No | Público | Placeholder — sin lógica implementada |

---

## 7. Flujos principales

### Flujo 1 — Creación y configuración de torneo (Admin/Manager)

```
Login → Dashboard → Torneos → "Nuevo Torneo"
  → FORM-03: nombre, categorías, fechas, formato
  → [Opcional] Pegar descripción en Asistente IA → autocompletado
  → Guardar → Torneo en estado DRAFT
  → Ir a "Reglas" del torneo
  → FORM-04: reglas operativas, formato, criterios
  → [Opcional] "Generar con IA" → criterios sugeridos automáticamente
  → Ajustar pesos → Guardar
  → "Enviar a Revisión" → estado IN_REVIEW
  → "Abrir Inscripciones" → estado REGISTRATION_OPEN
```

### Flujo 2 — Inscripción de equipo (Participante)

```
Login → Torneos → Seleccionar torneo con inscripciones abiertas
  → "Inscribir Equipo"
  → FORM-05: datos equipo, institución, docente, participantes
  → Enviar → Equipo en estado PENDIENTE
  → Esperar aprobación del manager
  [Notificación implícita — sin sistema de notificaciones en tiempo real]
```

### Flujo 3 — Gestión de equipos y apertura del torneo (Admin/Manager)

```
Panel Admin del Torneo → Tab "Equipos"
  → Ver equipos PENDIENTES
  → Revisar datos → Aprobar o Rechazar
  → Una vez suficientes equipos aprobados:
  → "Cerrar Inscripciones" → estado REGISTRATION_CLOSED
  → "Generar Fixtures" → sistema crea brackets automáticamente
  → "Iniciar Torneo" → estado IN_PROGRESS
```

### Flujo 4 — Arbitraje de partido (Admin/Manager)

```
Panel del torneo → "Fixtures / Competencias"
  → Ver bracket actual → Seleccionar partido activo
  → "Registrar Resultado"
  → FORM-06: puntuación por criterio (dinámico según criterios del torneo)
  → Confirmar → Sistema determina ganador → Actualiza posiciones
  → Bracket avanza automáticamente (si KNOCKOUT)
```

### Flujo 5 — Simulación de práctica (Participante)

```
Login → "Simulaciones" → Seleccionar torneo activo
  → Cargar contexto del torneo
  → [Opcional] Ver retos del torneo
  → [Opcional] Analizar código o componentes
  → Escribir entregable (mínimo 100 caracteres)
  → "Ejecutar Simulación"
  → Ver puntuaciones por criterio en gráfico de barras
```

### Flujo 6 — Vista pública (sin login)

```
URL directa /t/{id} → Sin login requerido
  → Ver info del torneo: nombre, categoría, fechas, descripción
  → Tab Equipos: lista de equipos participantes
  → Tab Partidos: resultados de partidos jugados
  → Tab Posiciones: tabla de standings actualizada
```

### Flujo 7 — Generación de criterios con IA (Admin/Manager)

```
Crear torneo → Configurar reglas → "Generar con IA"
  ó
Dashboard → Módulo "IA" → AIRecommendations
  → Seleccionar torneo
  → Seleccionar nivel de dificultad
  → "Generar criterios"
  → Sistema aplica plantillas por (tipo_torneo, nivel_tecnico)
  → Ajustar pesos con sliders (suma debe = 100%)
  → "Confirmar criterios"
  → Criterios guardados y vinculados al torneo
```

---

## 8. Matriz de funcionalidad por rol

| Funcionalidad | ADMIN | MANAGER | COACH | PARTICIPANT |
|---|:---:|:---:|:---:|:---:|
| Ver todos los torneos | ✓ | ✓ | ✓ | ✓ |
| Ver torneo público (sin login) | ✓ | ✓ | ✓ | ✓ |
| Crear torneo | ✓ | ✓ | — | — |
| Configurar reglas / criterios | ✓ | ✓ | — | — |
| Cambiar estado del torneo | ✓ | ✓ | — | — |
| Gestionar equipos (aprobar/rechazar) | ✓ | ✓ | — | — |
| Generar fixtures | ✓ | ✓ | — | — |
| Registrar resultado de partido | ✓ | ✓ | — | — |
| Usar módulo IA | ✓ | ✓ | — | — |
| Ver reportes | ✓ | ✓ | — | — |
| Gestionar instituciones | ✓ | — | — | — |
| Inscribir equipo en torneo | — | — | ✓ | ✓ |
| Ver mis torneos | — | — | ✓ | ✓ |
| Acceder a simulaciones | — | — | — | ✓ |
| Ejecutar simulación | — | — | — | ✓ (equipo aprobado) |
| Ver posiciones | ✓ | ✓ | ✓ | ✓ |
| Ver calendario | ✓ | ✓ | ✓ | ✓ |
| Soporte | ✓ | ✓ | ✓ | ✓ |

---

## 9. Pantallas sin funcionalidad completa

Las siguientes pantallas tienen UI construida pero sin conexión real al backend:

| Pantalla | Ruta | Estado | Observación |
|---|---|---|---|
| Dashboard Home | `/dashboard` | UI estática | KPIs y gráfico de crecimiento con datos mockeados |
| Calendario | `/dashboard/calendario` | UI estática | Sin eventos reales, sin endpoint |
| Reportes | `/dashboard/reportes` | UI estática | Sin exportación PDF/Excel real, sin datos reales |
| Instituciones | `/dashboard/instituciones` | UI parcial | Formulario construido, sin endpoint POST |
| Soporte | `/dashboard/soporte` | UI estática | Formulario construido, sin endpoint POST |
| Analítica | `/api/analitica/` | Placeholder backend | Endpoint devuelve texto plano sin lógica |

---

*Inventario generado por análisis estático del código fuente. Los flujos describen el comportamiento implementado en el código — no implica que el sistema esté desplegado y funcionando en producción.*
