# documentacion_simulacion — Arquitectura, Endpoints y Persistencia

El módulo de **simulación** (PMV2) de League permite a los participantes realizar predicciones de su desempeño, calificar entregables de retos específicos de programación o componentes, y simular el resultado de su participación en el torneo mediante rúbricas heurísticas.

---

## 1. Índice de Endpoints (`/api/simulacion/`)

Todos los endpoints requieren autenticación con token JWT en el header `Authorization: Bearer <access_token>` mediante el decorador `@auth_required()`.

| Método | Ruta | Rol Requerido | Descripción |
|--------|------|---------------|-------------|
| `POST` | `/api/simulacion/predecir/` | `PARTICIPANT` | Simulación predictiva basada en telemetría de robot |
| `GET`  | `/api/simulacion/historial/<int:participante_id>/` | `PARTICIPANT` | Historial de predicciones de un participante |
| `GET`  | `/api/simulacion/retos/<str:torneo_id>/` | `PARTICIPANT` | Obtiene retos disponibles de un torneo (opcional: filtrar por `caso`) |
| `POST` | `/api/simulacion/analisis/programacion/` | `PARTICIPANT` | Calificación heurística/simulada de código fuente del robot |
| `POST` | `/api/simulacion/analisis/componentes/` | `PARTICIPANT` | Calificación heurística de descripción de hardware/componentes |
| `GET`  | `/api/simulacion/analisis/<str:participante_id>/<str:torneo_id>/` | `PARTICIPANT` | Lista análisis de entregas previos del participante |
| `GET`  | `/api/simulacion/torneo/<str:tournament_id>/contexto/` | `PARTICIPANT` | Obtiene contexto del torneo (equipos, participantes, criterios) |
| `POST` | `/api/simulacion/torneo/<str:tournament_id>/ejecutar/` | `PARTICIPANT` | Ejecuta la simulación predictiva de entregable final |

---

## 2. Detalle de Endpoints

### 2.1. `POST /api/simulacion/predecir/`
Evalúa la telemetría enviada por un participante para predecir el puntaje estimado, tiempo probable de finalización y RMSE de validación.

**Headers:**
`Content-Type: application/json`  
`Authorization: Bearer <access_token>`

**Body:**
```json
{
  "participante_id": 1,
  "torneo_id": 99,
  "tiempo_estimado": 45.2,
  "complejidad_codigo": 5,
  "colisiones_historicas": 2,
  "telemetria_velocidad_prom": 1.8,
  "telemetria_errores": 3
}
```

**Response 201:**
```json
{
  "id": 1,
  "puntaje_estimado": 82.5,
  "tiempo_probable_fin": 48.1,
  "rmse_validacion": 1.25,
  "modelo_version": "v1"
}
```

**Response 400 (Bad Request):**
```json
{
  "complejidad_codigo": ["Asegúrese de que este valor esté entre 1 y 10."]
}
```

**Curl:**
```bash
curl -X POST http://localhost:8000/api/simulacion/predecir/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "participante_id": 1,
    "torneo_id": 99,
    "tiempo_estimado": 45.2,
    "complejidad_codigo": 5,
    "colisiones_historicas": 2,
    "telemetria_velocidad_prom": 1.8,
    "telemetria_errores": 3
  }'
```

---

### 2.2. `GET /api/simulacion/historial/<participante_id>/`
Obtiene las predicciones de telemetría previas de un participante.

**Headers:**
`Authorization: Bearer <access_token>`

**Response 200:**
```json
[
  {
    "id": 1,
    "torneo_id": 99,
    "tiempo_estimado": 45.2,
    "complejidad_codigo": 5,
    "colisiones_historicas": 2,
    "telemetria_json": {
      "velocidad_promedio": 1.8,
      "errores": 3
    },
    "puntaje_estimado": 82.5,
    "tiempo_probable_fin": 48.1,
    "rmse_validacion": 1.25,
    "creado_en": "2026-05-27T18:00:00Z",
    "modelo_version": "v1",
    "es_oficial": false
  }
]
```

**Curl:**
```bash
curl -X GET http://localhost:8000/api/simulacion/historial/1/ \
  -H "Authorization: Bearer <token>"
```

---

### 2.3. `GET /api/simulacion/retos/<torneo_id>/`
Obtiene los retos de programación y de componentes asociados al torneo. Permite filtrar por tipo con el query parameter `?caso=PROGRAMACION` o `?caso=COMPONENTES`.

**Headers:**
`Authorization: Bearer <access_token>`

**Response 200:**
```json
[
  {
    "id": "reto-uuid-111",
    "torneo_id": "torneo-uuid-999",
    "titulo": "Navegación con Encoder",
    "descripcion": "Desarrolla el algoritmo de odometría del robot.",
    "caso": "PROGRAMACION",
    "criterios_evaluacion": [
      {
        "nombre": "Precisión de parada",
        "peso": 60.0
      },
      {
        "nombre": "Calidad del código",
        "peso": 40.0
      }
    ]
  }
]
```

**Curl:**
```bash
curl -X GET "http://localhost:8000/api/simulacion/retos/torneo-uuid-999/?caso=PROGRAMACION" \
  -H "Authorization: Bearer <token>"
```

---

### 2.4. `POST /api/simulacion/analisis/programacion/`
Envía código fuente para análisis heurístico sintáctico y de estructura del robot.

**Headers:**
`Content-Type: application/json`  
`Authorization: Bearer <access_token>`

**Body:**
```json
{
  "reto_id": "reto-uuid-111",
  "participante_id": "part-uuid-999",
  "torneo_id": "torneo-uuid-999",
  "codigo_fuente": "def motor_control(speed):\n  if speed > 100: speed = 100\n  set_pwm(speed)"
}
```

**Response 201:**
```json
{
  "id": "analisis-uuid-abc",
  "caso": "PROGRAMACION",
  "reto_id": "reto-uuid-111",
  "puntaje_total_simulado": 85.0,
  "calificaciones_por_criterio": [
    {
      "criterio": "Uso de estructuras de control",
      "puntos": 9.0,
      "max_puntos": 10.0
    },
    {
      "criterio": "Modularidad",
      "puntos": 8.0,
      "max_puntos": 10.0
    }
  ],
  "observacion_general": "El código fuente cumple con las normas de diseño, excelente modularidad.",
  "creado_en": "2026-05-27T19:00:00Z"
}
```

**Curl:**
```bash
curl -X POST http://localhost:8000/api/simulacion/analisis/programacion/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "reto_id": "reto-uuid-111",
    "participante_id": "part-uuid-999",
    "torneo_id": "torneo-uuid-999",
    "codigo_fuente": "def motor_control(speed): pass"
  }'
```

---

### 2.5. `POST /api/simulacion/analisis/componentes/`
Envía descripción de hardware y sensores para validación de componentes del robot.

**Headers:**
`Content-Type: application/json`  
`Authorization: Bearer <access_token>`

**Body:**
```json
{
  "reto_id": "reto-uuid-222",
  "participante_id": "part-uuid-999",
  "torneo_id": "torneo-uuid-999",
  "descripcion_solucion": "Sensor ultrasónico HC-SR04 acoplado a la parte frontal a 5cm de la pista con servomotor SG90."
}
```

**Response 201:**
```json
{
  "id": "analisis-uuid-xyz",
  "caso": "COMPONENTES",
  "reto_id": "reto-uuid-222",
  "puntaje_total_simulado": 70.0,
  "calificaciones_por_criterio": [
    {
      "criterio": "Compatibilidad de voltajes",
      "puntos": 7.0,
      "max_puntos": 10.0
    }
  ],
  "observacion_general": "Configuración viable, se recomienda verificar corriente de alimentación.",
  "creado_en": "2026-05-27T19:05:00Z"
}
```

**Curl:**
```bash
curl -X POST http://localhost:8000/api/simulacion/analisis/componentes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "reto_id": "reto-uuid-222",
    "participante_id": "part-uuid-999",
    "torneo_id": "torneo-uuid-999",
    "descripcion_solucion": "Sensor ultrasónico..."
  }'
```

---

### 2.6. `GET /api/simulacion/analisis/<participante_id>/<torneo_id>/`
Obtiene una lista de análisis de entregas (programación y componentes) realizados previamente por el participante en el torneo.

**Headers:**
`Authorization: Bearer <access_token>`

**Response 200:**
```json
[
  {
    "id": "analisis-uuid-abc",
    "caso": "PROGRAMACION",
    "reto_id": "reto-uuid-111",
    "puntaje_total_simulado": 85.0,
    "calificaciones_por_criterio": [
      {
        "criterio": "Uso de estructuras de control",
        "puntos": 9.0,
        "max_puntos": 10.0
      }
    ],
    "observacion_general": "El código fuente cumple...",
    "creado_en": "2026-05-27T19:00:00Z"
  }
]
```

**Curl:**
```bash
curl -X GET http://localhost:8000/api/simulacion/analisis/part-uuid-999/torneo-uuid-999/ \
  -H "Authorization: Bearer <token>"
```

---

### 2.7. `GET /api/simulacion/torneo/<tournament_id>/contexto/`
Obtiene los datos del torneo, el equipo asociado del participante y los criterios de evaluación correspondientes.

**Headers:**
`Authorization: Bearer <access_token>`

**Response 200:**
```json
{
  "tournament": {
    "id": "torneo-uuid-999",
    "name": "Torneo Nacional de Robótica 2026",
    "state": "INSCRIPCION",
    "category": "SECUNDARIA"
  },
  "team": {
    "id": "team-uuid-999",
    "name": "RoboMasters",
    "nivel_tecnico_declarado": "INTERMEDIO",
    "participants_count": 5
  },
  "criterios": [
    {
      "id": "crit-uuid-999",
      "name": "Diseño Mecánico",
      "description": "Rúbrica para evaluar el ensamble...",
      "peso": 50.0,
      "min_qualification": 0.0,
      "max_qualification": 10.0
    }
  ]
}
```

**Curl:**
```bash
curl -X GET http://localhost:8000/api/simulacion/torneo/torneo-uuid-999/contexto/ \
  -H "Authorization: Bearer <token>"
```

---

### 2.8. `POST /api/simulacion/torneo/<tournament_id>/ejecutar/`
Simula el resultado del entregable final de manera predictiva, determinando puntajes, fortalezas/debilidades y posición estimada.

**Headers:**
`Content-Type: application/json`  
`Authorization: Bearer <access_token>`

**Body:**
```json
{
  "entregable": "Este es el entregable de al menos 100 caracteres de largo que describe detalladamente la solución mecánica y de control de nuestro robot para la competencia nacional de robótica."
}
```

**Response 200:**
```json
{
  "simulation_id": "uuid-v5-determinista",
  "scores": [
    {
      "criterio_id": "crit-uuid-999",
      "nombre": "Diseño Mecánico",
      "peso": 50.0,
      "valor_simulado": 7.5,
      "valor_normalizado": 75.0,
      "en_rango": true
    }
  ],
  "puntaje_total": 75.0,
  "posicion_estimada": {
    "posicion_estimada": 3,
    "total_equipos": 10,
    "percentil": 75.0
  },
  "fortalezas": [
    {
      "criterio_id": "crit-uuid-999",
      "nombre": "Diseño Mecánico",
      "valor_normalizado": 75.0,
      "motivo": "Criterio con mayor desempeño relativo"
    }
  ],
  "debilidades": [],
  "retroalimentacion": {
    "resumen": "Tu equipo obtuvo un puntaje total simulado de 75.00/100, lo que lo ubica en la posición estimada 3 de 10 equipos.",
    "recomendaciones": [],
    "sin_mejoras_criticas": true
  }
}
```

**Curl:**
```bash
curl -X POST http://localhost:8000/api/simulacion/torneo/torneo-uuid-999/ejecutar/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "entregable": "Este es el entregable de al menos 100 caracteres de largo..."
  }'
```

---

## 3. Estructura de Base de Datos (DDL) y Modelos INSERT

El módulo persistente consta de tres tablas administradas en el ORM de Django:

### 3.1. `simulacion_predictiva`
Guarda las simulaciones y predicciones realizadas basadas en telemetría de pista física o software.

```sql
CREATE TABLE IF NOT EXISTS simulacion_predictiva (
    id                    SERIAL PRIMARY KEY,
    participante_id       INTEGER NOT NULL,
    torneo_id             INTEGER NOT NULL,
    tiempo_estimado       DOUBLE PRECISION NOT NULL,
    complejidad_codigo    INTEGER NOT NULL,
    colisiones_historicas INTEGER NOT NULL,
    telemetria_json       JSONB NOT NULL DEFAULT '{}'::jsonb,
    puntaje_estimado      DOUBLE PRECISION NULL,
    tiempo_probable_fin   DOUBLE PRECISION NULL,
    rmse_validacion       DOUBLE PRECISION NULL,
    creado_en             TIMESTAMP NOT NULL,
    modelo_version        VARCHAR(20) NOT NULL DEFAULT 'v1',
    es_oficial            BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS simulacion_predictiva_part_torneo_idx ON simulacion_predictiva(participante_id, torneo_id);
CREATE INDEX IF NOT EXISTS simulacion_predictiva_creado_en_idx ON simulacion_predictiva(creado_en);

-- INSERT modelo:
INSERT INTO simulacion_predictiva (
    participante_id, torneo_id, tiempo_estimado, complejidad_codigo, colisiones_historicas, 
    telemetria_json, puntaje_estimado, tiempo_probable_fin, rmse_validacion, creado_en, 
    modelo_version, es_oficial
) VALUES (
    1, 99, 45.2, 5, 2, 
    '{"velocidad_promedio": 1.8, "errores": 3}'::jsonb, 82.5, 48.1, 1.25, NOW(), 
    'v1', FALSE
);
```

### 3.2. `simulacion_analisis_entrega`
Guarda el resultado heurístico del análisis individual de programación o componentes de los robots para retos concretos.

```sql
CREATE TABLE IF NOT EXISTS simulacion_analisis_entrega (
    id                          UUID PRIMARY KEY,
    reto_id                     VARCHAR(36) NOT NULL,
    participante_id             VARCHAR(36) NOT NULL,
    torneo_id                   VARCHAR(36) NOT NULL,
    caso                        VARCHAR(20) NOT NULL, -- PROGRAMACION | COMPONENTES
    contenido_entrega           TEXT NOT NULL,
    calificaciones_por_criterio JSONB NOT NULL DEFAULT '[]'::jsonb,
    puntaje_total_simulado      DOUBLE PRECISION NOT NULL,
    observacion_general         TEXT NOT NULL DEFAULT '',
    creado_en                   TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS simulacion_analisis_part_torneo_idx ON simulacion_analisis_entrega(participante_id, torneo_id);
CREATE INDEX IF NOT EXISTS simulacion_analisis_reto_idx ON simulacion_analisis_entrega(reto_id);

-- INSERT modelo:
INSERT INTO simulacion_analisis_entrega (
    id, reto_id, participante_id, torneo_id, caso, contenido_entrega, 
    calificaciones_por_criterio, puntaje_total_simulado, observacion_general, creado_en
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000', 'reto-uuid-111', 'part-uuid-999', 'torneo-uuid-999', 
    'PROGRAMACION', 'def motor_control(speed): set_pwm(speed)', 
    '[{"criterio": "Modularidad", "puntos": 8.0, "max_puntos": 10.0}]'::jsonb, 
    80.0, 'Código modular y limpio.', NOW()
);
```

### 3.3. `simulacion_resultado`
Guarda el reporte agregado de la simulación predictiva completa del torneo por equipo.

```sql
CREATE TABLE IF NOT EXISTS simulacion_resultado (
    id                    UUID PRIMARY KEY,
    tournament_id         VARCHAR(36) NOT NULL,
    equipo_id             VARCHAR(36) NOT NULL,
    entregable            TEXT NOT NULL,
    scores                JSONB NOT NULL DEFAULT '[]'::jsonb,
    puntaje_total         NUMERIC(5, 2) NOT NULL,
    posicion_estimada     INTEGER NOT NULL,
    total_equipos         INTEGER NOT NULL,
    percentil             DOUBLE PRECISION NOT NULL,
    advertencia_muestra   VARCHAR(100) NOT NULL DEFAULT '',
    fortalezas            JSONB NOT NULL DEFAULT '[]'::jsonb,
    debilidades           JSONB NOT NULL DEFAULT '[]'::jsonb,
    retro_resumen         TEXT NOT NULL DEFAULT '',
    retro_recomendaciones JSONB NOT NULL DEFAULT '[]'::jsonb,
    sin_mejoras_criticas  BOOLEAN NOT NULL DEFAULT FALSE,
    creado_en             TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS simulacion_resultado_torneo_equipo_idx ON simulacion_resultado(tournament_id, equipo_id);
CREATE INDEX IF NOT EXISTS simulacion_resultado_creado_en_idx ON simulacion_resultado(creado_en);

-- INSERT modelo:
INSERT INTO simulacion_resultado (
    id, tournament_id, equipo_id, entregable, scores, puntaje_total, 
    posicion_estimada, total_equipos, percentil, advertencia_muestra, fortalezas, 
    debilidades, retro_resumen, retro_recomendaciones, sin_mejoras_criticas, creado_en
) VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'torneo-uuid-999', 'team-uuid-999', 
    'Nuestro robot utiliza encoders para estimación de velocidad...', 
    '[{"nombre": "Diseño Mecánico", "peso": 50.0, "valor_simulado": 7.5, "valor_normalizado": 75.0, "en_rango": true}]'::jsonb,
    75.00, 3, 10, 75.0, '',
    '[{"nombre": "Diseño Mecánico", "criterio_id": "crit-uuid-999", "valor_normalizado": 75.0, "motivo": "Criterio con mayor desempeño relativo"}]'::jsonb,
    '[]'::jsonb, 'Tu equipo obtuvo un puntaje total simulado de 75.00/100, lo que lo ubica en la posición estimada 3 de 10 equipos.',
    '[]'::jsonb, TRUE, NOW()
);
```

---

*Última actualización: PMV2 — simulacion*
