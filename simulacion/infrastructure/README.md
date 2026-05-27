# simulacion/infrastructure — Documentación de Endpoints

> **Stack:** Django 6 + DRF + PostgreSQL + JWT  
> **Módulo:** `simulacion`  
> **Prefijo base:** `/api/simulacion/`  
> **Autenticación:** Bearer JWT en todas las rutas

---

## HU-SIM-01 — Contexto de simulación del torneo

### `GET /api/simulacion/torneo/<tournament_id>/contexto/`

Retorna el contexto completo de simulación para el líder de equipo autenticado:
datos del torneo, datos de su equipo (con conteo de participantes) y los criterios
de evaluación oficiales del torneo.

---

### Headers obligatorios

| Header          | Valor                          |
|-----------------|-------------------------------|
| `Authorization` | `Bearer <access_token>`        |
| `Content-Type`  | `application/json`             |

---

### Rol requerido

`SystemRol.PARTICIPANT` — Líder de equipo (representante)

---

### Parámetros de ruta

| Parámetro       | Tipo   | Descripción                      |
|-----------------|--------|----------------------------------|
| `tournament_id` | string | ID (UUID) del torneo objetivo    |

---

### Body esperado

Ninguno. Es una petición `GET`.

---

### Response 200 — Éxito

```json
{
  "tournament": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Liga Nacional de Robótica 2026",
    "state": "INSCRIPCION",
    "category": "SECUNDARIA"
  },
  "team": {
    "id": "b1c2d3e4-f5a6-7890-abcd-ef1234567890",
    "name": "Team Alpha",
    "nivel_tecnico_declarado": "INTERMEDIO",
    "participants_count": 5
  },
  "criterios": [
    {
      "id": "c1d2e3f4-a5b6-7890-1234-abcdef567890",
      "name": "Diseño técnico",
      "description": "Calidad del diseño técnico del prototipo presentado",
      "peso": 30.0,
      "min_qualification": 0.0,
      "max_qualification": 100.0
    },
    {
      "id": "d2e3f4a5-b6c7-8901-2345-bcdef0678901",
      "name": "Presentación oral",
      "description": "Claridad y seguridad en la exposición ante el jurado",
      "peso": 25.0,
      "min_qualification": 0.0,
      "max_qualification": 100.0
    },
    {
      "id": "e3f4a5b6-c7d8-9012-3456-cdef01789012",
      "name": "Trabajo en equipo",
      "description": "Coordinación y colaboración observada durante la competencia",
      "peso": 20.0,
      "min_qualification": 0.0,
      "max_qualification": 100.0
    },
    {
      "id": "f4a5b6c7-d8e9-0123-4567-def012890123",
      "name": "Innovación",
      "description": "Originalidad y creatividad de la solución propuesta",
      "peso": 25.0,
      "min_qualification": 0.0,
      "max_qualification": 100.0
    }
  ]
}
```

---

### Códigos de error

| Código HTTP | Payload                                                      | Causa                                                       |
|-------------|--------------------------------------------------------------|-------------------------------------------------------------|
| `401`       | `{"error": "Token de autenticación requerido"}`             | Header `Authorization` ausente o JWT inválido/expirado      |
| `401`       | `{"error": "Token de acceso inválido"}`                     | El token no es de tipo `access`                             |
| `403`       | `{"error": "No tiene permisos suficientes, <rol>"}`         | El JWT es válido pero el rol no es `PARTICIPANT`            |
| `403`       | `{"error": "No tiene un equipo aprobado en este torneo"}`   | El torneo existe pero el `user_id` del JWT no es `representante_id` de ningún equipo con `estado_inscripcion='APROBADO'` |
| `404`       | `{"error": "Torneo no encontrado"}`                         | El `tournament_id` no existe en la base de datos            |

---

### Ejemplo `curl`

```bash
curl -X GET \
  "http://localhost:8000/api/simulacion/torneo/3fa85f64-5717-4562-b3fc-2c963f66afa6/contexto/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

---

### Notas de implementación

- **Una sola consulta SQL**: El repositorio usa `prefetch_related` con `Prefetch` explícito
  para `criterias` y `teams`, garantizando máximo 3 queries (1 principal + 2 prefetches).
- **No N+1**: Verificado con `assertNumQueries(3)` en el test de integración.
- **Reutilización de modelos**: No se crean modelos ORM propios; se usan
  `TournamentModel`, `CriteriaModel`, `TeamModel` y `ParticipantModel` de `competencia/`.
- **Arquitectura hexagonal**: La vista solo conoce el caso de uso; el caso de uso
  solo conoce el port; el repositorio implementa el port.

---

*Última actualización: HU-SIM-01 — PMV2*
