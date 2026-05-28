# PMV2 — Módulo de Simulación

> **Stack:** Django 6 + DRF + PostgreSQL + JWT
> **Arquitectura:** hexagonal modular por app (`domain` / `application` / `infrastructure`)
> **Alcance del PMV:** solo carpeta `simulacion/`, sin UI, rol objetivo: líder de equipo (representante)

---

## 1. Reglas de desarrollo (innegociables)

1. Solo se trabaja dentro de la carpeta `simulacion/`.
2. Sin UI. El entregable es API REST (DRF) probado con curl o Postman.
3. Solo el caso de uso del líder de equipo. Otros roles quedan fuera del PMV2.
4. **Reutilización primero**: si un modelo de `competencia/` ya contiene los datos requeridos, se reutiliza. Solo se crea un modelo ORM nuevo en `simulacion/infrastructure/adapters/output/models.py` cuando ningún modelo existente cubre el dato (ej.: historial persistente de simulaciones). Cada modelo nuevo lleva un comentario al inicio del archivo justificando por qué los modelos existentes no servían.
5. Consultas optimizadas con join: `select_related` y `prefetch_related` en una sola query por endpoint. Prohibido N+1. Verificable con `assertNumQueries` en los tests.
6. Autenticación JWT obligatoria en todos los endpoints mediante `@auth_required` de `authentication.infrastructure.security.auth_decorator`.
7. Arquitectura hexagonal preservada: `domain` (entidades + ports) → `application` (use_cases) → `infrastructure` (adapters + repositories).
8. **Documentación obligatoria**: `simulacion/infrastructure/README.md` con la documentación de cada endpoint (ruta, método, body, response, errores, rol requerido). Se actualiza en la misma PR que añade el endpoint.

---

## 2. Alcance funcional reducido

### 2.1 RFs conservados

| Código   | Descripción                                          | Cobertura                |
|----------|------------------------------------------------------|--------------------------|
| RF2-001  | Módulo de simulación de escenarios competitivos      | HU-SIM-01 + HU-SIM-02    |
| RF2-003  | Ejecución de simulaciones por equipo                 | HU-SIM-02                |
| RF2-004  | Motor de análisis predictivo del desempeño           | HU-SIM-02                |
| RF2-005  | Predicción de posición final estimada                | HU-SIM-03                |
| RF2-006  | Identificación de fortalezas y debilidades           | HU-SIM-04                |
| RF2-011  | Retroalimentación automática post-simulación         | HU-SIM-05                |

### 2.2 RFs diferidos

| Código   | Descripción                                  | Motivo                                                                                                          |
|----------|----------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| RF2-002  | Configuración de variables de simulación     | El PMV usa los pesos y rangos ya definidos en `CriteriaModel` del torneo. Ajustes finos requieren UI dedicada.  |
| RF2-009  | Panel de simulación para el docente          | Pertenece a otro rol y a un flujo de revisión. Fuera del foco del líder de equipo.                              |
| RF2-012  | Modo de práctica libre                       | Requiere desacoplar la simulación del torneo y criterios oficiales. Iteración posterior.                        |

### 2.3 RNFs aplicados

| Código     | Requerimiento                          | Forma de cumplimiento                                                                                              |
|------------|----------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| RNF2-001   | Rendimiento de simulaciones            | Una sola consulta SQL por endpoint con `select_related`/`prefetch_related`. P95 < 800 ms en dataset de prueba.     |
| RNF2-002   | Precisión del modelo predictivo        | Motor determinista basado en keywords ponderadas y normalización por rango de cada criterio (min/max).             |
| RNF2-004   | Disponibilidad del módulo              | Endpoints en `/api/simulacion/` con el resto de la API; sin dependencias externas bloqueantes.                     |
| RNF2-010   | Seguridad de datos                     | `@auth_required([SystemRol.PARTICIPANT])` + validación de que `user_id` del JWT coincide con `representante_id`.   |
| RNF2-006   | Visualización interactiva              | **Diferido**: aplica regla "sin UI".                                                                                |
| RNF2-009   | Compatibilidad con móviles             | **Diferido**: aplica regla "sin UI".                                                                                |

---

## 3. Arquitectura objetivo de `simulacion/`

```
simulacion/
├── domain/
│   ├── entities/
│   │   ├── simulation_input.py        # VO: texto entregable + tournament_id + team_id
│   │   ├── criterion_score.py         # VO: criterio_id, nombre, peso, valor, normalizado
│   │   └── simulation_result.py       # Agregado: scores + posición + fortalezas + feedback
│   └── ports/
│       ├── tournament_context_port.py # Lee torneo+criterios+equipo con UN solo JOIN
│       └── scoring_engine_port.py     # Motor de scoring del entregable
├── application/
│   └── use_cases/
│       ├── get_simulation_context_use_case.py   # HU-SIM-01
│       └── run_simulation_use_case.py           # HU-SIM-02..05
├── infrastructure/
│   ├── README.md                                 # ← documentación de endpoints (obligatoria)
│   ├── adapters/input/api/
│   │   ├── views.py     # @api_view + @auth_required
│   │   └── urls.py
│   ├── repositories/
│   │   └── tournament_context_repository.py    # select_related + prefetch_related
│   └── scoring/
│       └── heuristic_scoring_engine.py         # implementación determinista
└── test/
    └── test_run_simulation_use_case.py
```

### 3.1 Modelos reutilizados desde `competencia/`

| Modelo            | Campos utilizados                                                                                                  |
|-------------------|--------------------------------------------------------------------------------------------------------------------|
| `TournamentModel` | `id`, `name`, `state`, `category`, `config_tournament`                                                              |
| `CriteriaModel`   | `id`, `name`, `description`, `value` (peso), `min_value_qualification`, `max_value_qualification`, `tournament_id` |
| `TeamModel`       | `id`, `name`, `tournament_id`, `representante_id`, `estado_inscripcion`, `nivel_tecnico_declarado`                  |
| `ParticipantModel`| Conteo vía `prefetch` para validar tamaño del equipo (lectura, no escritura)                                       |

### 3.2 Patrón de consulta optimizada

```python
from competencia.infrastructure.adapters.output.models import (
    TournamentModel, CriteriaModel, TeamModel
)
from django.db.models import Prefetch, Count

tournament = (
    TournamentModel.objects
    .prefetch_related(
        Prefetch('criterias', queryset=CriteriaModel.objects.order_by('name')),
        Prefetch(
            'teams',
            queryset=TeamModel.objects
                .filter(representante_id=user_id, estado_inscripcion='APROBADO')
                .annotate(participants_count=Count('participants'))
        )
    )
    .filter(pk=tournament_id)
    .first()
)
```

---

## 4. Épicas e Historias de Usuario

### Épica 1 — `E-SIM-CTX` — Contexto de simulación
Objetivo: el líder de equipo recupera, con una sola consulta, los criterios oficiales del torneo y los datos de su equipo, listos para alimentar el motor de simulación.
Historias: **HU-SIM-01**

### Épica 2 — `E-SIM-ENGINE` — Motor de simulación predictiva
Objetivo: el líder envía un entregable textual y el sistema calcula una calificación simulada por criterio, basada en los pesos y rangos del torneo.
Historias: **HU-SIM-02**

### Épica 3 — `E-SIM-RESULT` — Resultados, análisis y retroalimentación
Objetivo: a partir del scoring, devolver la posición final estimada, fortalezas/debilidades, y feedback automático accionable.
Historias: **HU-SIM-03, HU-SIM-04, HU-SIM-05**

---

## 5. Historia de Usuario — HU-SIM-01

| Campo        | Valor                                                                                                                                                                                                                                                                                                              |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **ID**       | HU-SIM-01                                                                                                                                                                                                                                                                                                          |
| **Épica**    | E-SIM-CTX — Contexto de simulación                                                                                                                                                                                                                                                                                 |
| **Título**   | Obtener contexto de simulación del torneo                                                                                                                                                                                                                                                                          |
| **Historia** | Como líder de equipo (representante) de un equipo aprobado en un torneo, quiero consultar los criterios oficiales de evaluación y la información básica de mi equipo en una sola llamada, para poder preparar mi entregable de simulación conociendo exactamente cómo será calificado.                              |
| **Prioridad**| Alta — bloquea a HU-SIM-02                                                                                                                                                                                                                                                                                          |
| **Estimación**| 1 h                                                                                                                                                                                                                                                                                                                |

### Criterios de Aceptación

**Escenario: Contexto recuperado con éxito (representante autorizado)**
- **Dado** el líder de equipo inició sesión con un JWT válido (rol `PARTICIPANT`)
- **Dado** el líder es `representante_id` de un `TeamModel` con `estado_inscripcion = APROBADO` en el torneo objetivo
- **Cuando** envía `GET /api/simulacion/torneo/<tournament_id>/contexto/` con `Authorization: Bearer <token>`
- **Entonces** el sistema responde `HTTP 200` con el payload:
  ```json
  {
    "tournament": { "id": "...", "name": "...", "state": "...", "category": "..." },
    "team": { "id": "...", "name": "...", "nivel_tecnico_declarado": "...", "participants_count": 5 },
    "criterios": [
      { "id": "...", "name": "...", "description": "...", "peso": 25.0, "min_qualification": 0.0, "max_qualification": 100.0 }
    ]
  }
  ```
- **Entonces** la suma de pesos de criterios suma 100% (o el total configurado en el torneo)
- **Entonces** la información se obtiene con **UNA sola consulta SQL** usando `select_related`/`prefetch_related`

**Escenario: Líder no es representante del equipo en ese torneo**
- **Dado** el JWT pertenece a un usuario que no figura como `representante_id` de ningún equipo aprobado en el torneo
- **Cuando** envía `GET /api/simulacion/torneo/<tournament_id>/contexto/`
- **Entonces** el sistema responde `HTTP 403` con `{ "error": "No tiene un equipo aprobado en este torneo" }`

**Escenario: Torneo no existe**
- **Dado** el `tournament_id` de la URL no existe en la base de datos
- **Cuando** envía `GET /api/simulacion/torneo/<tournament_id>/contexto/`
- **Entonces** el sistema responde `HTTP 404` con `{ "error": "Torneo no encontrado" }`

**Escenario: Acceso sin autenticación**
- **Dado** la petición no incluye header `Authorization` o el JWT es inválido/expirado
- **Cuando** envía `GET /api/simulacion/torneo/<tournament_id>/contexto/`
- **Entonces** el sistema responde `HTTP 401` con `{ "error": "Token de autenticación requerido" }`

**Escenario: Cumplimiento de la regla de optimización por join**
- **Dado** se inspecciona el query log de Django durante la ejecución del endpoint
- **Cuando** se ejecuta el endpoint con un torneo que tiene 8 criterios y un equipo con 5 participantes
- **Entonces** el número total de queries SQL emitidas es ≤ 3 (1 query principal + prefetch internas controladas)
- **Entonces** no se observa el patrón N+1

---

## 6. Historia de Usuario — HU-SIM-02

| Campo          | Valor |
|----------------|-------|
| **ID**         | HU-SIM-02 |
| **Épica**      | E-SIM-ENGINE — Motor de simulación predictiva |
| **Título**     | Ejecutar simulación predictiva sobre un entregable textual |
| **Historia**   | Como líder de equipo, quiero enviar un texto que describa el entregable de mi equipo y recibir como respuesta una calificación simulada por cada criterio del torneo, para anticipar cómo nos evaluará el jurado antes de competir. |
| **Prioridad**  | Alta — núcleo del PMV |
| **Estimación** | 3 h |
| **Dependencias**| HU-SIM-01 |

### Criterios de Aceptación

**Escenario: Simulación exitosa devuelve scores por criterio**
- **Dado** el líder tiene un equipo aprobado en el torneo y un JWT válido
- **Dado** el torneo tiene N criterios definidos en `CriteriaModel` con sus pesos y rangos
- **Cuando** envía `POST /api/simulacion/torneo/<tournament_id>/ejecutar/` con body `{ "entregable": "<texto>" }` y un texto de al menos 100 caracteres
- **Entonces** el sistema responde `HTTP 200` con `{ simulation_id, scores: [{ criterio_id, nombre, peso, valor_simulado, valor_normalizado, en_rango }], puntaje_total }`
- **Entonces** cada `valor_simulado` respeta el `min_value_qualification` y `max_value_qualification` del criterio
- **Entonces** `puntaje_total = Σ (valor_normalizado_i × peso_i / 100)`, redondeado a 2 decimales
- **Entonces** el cálculo se realiza con UNA sola consulta SQL

**Escenario: Entregable demasiado corto**
- **Dado** el líder envía un body con `entregable` de menos de 100 caracteres
- **Cuando** envía `POST /api/simulacion/torneo/<tournament_id>/ejecutar/`
- **Entonces** el sistema responde `HTTP 400` con `{ "error": "El entregable debe tener al menos 100 caracteres", "actual_length": <n> }`

**Escenario: Campo `entregable` ausente**
- **Dado** el body no incluye el campo `entregable` o lo envía vacío
- **Cuando** envía `POST /api/simulacion/torneo/<tournament_id>/ejecutar/`
- **Entonces** el sistema responde `HTTP 400` con `{ "campo": "entregable", "error": "requerido" }`

**Escenario: Líder sin equipo aprobado en el torneo**
- **Dado** el JWT no corresponde al `representante_id` de ningún equipo aprobado
- **Cuando** envía `POST /api/simulacion/torneo/<tournament_id>/ejecutar/`
- **Entonces** el sistema responde `HTTP 403` con `{ "error": "No tiene un equipo aprobado en este torneo" }`

**Escenario: Determinismo del motor de scoring**
- **Dado** el motor recibe dos veces el mismo entregable con el mismo conjunto de criterios
- **Cuando** se ejecuta la simulación dos veces consecutivas
- **Entonces** los scores devueltos son idénticos (motor determinista)
- **Entonces** esto es verificable por un test unitario en `simulacion/test/`

---

## 7. Historia de Usuario — HU-SIM-03

| Campo          | Valor |
|----------------|-------|
| **ID**         | HU-SIM-03 |
| **Épica**      | E-SIM-RESULT — Resultados y retroalimentación |
| **Título**     | Predicción de posición final estimada |
| **Historia**   | Como líder de equipo, quiero ver, junto con mi puntaje simulado, una estimación de la posición final en la que terminaría mi equipo en el torneo, para tener una referencia concreta de qué tan competitivos somos. |
| **Prioridad**  | Media-Alta |
| **Estimación** | 1.5 h |
| **Dependencias**| HU-SIM-02 |

### Criterios de Aceptación

**Escenario: Posición estimada incluida en el response**
- **Dado** el torneo tiene M equipos con `estado_inscripcion = APROBADO`
- **Cuando** el motor calcula el `puntaje_total` del equipo
- **Entonces** el response incluye `{ posicion_estimada: <1..M>, total_equipos: M, percentil: <0..100> }`
- **Entonces** la `posicion_estimada` se calcula mapeando el `puntaje_total` contra una distribución de referencia derivada del `nivel_tecnico_declarado` del equipo

**Escenario: Torneo con un único equipo aprobado**
- **Dado** el equipo del líder es el único con `estado_inscripcion = APROBADO`
- **Cuando** se ejecuta la simulación
- **Entonces** `posicion_estimada = 1` y `total_equipos = 1`
- **Entonces** se incluye `{ "advertencia": "Estimación con muestra única" }`

**Escenario: Consistencia entre ejecuciones**
- **Dado** se ejecuta dos veces la simulación con el mismo entregable
- **Cuando** el conjunto de equipos aprobados del torneo no cambió
- **Entonces** la `posicion_estimada` es idéntica en ambas ejecuciones

---

## 8. Historia de Usuario — HU-SIM-04

| Campo          | Valor |
|----------------|-------|
| **ID**         | HU-SIM-04 |
| **Épica**      | E-SIM-RESULT — Resultados y retroalimentación |
| **Título**     | Identificación automática de fortalezas y debilidades |
| **Historia**   | Como líder de equipo, quiero que la simulación destaque automáticamente en qué criterios mi entregable obtuvo mejor y peor desempeño, para saber dónde concentrar el esfuerzo de mejora antes de competir. |
| **Prioridad**  | Media-Alta |
| **Estimación** | 1 h |
| **Dependencias**| HU-SIM-02 |

### Criterios de Aceptación

**Escenario: Listas de fortalezas y debilidades en el response**
- **Dado** la simulación ha calculado scores para todos los criterios del torneo
- **Cuando** se construye el response de `POST /api/simulacion/torneo/<id>/ejecutar/`
- **Entonces** el response incluye `{ fortalezas: [{ criterio_id, nombre, valor_normalizado, motivo }], debilidades: [{ ... }] }`
- **Entonces** `fortalezas` contiene hasta los 3 criterios con mayor `valor_normalizado`
- **Entonces** `debilidades` contiene hasta los 3 criterios con menor `valor_normalizado`
- **Entonces** el criterio en `debilidades` incluye `motivo: "Puntaje por debajo del 50% del rango máximo del criterio"` cuando aplique

**Escenario: Torneo con 3 o menos criterios**
- **Dado** el torneo tiene únicamente 2 criterios definidos
- **Cuando** se ejecuta la simulación
- **Entonces** `fortalezas` contiene a lo más 1 criterio y `debilidades` a lo más 1 (mitad superior/inferior)
- **Entonces** ningún criterio aparece simultáneamente en `fortalezas` y `debilidades`

**Escenario: Empate de scores entre criterios**
- **Dado** dos criterios reciben el mismo `valor_normalizado` en el tope/fondo
- **Cuando** se determinan fortalezas/debilidades
- **Entonces** el desempate se hace por mayor peso ponderado, luego por orden alfabético del `name`
- **Entonces** el comportamiento es determinista y reproducible

---

## 9. Historia de Usuario — HU-SIM-05

| Campo          | Valor |
|----------------|-------|
| **ID**         | HU-SIM-05 |
| **Épica**      | E-SIM-RESULT — Resultados y retroalimentación |
| **Título**     | Retroalimentación automática post-simulación |
| **Historia**   | Como líder de equipo, quiero recibir, junto con los puntajes y la posición estimada, un texto de retroalimentación claro y accionable, para entender en lenguaje natural cómo mejorar mi entregable. |
| **Prioridad**  | Media |
| **Estimación** | 1 h |
| **Dependencias**| HU-SIM-03, HU-SIM-04 |

### Criterios de Aceptación

**Escenario: Mensaje de retroalimentación generado**
- **Dado** se completaron HU-SIM-02, HU-SIM-03 y HU-SIM-04
- **Cuando** se construye el response del endpoint `POST /api/simulacion/torneo/<id>/ejecutar/`
- **Entonces** el response incluye `retroalimentacion: { resumen: "<texto>", recomendaciones: ["<r1>", "<r2>"] }`
- **Entonces** `resumen` menciona el `puntaje_total`, la posición estimada y el total de equipos
- **Entonces** `recomendaciones` incluye al menos una recomendación por cada criterio en `debilidades`

**Escenario: Retroalimentación positiva cuando todo está sobre el 80%**
- **Dado** todos los criterios obtienen `valor_normalizado ≥ 80%`
- **Cuando** se construye la retroalimentación
- **Entonces** el resumen es positivo y reconoce el desempeño global
- **Entonces** `recomendaciones` puede estar vacío y se incluye `{ "sin_mejoras_criticas": true }`

**Escenario: Idioma del feedback**
- **Dado** no se envía cabecera `Accept-Language` o se envía `Accept-Language: es`
- **Cuando** se genera la retroalimentación
- **Entonces** todos los textos se devuelven en español (es-PE)

**Escenario: Pruebas de regresión**
- **Dado** el motor recibe un mismo `(puntaje, fortalezas, debilidades)`
- **Cuando** se invoca dos veces consecutivas
- **Entonces** el texto generado es idéntico (motor determinista, sin LLM externo en este PMV)

---

## 10. Mapeo final de endpoints

| Método | Ruta                                                   | Historias que cubre                           |
|--------|--------------------------------------------------------|-----------------------------------------------|
| GET    | `/api/simulacion/torneo/<tournament_id>/contexto/`     | HU-SIM-01                                     |
| POST   | `/api/simulacion/torneo/<tournament_id>/ejecutar/`     | HU-SIM-02, HU-SIM-03, HU-SIM-04, HU-SIM-05    |

---

## 11. Checklist de cumplimiento del PMV (≤ 8 h)

- [ ] Solo se tocó la carpeta `simulacion/`
- [ ] No se duplicaron modelos ORM; si se creó alguno nuevo, queda justificado en la cabecera del archivo
- [ ] Cada endpoint hace 1 sola query con joins (verificado con `assertNumQueries` en tests)
- [ ] Sin UI: el entregable es API REST documentable con curl/Postman
- [ ] JWT obligatorio en ambos endpoints (`@auth_required` con `SystemRol.PARTICIPANT`)
- [ ] `simulacion/infrastructure/README.md` existe y cubre todos los endpoints de la PR
- [ ] RFs cubiertos: 2-001, 2-003, 2-004, 2-005, 2-006, 2-011
- [ ] RFs diferidos documentados: 2-002, 2-009, 2-012
- [ ] RNFs aplicados: 2-001, 2-002, 2-004, 2-010
- [ ] Tests deterministas (mismo input → mismo output)
