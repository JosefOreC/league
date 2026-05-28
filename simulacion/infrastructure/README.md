# simulacion/infrastructure — Documentación de Endpoints

> **Stack:** Django 6 + DRF + PostgreSQL + JWT  
> **Módulo:** `simulacion`  
> **Prefijo base:** `/api/simulacion/`  
> **Autenticación:** Bearer JWT en todas las rutas

---

## HU-SIM-01 — Contexto de simulación del torneo

### `GET /api/simulacion/torneo/<tournament_id>/contexto/`

Retorna el contexto completo de simulación: datos del torneo, datos del equipo
del representante autenticado (con conteo de participantes) y los criterios de
evaluación oficiales del torneo.

### Headers obligatorios

| Header          | Valor                   |
|-----------------|------------------------|
| `Authorization` | `Bearer <access_token>` |
| `Content-Type`  | `application/json`      |

### Rol requerido: `PARTICIPANT` (líder de equipo / representante)

### Body: ninguno (petición GET)

### Response 200

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
    }
  ]
}
```

### Códigos de error

| HTTP | Payload | Causa |
|------|---------|-------|
| `401` | `{"error": "Token de autenticación requerido"}` | Header `Authorization` ausente o JWT inválido/expirado |
| `401` | `{"error": "Token de acceso inválido"}` | Token no es de tipo `access` |
| `403` | `{"error": "No tiene permisos suficientes, <rol>"}` | Rol del JWT no es `PARTICIPANT` |
| `403` | `{"error": "No tiene un equipo aprobado en este torneo"}` | `user_id` del JWT no es `representante_id` de ningún equipo `APROBADO` en el torneo |
| `404` | `{"error": "Torneo no encontrado"}` | `tournament_id` no existe en la BD |

### Ejemplo `curl`

```bash
curl -X GET \
  "http://localhost:8000/api/simulacion/torneo/3fa85f64-5717-4562-b3fc-2c963f66afa6/contexto/" \
  -H "Authorization: Bearer <token>"
```

### Notas de implementación

- **≤3 queries SQL**: 1 query principal + 2 prefetches (`criterias`, `teams`).
  La anotación `total_approved_teams=Count(...)` se incluye en la query principal.
- Reutiliza `TournamentModel`, `CriteriaModel`, `TeamModel`, `ParticipantModel` de `competencia/`.

---

## HU-SIM-02/03/04/05 — Ejecutar simulación predictiva

### `POST /api/simulacion/torneo/<tournament_id>/ejecutar/`

Evalúa el texto de un entregable contra los criterios del torneo usando el motor
heurístico determinista (sin LLM), retornando:
- **HU-SIM-02**: calificación simulada por criterio + puntaje total.
- **HU-SIM-03**: posición estimada en el torneo.
- **HU-SIM-04**: fortalezas y debilidades automáticas.
- **HU-SIM-05**: retroalimentación accionable en español.

### Headers obligatorios

| Header          | Valor                   |
|-----------------|------------------------|
| `Authorization` | `Bearer <access_token>` |
| `Content-Type`  | `application/json`      |

### Rol requerido: `PARTICIPANT` (líder de equipo / representante)

### Body esperado

```json
{
  "entregable": "Texto descriptivo del entregable del equipo. Debe tener al menos 100 caracteres y describir el proyecto con suficiente detalle para que el motor heurístico pueda evaluar cada criterio de forma significativa."
}
```

### Response 200

```json
{
  "simulation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "scores": [
    {
      "criterio_id": "c1d2e3f4-a5b6-7890-1234-abcdef567890",
      "nombre": "Diseño técnico",
      "peso": 30.0,
      "valor_simulado": 72.5,
      "valor_normalizado": 72.5,
      "en_rango": true
    },
    {
      "criterio_id": "d2e3f4a5-b6c7-8901-2345-bcdef0678901",
      "nombre": "Innovación",
      "peso": 25.0,
      "valor_simulado": 65.0,
      "valor_normalizado": 65.0,
      "en_rango": true
    }
  ],
  "puntaje_total": 69.13,
  "posicion_estimada": {
    "posicion_estimada": 3,
    "total_equipos": 10,
    "percentil": 69.0
  },
  "fortalezas": [
    {
      "criterio_id": "c1d2e3f4-a5b6-7890-1234-abcdef567890",
      "nombre": "Diseño técnico",
      "valor_normalizado": 72.5,
      "motivo": "Criterio con mayor desempeño relativo"
    }
  ],
  "debilidades": [
    {
      "criterio_id": "d2e3f4a5-b6c7-8901-2345-bcdef0678901",
      "nombre": "Trabajo en equipo",
      "valor_normalizado": 48.0,
      "motivo": "Puntaje por debajo del 50% del rango máximo del criterio"
    }
  ],
  "retroalimentacion": {
    "resumen": "Tu equipo obtuvo un puntaje total simulado de 69.13/100, lo que lo ubica en la posición estimada 3 de 10 equipos (percentil 69.0).",
    "recomendaciones": [
      "Refuerza el criterio 'Trabajo en equipo': obtuvo 48.0% del rango máximo. Puntaje por debajo del 50% del rango máximo del criterio."
    ],
    "sin_mejoras_criticas": false
  }
}
```

### Respuesta cuando todo está sobre el 80%

```json
{
  "retroalimentacion": {
    "resumen": "Tu equipo obtuvo un puntaje total simulado de 88.50/100 ... El desempeño global es sobresaliente en todos los criterios.",
    "recomendaciones": [],
    "sin_mejoras_criticas": true
  }
}
```

### Respuesta con un único equipo aprobado

```json
{
  "posicion_estimada": {
    "posicion_estimada": 1,
    "total_equipos": 1,
    "percentil": 70.0,
    "advertencia": "Estimación con muestra única"
  }
}
```

### Códigos de error

| HTTP | Payload | Causa |
|------|---------|-------|
| `400` | `{"campo": "entregable", "error": "requerido"}` | Body sin campo `entregable` o vacío |
| `400` | `{"error": "El entregable debe tener al menos 100 caracteres", "actual_length": 45}` | Texto menor a 100 chars |
| `401` | `{"error": "Token de autenticación requerido"}` | JWT ausente o inválido |
| `403` | `{"error": "No tiene permisos suficientes, <rol>"}` | Rol no es `PARTICIPANT` |
| `403` | `{"error": "No tiene un equipo aprobado en este torneo"}` | Sin equipo `APROBADO` en el torneo |
| `404` | `{"error": "Torneo no encontrado"}` | `tournament_id` inexistente |

### Ejemplo `curl`

```bash
curl -X POST \
  "http://localhost:8000/api/simulacion/torneo/3fa85f64-5717-4562-b3fc-2c963f66afa6/ejecutar/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "entregable": "Nuestro proyecto integra sensores ultrasónicos para navegación autónoma. El diseño técnico usa arquitectura modular con microcontroladores ARM. La innovación es el algoritmo de detección de obstáculos en tiempo real con IA embebida. Trabajamos en equipo con metodología ágil."
  }'
```

### Notas de implementación

- **Motor determinista**: mismo entregable + mismo contexto → mismo `simulation_id` y mismos `scores`.  
  `simulation_id` = UUID v5 derivado de `(tournament_id, team_id, entregable)`.
- **Sin persistencia**: el resultado no se guarda en BD (conforme al alcance del PMV2).
- **Sin N+1**: reutiliza la misma query optimizada de HU-SIM-01.
- **Motor heurístico**: combina calidad base del texto (longitud + riqueza léxica) con solapamiento de keywords del criterio. Pesos: 30% calidad base + 70% keyword-match.
- **Fortalezas/debilidades**: sin overlap garantizado. Para n≤3 criterios: máx. 1 en cada lista.

---

*Última actualización: HU-SIM-02/03/04/05 — PMV2*
