# documentacion_authentication — Arquitectura, Endpoints y Persistencia

El módulo de **authentication** gestiona el registro de usuarios, el inicio de sesión seguro, la renovación de credenciales mediante refresh tokens y la validación de identidad con roles integrados a nivel del sistema (`admin`, `manager`, `coach`, `participant`).

---

## 1. Índice de Endpoints (`/api/auth/`)

| Método | Ruta | Rol Requerido | Descripción |
|--------|------|---------------|-------------|
| `POST` | `/api/auth/login/` | Público | Autentica a un usuario y genera tokens (Access + Refresh) |
| `POST` | `/api/auth/register/` | Público | Registra a un nuevo usuario en el sistema |
| `GET`  | `/api/auth/me/` | Cualquiera autenticado | Retorna el perfil y los datos del token del usuario activo |
| `PUT`  | `/api/auth/logout/` | Cualquiera autenticado | Invalida/Cierra sesión activa |
| `POST` | `/api/auth/refresh/` | Público | Renueva el `access_token` a partir de un `refresh_token` válido |

---

## 2. Detalle de Endpoints Destacados

### 2.1. `POST /api/auth/login/`
Permite a un usuario iniciar sesión en la plataforma.

**Headers:**
`Content-Type: application/json`

**Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña123"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "usuario@ejemplo.com",
    "name": "Juan Pérez",
    "rol": "participant",
    "state": "active"
  }
}
```

---

### 2.2. `POST /api/auth/register/`
Registra un nuevo usuario participante.

**Headers:**
`Content-Type: application/json`

**Body:**
```json
{
  "email": "nuevo@ejemplo.com",
  "password": "contraseña123",
  "name": "Ana García",
  "birth_date": "2000-05-15"
}
```

---

## 3. Esquema de Base de Datos y Modelos INSERT

El módulo persistente consta de la tabla `authentication_user`:

### 3.1. DDL SQL (Tabla de Usuarios)

```sql
CREATE TABLE IF NOT EXISTS authentication_user (
    id              VARCHAR(36) PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    rol             VARCHAR(50)  NOT NULL, -- admin | manager | coach | participant
    state           VARCHAR(50)  NOT NULL, -- active | inactive | blocked
    birth_date      DATE         NOT NULL,
    attempts        INTEGER      NOT NULL DEFAULT 0,
    blocked_until   TIMESTAMP    NULL,
    last_login      TIMESTAMP    NULL,
    created_at      TIMESTAMP    NOT NULL,
    updated_at      TIMESTAMP    NOT NULL
);
```

---

### 3.2. Script INSERT SQL de Ejemplo

```sql
-- Usuario de Prueba con contraseña pre-hasheada (ej. de hash bcrypt de 'password123')
INSERT INTO authentication_user (
    id, email, password_hash, name, rol, state, birth_date,
    attempts, blocked_until, last_login, created_at, updated_at
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'usuario@ejemplo.com',
    '$2b$12$XxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx',
    'Juan Pérez',
    'participant',
    'active',
    '2000-05-15',
    0,
    NULL,
    NOW(),
    NOW(),
    NOW()
);
```

---

*Última actualización: PMV2 — authentication*
