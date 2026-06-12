# PLAN DE MEJORA FURPS+ — ZOIDS LEAGUE
**Versión:** 1.0  
**Fecha:** 2026-06-12  
**Autor:** Arquitecto de Software Senior  
**Entrada:** `01_Auditoria_FURPS.md`  
**Rama:** Auditoria-Furps  

---

## DECLARACIÓN DE PRINCIPIOS

> **EL SISTEMA YA FUNCIONA. PUEDE ESTAR EN PRODUCCIÓN.**  
> Toda mejora propuesta en este plan asume que existe tráfico real y datos reales.  
> Ningún cambio puede romper lo que ya opera correctamente.

Cada mejora de este plan cumple obligatoriamente los siguientes principios:

| Principio | Significado operativo |
|---|---|
| **Compatibilidad hacia atrás** | Ningún contrato de API existente cambia su forma ni rompe clientes actuales |
| **Cambios incrementales** | Cada mejora es un paso atómico verificable de forma independiente |
| **Riesgo mínimo** | Se prefiere la solución de menor impacto sobre infraestructura compartida |
| **Validación obligatoria** | Todo cambio tiene criterios de aceptación explícitos antes y después |
| **Posibilidad de rollback** | Cada cambio puede revertirse sin pérdida de datos ni degradación de servicio |

---

## RESUMEN DE BRECHAS A CUBRIR

| ID Brecha | Categoría | Severidad | Wave asignado |
|---|---|---|---|
| BC-01 `Match.set_estado()` bug | Funcionalidad | Crítica | Wave 0 |
| BC-02 `set_es_bye()` inexistente | Funcionalidad | Crítica | Wave 0 |
| BC-03 SECRET_KEY hardcodeada | Seguridad | Crítica | Wave 0 |
| BC-04 ALLOWED_HOSTS=["*"] | Seguridad | Crítica | Wave 0 |
| RS-03 API Key en docker-compose | Seguridad | Alta | Wave 0 |
| BC-05 Sin healthchecks Docker | Infraestructura | Alta | Wave 1 |
| BM-04 Fixtures sin transacción | Confiabilidad | Alta | Wave 1 |
| BM-05 Sin logging configurado | Observabilidad | Alta | Wave 1 |
| BM-02 Sin rate limiting | Seguridad | Alta | Wave 1 |
| BM-06 Standing incompleto | Funcionalidad | Alta | Wave 2 |
| BM-01 Sin paginación | Rendimiento | Alta | Wave 2 |
| Bm-08 Índices BD faltantes | Rendimiento | Media | Wave 2 |
| BM-08 Dependencias sin pin | Mantenibilidad | Media | Wave 2 |
| BM-07 Sin tests integración | Calidad | Media | Wave 3 |
| Bm-06 coverage.py ausente | Calidad | Media | Wave 3 |
| HF-03 Validación estado fixtures | Funcionalidad | Media | Wave 3 |
| HF-04 ConfigKnockout range bug | Funcionalidad | Media | Wave 3 |
| Bm-01 Sin OpenAPI/Swagger | Documentación | Media | Wave 3 |
| Bm-03 Validación formularios | Usabilidad | Media | Wave 3 |
| Bm-04 Modales de confirmación | Usabilidad | Media | Wave 3 |
| HF-05 Email no verificado | Funcionalidad | Media | Wave 3 |
| Bm-07 Sin backup strategy | Operaciones | Media | Wave 4 |
| RO-01 Sin fallback IA | Confiabilidad | Media | Wave 4 |
| Bm-05 AIRecommendations desconectado | Funcionalidad | Baja | Wave 4 |
| Bm-09 XGBoost sin versionar | IA/ML | Baja | Wave 4 |

---

## ROADMAP

```
TIMELINE
══════════════════════════════════════════════════════════════════════

  Wave 0 ── HOTFIX CRÍTICO ─────────────────────────── Días 1-2
  │  M0-01  Fix Match.set_estado() bug
  │  M0-02  Fix match.set_es_bye() → set_bye()
  │  M0-03  SECRET_KEY → variable de entorno
  │  M0-04  ALLOWED_HOSTS específico
  │  M0-05  API Keys fuera de docker-compose
  │
  Wave 1 ── CONFIABILIDAD BASE ─────────────────────── Días 3-9
  │  M1-01  Healthchecks en Docker Compose
  │  M1-02  @transaction.atomic en generación de fixtures
  │  M1-03  Logging estructurado en settings.py
  │  M1-04  Rate limiting en endpoints de autenticación
  │
  Wave 2 ── FUNCIONALIDAD + RENDIMIENTO ────────────── Días 10-21
  │  M2-01  Completar lógica de Standing
  │  M2-02  Paginación en endpoints colección
  │  M2-03  Índices compuestos en BD (migración sin downtime)
  │  M2-04  Pinear versiones de dependencias
  │
  Wave 3 ── CALIDAD + USABILIDAD ───────────────────── Días 22-42
  │  M3-01  Tests de integración HTTP (APITestCase)
  │  M3-02  Configurar coverage.py
  │  M3-03  Corregir validación de estado en GenerateFixtures
  │  M3-04  Corregir range en ConfigKnockout
  │  M3-05  OpenAPI/Swagger con drf-spectacular
  │  M3-06  Validación reactiva en formularios frontend
  │  M3-07  Modales de confirmación en acciones destructivas
  │  M3-08  Activar verificación de email en login
  │
  Wave 4 ── ESCALABILIDAD + OBSERVABILIDAD ─────────── Días 43-90
     M4-01  Estrategia de backup PostgreSQL
     M4-02  Fallback para dependencia OpenRouter
     M4-03  Conectar AIRecommendations a rutas
     M4-04  Versionamiento de modelo XGBoost

══════════════════════════════════════════════════════════════════════
```

---

## ESTRATEGIA GLOBAL DE PRESERVACIÓN DE FUNCIONALIDAD

Antes de iniciar cualquier Wave se debe establecer una **línea base verificable**:

1. **Snapshot de base de datos**: `pg_dump` manual previo a cada Wave.
2. **Suite de humo**: Ejecutar manualmente los 5 flujos críticos y documentar que pasan:
   - Flujo 1: Login → Crear torneo → Configurar reglas → Abrir inscripciones
   - Flujo 2: Inscribir equipo → Aprobar equipo → Cerrar inscripciones
   - Flujo 3: Generar fixtures → Registrar resultado → Ver posiciones
   - Flujo 4: Analizar torneo con IA → Confirmar criterios
   - Flujo 5: Ejecutar simulación → Ver predicción
3. **Validar que la suite de humo pasa** al final de cada Wave antes de continuar.
4. **Feature flags en cambios de comportamiento**: Cuando una mejora altera comportamiento observable, usar un flag de configuración para activarla gradualmente.

---

## WAVE 0 — HOTFIX CRÍTICO

> **Ventana de ejecución:** 48 horas máximo  
> **Restricción especial:** Estos cambios NO alteran contratos de API ni estructura de BD.  
> Son correcciones de 1 a 3 líneas de código cada una.

---

### M0-01 — Corrección de `Match.set_estado()`

**Objetivo:** Reparar el setter de estado de partido para que asigne correctamente el valor.

**Justificación:** El operador `==` en Python evalúa una comparación booleana sin efecto secundario; el atributo `__estado` nunca cambia. Esto hace que todo flujo que dependa del estado de un partido (avance en fixture, cierre de ronda, finalización de torneo) opere sobre datos incorrectos. Es el bug de mayor impacto en el sistema.

**Prioridad:** Crítica  
**Riesgo:** Mínimo — cambio de 1 carácter en una función de 2 líneas sin efectos secundarios.

**Dependencias:** Ninguna.

**Estrategia de validación:**
1. Verificar en tests unitarios existentes (`test_fixtures_and_standings.py`) que el estado cambia correctamente después del fix.
2. Crear un test de regresión específico: `test_match_set_estado_assigns_value()` que afirme `match.estado == "FINISHED"` después de llamar `match.set_estado("FINISHED")`.
3. Ejecutar el Flujo 3 de la suite de humo (registrar resultado → verificar que el partido queda con estado actualizado).

**Estrategia de rollback:** Git revert del commit. El cambio es atómico; un revert restaura el carácter exactamente. No afecta BD.

**Archivo:** `competencia/domain/entities/match.py:63`  
**Cambio:** `self.__estado == value` → `self.__estado = value`

---

### M0-02 — Corrección de `match.set_es_bye()` → `match.set_bye()`

**Objetivo:** Alinear la llamada en `GenerateFixturesUseCase` con el nombre real del método en la entidad `Match`.

**Justificación:** Una llamada a método inexistente produce `AttributeError` en tiempo de ejecución cuando se genera cualquier fixture que contenga byes (número de equipos no potencia de 2). Afecta directamente el flujo central de Knockout y Hybrid.

**Prioridad:** Crítica  
**Riesgo:** Mínimo — cambio de nombre de método en 1 línea. No altera lógica ni estructura.

**Dependencias:** M0-01 (ambos están en el mismo flujo de generación de fixtures; corregir en el mismo commit reduce el número de despliegues).

**Estrategia de validación:**
1. Verificar que la entidad `Match` expone exactamente un método `set_bye()` (grep del código).
2. Ejecutar `test_fixtures_and_standings.py` con un fixture de 6 equipos (fuerza byes).
3. Flujo 3 de suite de humo con número impar de equipos.

**Estrategia de rollback:** Git revert. Sin impacto en BD.

**Archivo:** `competencia/application/use_cases/generate_fixtures_use_case.py:108`  
**Cambio:** `match.set_es_bye(True)` → `match.set_bye(True)`

---

### M0-03 — Mover `SECRET_KEY` a variable de entorno

**Objetivo:** Eliminar la clave secreta de Django del código fuente y leerla desde el entorno.

**Justificación:** Una `SECRET_KEY` hardcodeada en el repositorio significa que cualquier persona con acceso al código puede forjar tokens JWT, falsificar cookies de sesión y manipular firmas CSRF. El riesgo persiste incluso después de que el repositorio sea privado porque puede haber sido clonado o cacheado.

**Prioridad:** Crítica  
**Riesgo:** Bajo-Medio. El único riesgo es que el contenedor reinicie sin la variable configurada. Mitigable con validación de arranque.

**Dependencias:** Acceso al entorno de despliegue para inyectar la variable antes de redeployar.

**Estrategia de validación:**
1. **Antes del cambio:** Documentar el valor actual de `SECRET_KEY` en un gestor de secretos (no en código).
2. Agregar a `.env` la línea `SECRET_KEY=<valor_actual>` — misma clave, distinto lugar.
3. Modificar `settings.py`: `SECRET_KEY = os.environ.get("SECRET_KEY")`.
4. Agregar validación de arranque: si `SECRET_KEY` es `None`, el proceso debe fallar con mensaje claro.
5. Rebuild y arranque del contenedor; verificar que Django inicia sin error.
6. Ejecutar Flujo 1 (login) para confirmar que JWT sigue funcionando con la misma clave.
7. Verificar que tokens generados antes del cambio siguen siendo válidos (clave no cambió, solo su ubicación).

**Estrategia de rollback:** Revertir `settings.py` al valor hardcodeado. Los tokens existentes seguirán siendo válidos porque la clave no cambió.

**Archivos:** `backend/league/settings.py`, `.env`, `.env.example`

---

### M0-04 — Especificar `ALLOWED_HOSTS`

**Objetivo:** Reemplazar `["*"]` por la lista explícita de dominios que el sistema sirve.

**Justificación:** `ALLOWED_HOSTS = ["*"]` permite que cualquier dominio sea válido en el encabezado HTTP `Host`, facilitando ataques de Host Header Injection donde un atacante puede envenenar cachés o generar URLs maliciosas en correos del sistema.

**Prioridad:** Crítica  
**Riesgo:** Bajo. El único riesgo es bloquear un dominio legítimo que no esté en la lista.

**Dependencias:** M0-03 (para leer los hosts desde variable de entorno de forma consistente).

**Estrategia de validación:**
1. Identificar TODOS los dominios desde los que el frontend llama al backend (incluyendo localhost para desarrollo).
2. Construir la lista: `["localhost", "127.0.0.1", "<dominio-producción>"]`.
3. Leer desde entorno: `ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")`.
4. Tras el despliegue, hacer una petición HTTP con `Host: evil.com` y verificar que Django retorna 400.
5. Verificar que el frontend sigue funcionando normalmente.

**Estrategia de rollback:** Revertir `settings.py`. Sin impacto en BD ni sesiones.

**Archivo:** `backend/league/settings.py`

---

### M0-05 — Mover `OPENROUTER_API_KEY` fuera de `docker-compose.yml`

**Objetivo:** Eliminar la API key de IA del archivo versionado y leerla desde un archivo `.env` ignorado por git.

**Justificación:** Las API keys en archivos versionados quedan expuestas en el historial de git, incluso si se eliminan después. Cualquier persona con acceso al repositorio puede usar la clave para realizar llamadas a expensas del propietario.

**Prioridad:** Crítica (aunque operacional, es un riesgo económico directo)  
**Riesgo:** Mínimo. Docker Compose ya soporta nativamente la lectura de `.env`.

**Dependencias:** Ninguna técnica. Requiere coordinación de equipo para no perder la clave durante la transición.

**Estrategia de validación:**
1. Copiar la clave actual al archivo `.env` local antes de modificar `docker-compose.yml`.
2. Confirmar que `.env` está en `.gitignore`.
3. En `docker-compose.yml`, reemplazar el valor literal por `${OPENROUTER_API_KEY}`.
4. Reconstruir y levantar los contenedores.
5. Hacer una llamada al endpoint `/api/ia/analizar` y verificar que responde correctamente.
6. Rotar la clave en OpenRouter dashboard (la clave anterior fue expuesta; una nueva clave invalida el riesgo histórico).

**Estrategia de rollback:** Restaurar el valor literal en `docker-compose.yml`. Sin impacto funcional.

**Archivo:** `docker-compose.yml`, `.env`, `.gitignore`

---

## WAVE 1 — CONFIABILIDAD BASE

> **Ventana de ejecución:** Días 3-9 (1 semana)  
> **Prerequisito:** Wave 0 completado y suite de humo pasando.

---

### M1-01 — Healthchecks en Docker Compose

**Objetivo:** Configurar comprobaciones de salud para los contenedores `db` y `backend` para que Docker orqueste el arranque en el orden correcto.

**Justificación:** Sin healthchecks, el contenedor `backend` puede intentar conectarse a `db` antes de que PostgreSQL esté listo para aceptar conexiones, generando errores silenciosos de inicio. En un reinicio de emergencia esto puede dejar el sistema en estado inconsistente sin alertas.

**Prioridad:** Alta  
**Riesgo:** Mínimo. Los healthchecks son configuración adicional; no modifican el comportamiento del contenedor en condiciones normales.

**Dependencias:** Ninguna.

**Estrategia de validación:**
1. Añadir `healthcheck` al servicio `db` con `pg_isready -U $DB_USER`.
2. Añadir `healthcheck` al servicio `backend` con `curl -f http://localhost:8000/api/` o similar.
3. Añadir `depends_on: db: condition: service_healthy` al servicio `backend`.
4. Detener todos los contenedores y hacer `docker compose up`; verificar en los logs que `backend` espera a que `db` reporte healthy.
5. Simular un reinicio de `db` (`docker compose restart db`) y verificar que `backend` se recupera sin intervención manual.

**Estrategia de rollback:** Eliminar los bloques `healthcheck` y `depends_on condition`. El comportamiento retorna al `depends_on` simple original.

**Archivo:** `docker-compose.yml`

---

### M1-02 — `@transaction.atomic` en generación de fixtures

**Objetivo:** Envolver la creación masiva de partidos en una transacción atómica para garantizar consistencia.

**Justificación:** La generación de un fixture Knockout de 64 equipos crea 63 filas en `competencia_match`. Si el proceso falla en la fila 40 (error de red, timeout, constraint violation), las 39 filas ya insertadas quedan huérfanas. El torneo queda en estado inconsistente y no puede recuperarse sin intervención manual en BD.

**Prioridad:** Alta  
**Riesgo:** Bajo. `@transaction.atomic` en Django es un decorator/context manager estándar. El único riesgo nuevo es que un fallo que antes dejaba datos parciales ahora deja cero datos, lo cual es el comportamiento correcto.

**Dependencias:** M0-01 y M0-02 deben estar corregidos primero (para que la generación de fixtures funcione).

**Estrategia de validación:**
1. Ejecutar `test_fixtures_and_standings.py` para confirmar que los tests siguen pasando.
2. Escribir un test de regresión que simule un fallo en la mitad de la inserción (mock del repositorio que lanza excepción en el partido N) y verificar que no quedan partidos en BD.
3. Ejecutar el Flujo 3 de la suite de humo en el entorno de staging.

**Estrategia de rollback:** Eliminar el decorator/context manager. El comportamiento retorna al no-transaccional anterior. Sin impacto en datos existentes.

**Archivo:** `competencia/application/use_cases/generate_fixtures_use_case.py`

---

### M1-03 — Logging estructurado en `settings.py`

**Objetivo:** Configurar el sistema de logging de Django para que registre eventos de nivel WARNING y superior a archivo y consola en producción.

**Justificación:** Sin logging configurado, los errores 500 en producción son invisibles hasta que un usuario los reporta. Los errores de integración con OpenRouter, fallos de BD y excepciones no capturadas pasan desapercibidos. Esto hace imposible la operación responsable del sistema.

**Prioridad:** Alta  
**Riesgo:** Mínimo. La configuración de logging es aditiva; no altera comportamiento de la aplicación.

**Dependencias:** M0-03 (para leer el nivel de log desde entorno si se desea).

**Estrategia de validación:**
1. Añadir el bloque `LOGGING` en `settings.py` con handlers para `console` y `file` (`/var/log/django/app.log`).
2. Configurar nivel DEBUG en desarrollo, WARNING en producción (leído desde `os.environ.get("LOG_LEVEL", "WARNING")`).
3. Forzar un error 500 intencional (URL inexistente) y verificar que aparece en el log.
4. Verificar que el log de acceso de gunicorn ya existente no queda duplicado.

**Estrategia de rollback:** Eliminar el bloque `LOGGING` de `settings.py`. Django retorna a su configuración de logging por defecto.

**Archivo:** `backend/league/settings.py`

---

### M1-04 — Rate limiting en endpoints de autenticación

**Objetivo:** Limitar el número de intentos de autenticación por IP para prevenir ataques de fuerza bruta.

**Justificación:** El sistema ya bloquea una cuenta después de 5 intentos fallidos, lo cual es correcto. Pero sin rate limiting de red, un atacante puede hacer miles de peticiones contra diferentes cuentas (credential stuffing) o contra cuentas válidas para provocar bloqueos masivos (DoS de autenticación).

**Prioridad:** Alta  
**Riesgo:** Medio. Un rate limiting demasiado agresivo puede bloquear usuarios legítimos que comparten IP (NAT universitario). Debe configurarse con límites generosos inicialmente.

**Dependencias:** M1-03 (logging debe estar activo para registrar los intentos bloqueados).

**Estrategia de validación:**
1. Instalar `django-ratelimit` y agregarlo a `requirements.txt` (con versión exacta).
2. Configurar: `@ratelimit(key='ip', rate='20/m', method='POST', block=True)` en `login_view` y `register_view`.
3. Comenzar con un límite generoso (20/minuto) para no afectar usuarios legítimos.
4. Probar que después de 20 peticiones POST en menos de 1 minuto desde la misma IP se recibe HTTP 429.
5. Verificar que un usuario legítimo puede hacer login normalmente.
6. Verificar que el límite se resetea después de 1 minuto.

**Estrategia de rollback:** Eliminar los decoradores `@ratelimit` y remover `django-ratelimit` de `requirements.txt`. Sin impacto en datos.

**Archivos:** `authentication/adapters/input/api/views/login_view.py`, `register_view.py`, `requirements.txt`

---

## WAVE 2 — FUNCIONALIDAD + RENDIMIENTO

> **Ventana de ejecución:** Días 10-21 (2 semanas)  
> **Prerequisito:** Wave 1 completado. Suite de humo pasando.

---

### M2-01 — Completar lógica de Standing (tabla de posiciones)

**Objetivo:** Implementar el cálculo y persistencia de posiciones después de cada registro de resultado, completando el feature que ya está parcialmente visible en UI.

**Justificación:** La tabla de posiciones (`Standing`) tiene modelo en BD y vista en frontend, pero la lógica de actualización está incompleta. Los usuarios finales ven una sección vacía o desactualizada. Es un feature que el sistema promete pero no cumple.

**Prioridad:** Alta  
**Riesgo:** Medio. La lógica de cálculo de posiciones (desempates por criterios, diferencia de puntos) puede tener variantes según el tipo de torneo. Un error puede mostrar posiciones incorrectas.

**Dependencias:** M0-01 (los estados de partido deben funcionar para que el Standing sea consistente).

**Estrategia de validación:**
1. Definir el contrato exacto: ¿qué campos calcula Standing? (posición, PJ, PG, PE, PP, puntos, diferencial).
2. Escribir tests unitarios para el calculador de posiciones **antes** de implementarlo (TDD).
3. Implementar en `register_match_result_use_case.py` la llamada al recalculador al final de cada registro.
4. Verificar con datos de un torneo Round-Robin completo (4 equipos, 6 partidos) que las posiciones son correctas.
5. Verificar que el frontend muestra la tabla actualizada sin cambios en el contrato de la API (`GET /torneo/<id>/posiciones/`).

**Estrategia de rollback:** Revertir los cambios en el use case. La tabla queda vacía como antes; no hay pérdida de datos.

**Archivos:** `competencia/application/use_cases/register_match_result_use_case.py`, `competencia/adapters/output/repositories/standing_repository_postgresql.py`

---

### M2-02 — Paginación en endpoints de colección

**Objetivo:** Implementar paginación basada en cursor o número de página en todos los endpoints que devuelven listas sin límite.

**Justificación:** `GET /api/competencia/all/` sin paginación retorna todos los torneos en una sola respuesta. Con 500+ torneos esto supera los 5 MB de payload, degrada el tiempo de respuesta del servidor y puede saturar la memoria del cliente. El riesgo crece con el tiempo.

**Prioridad:** Alta  
**Riesgo:** Medio-Alto. **Este es el cambio con mayor riesgo de romper el frontend.** Si el cliente espera un array y recibe `{results: [], count: N, next: "..."}`, se rompe el renderizado.

**Principio de compatibilidad aplicado:** Implementar paginación de forma **opt-in** primero.  
- Estrategia: añadir parámetro `?page=1&page_size=20`. Si no se envía, retorna el comportamiento actual (sin paginación). En un sprint posterior, hacer el paginado obligatorio.

**Dependencias:** M1-03 (logging para monitorear tiempos de respuesta antes y después).

**Estrategia de validación:**
1. Verificar que el frontend sigue funcionando con la respuesta sin paginar (primera fase: paginación opt-in).
2. Con `?page=1&page_size=5`, verificar que se retornan exactamente 5 registros y que `next` apunta a la página siguiente.
3. Verificar que `?page=99` con datos insuficientes retorna `{results: [], count: N, next: null}` sin error 500.
4. Medir el tiempo de respuesta antes/después con 100 torneos en BD.

**Estrategia de rollback:** Eliminar la clase paginadora de la configuración DRF. Las vistas retornan al comportamiento anterior sin paginación.

**Archivos:** `backend/league/settings.py` (configuración DRF), views de competencia.

---

### M2-03 — Índices compuestos en base de datos (migración sin downtime)

**Objetivo:** Agregar índices en columnas de alta frecuencia de consulta para reducir tiempos de respuesta.

**Justificación:** Columnas como `estado` en `competencia_tournament` o `(tournament_id, estado)` en `competencia_team` se usan en filtros frecuentes sin índice, forzando full table scans. Con 10.000+ registros esto se vuelve perceptible para el usuario.

**Prioridad:** Media  
**Riesgo:** Bajo-Medio. La creación de índices en PostgreSQL **puede bloquear escrituras** si se usa `CREATE INDEX` estándar. Solución: usar `CREATE INDEX CONCURRENTLY` que PostgreSQL aplica sin bloquear.

**Índices propuestos:**
```sql
-- authentication_user (login busca por email)
CREATE INDEX CONCURRENTLY idx_user_email ON authentication_user(email);

-- Torneos por estado
CREATE INDEX CONCURRENTLY idx_tournament_estado ON competencia_tournament(estado);

-- Equipos por torneo y estado
CREATE INDEX CONCURRENTLY idx_team_tournament_estado ON competencia_team(tournament_id, estado);

-- Partidos por torneo y ronda
CREATE INDEX CONCURRENTLY idx_match_tournament_round ON competencia_match(tournament_id, round);
```

**Dependencias:** Ninguna técnica. Requiere conocer el volumen de datos actual.

**Estrategia de validación:**
1. Crear una migración Django vacía con `RunSQL` usando `CREATE INDEX CONCURRENTLY`.
2. Verificar con `EXPLAIN ANALYZE` que las queries críticas usan el índice nuevo (Index Scan vs Seq Scan).
3. Medir tiempos de respuesta de `/api/competencia/all/` antes y después.
4. Verificar que no hubo bloqueos durante la migración revisando logs de PostgreSQL.

**Estrategia de rollback:** Migración inversa con `DROP INDEX CONCURRENTLY idx_*`. Sin impacto en datos.

**Archivo:** Nueva migración en `competencia/migrations/` y `authentication/migrations/`

---

### M2-04 — Pinear versiones de dependencias

**Objetivo:** Reemplazar rangos abiertos (`>=`) por versiones exactas en `requirements.txt` para garantizar builds reproducibles.

**Justificación:** `openai>=1.0.0` puede instalar `openai==2.x.x` en un próximo build si la librería publica una nueva major version con breaking changes. Esto puede romper silenciosamente la integración con OpenRouter sin que ningún test lo detecte.

**Prioridad:** Media  
**Riesgo:** Mínimo. Es un cambio de texto en un archivo de configuración. No afecta el código en ejecución.

**Dependencias:** Ninguna.

**Estrategia de validación:**
1. En el entorno de desarrollo, ejecutar `pip freeze` y registrar las versiones exactas instaladas actualmente.
2. Reemplazar `openai>=1.0.0` por `openai==<versión-exacta-actual>` y equivalente para `python-dotenv`.
3. Reconstruir el contenedor desde cero (`docker build --no-cache`) y verificar que se instalan exactamente las versiones especificadas.
4. Ejecutar suite de humo completa.

**Estrategia de rollback:** Revertir `requirements.txt`. Sin impacto en el entorno en ejecución.

**Archivo:** `backend/requirements.txt`

---

## WAVE 3 — CALIDAD + USABILIDAD

> **Ventana de ejecución:** Días 22-42 (3 semanas)  
> **Prerequisito:** Wave 2 completado. Suite de humo pasando.

---

### M3-01 — Tests de integración HTTP

**Objetivo:** Crear tests que ejerciten los endpoints de la API a través de la capa HTTP completa (serialización, autenticación, validación, repositorio).

**Justificación:** Los tests unitarios actuales cubren entidades de dominio pero no la capa de adaptadores (vistas, serializers, URLs). Un bug en un serializer, en el decorator `@auth_required`, o en el mapeo de excepciones a HTTP status codes pasaría invisible hasta llegar a producción.

**Prioridad:** Media  
**Riesgo:** Nulo para el sistema en producción. Los tests son solo lectura del código; no modifican comportamiento.

**Dependencias:** M0-01, M0-02 (los flujos deben funcionar para que los tests sean válidos).

**Cobertura mínima propuesta:**
```
- POST /api/auth/login/          → 200, 401, 423
- POST /api/auth/register/       → 201, 400
- POST /api/competencia/create/  → 201, 400, 401, 403
- GET  /api/competencia/all/     → 200
- POST /torneo/<id>/inscribir/   → 201, 400, 403
- POST /partido/<id>/resultado/  → 200, 400, 404
```

**Estrategia de validación:**
1. Usar `APITestCase` de DRF con una BD de test separada (Django crea y destruye automáticamente).
2. Los tests no deben depender de datos externos ni de OpenRouter (mockear con `unittest.mock.patch`).
3. Objetivo mínimo: los 5 flujos de la suite de humo cubiertos como tests automatizados.
4. Integrar en `python manage.py test` existente.

**Estrategia de rollback:** Los tests son archivos nuevos; eliminarlos no afecta producción.

**Archivos:** Nuevos en `authentication/tests/`, `competencia/tests/`

---

### M3-02 — Configurar `coverage.py`

**Objetivo:** Medir el porcentaje de código cubierto por los tests y establecer un umbral mínimo de 60%.

**Justificación:** Sin medición, no hay forma de saber si los tests que existen realmente cubren los flujos críticos. Coverage proporciona la señal objetiva necesaria para priorizar futuros tests.

**Prioridad:** Media  
**Riesgo:** Nulo para producción.

**Dependencias:** M3-01 (más tests = medición más útil).

**Estrategia de validación:**
1. Instalar `coverage` y `pytest-cov` en `requirements-dev.txt`.
2. Crear `.coveragerc` excluyendo migraciones, `__init__.py` y archivos de configuración.
3. Ejecutar `coverage run manage.py test && coverage report`.
4. Objetivo inicial: 60%. Bloquear merges futuros que bajen la cobertura.

**Estrategia de rollback:** Eliminar los archivos de configuración. Sin impacto en producción.

**Archivos:** `.coveragerc`, `requirements-dev.txt`

---

### M3-03 — Corregir validación de estado en `GenerateFixturesUseCase`

**Objetivo:** Reemplazar el `pass` en la validación de estado del torneo por una excepción que rechace la operación si el torneo no está en estado `REGISTRATION_CLOSED`.

**Justificación:** Actualmente es posible llamar a `generar-fixtures` desde cualquier estado del torneo (DRAFT, IN_PROGRESS, FINALIZED), lo que puede generar fixtures duplicados o inconsistentes en torneos que ya están en progreso.

**Prioridad:** Media  
**Riesgo:** Bajo. El cambio solo agrega una restricción que antes no existía. El riesgo es bloquear un uso no documentado que algún usuario estuviera haciendo (poco probable en producción normal).

**Dependencias:** M0-01, M0-02.

**Estrategia de validación:**
1. Definir la excepción a lanzar (por ejemplo, `InvalidTournamentStateError` con HTTP 409).
2. Escribir un test que intente generar fixtures en un torneo en estado DRAFT y verifique que recibe 409.
3. Escribir un test que genere fixtures en estado REGISTRATION_CLOSED y verifique que funciona.
4. Ejecutar suite de humo — el Flujo 3 usa exactamente el estado correcto.

**Estrategia de rollback:** Revertir el cambio. El `pass` original no genera ningún error (la generación continúa como antes).

**Archivo:** `competencia/application/use_cases/generate_fixtures_use_case.py:23`

---

### M3-04 — Corregir iteración en `ConfigKnockout.validate_for_start()`

**Objetivo:** Reemplazar `range(1, n)` por una verificación correcta de potencia de 2.

**Justificación:** La validación actual puede retornar `True` o `False` erróneamente según el número de equipos, lo que permite iniciar torneos Knockout con configuraciones inválidas (e.g., 6 equipos sin byes calculados) o rechaza configuraciones válidas (e.g., 8 equipos en ciertos rangos).

**Prioridad:** Media  
**Riesgo:** Bajo. Cambio puntual en lógica de validación. El riesgo es rechazar un inicio de torneo que antes se aceptaba (comportamiento más correcto, no más permisivo).

**Dependencias:** M0-01, M0-02.

**Estrategia de validación:**
1. Escribir tests parametrizados: [4, 8, 16, 32, 64] deben retornar True; [5, 6, 7, 9, 10] deben retornar False.
2. Usar la verificación matemática estándar: `n > 0 and (n & (n - 1)) == 0`.
3. Verificar que los tests de fixtures existentes siguen pasando.

**Estrategia de rollback:** Revertir el cambio. La validación vuelve al comportamiento anterior (impreciso).

**Archivo:** `competencia/domain/entities/config_knockout.py:51`

---

### M3-05 — Generar especificación OpenAPI con `drf-spectacular`

**Objetivo:** Auto-generar documentación de API en formato OpenAPI 3.0 y servirla en `/api/schema/swagger-ui/`.

**Justificación:** La documentación actual es manual (archivos Markdown) y puede quedar desactualizada. Una especificación auto-generada desde el código es siempre fiel al contrato real de la API, facilita integraciones de terceros y reduce el onboarding de nuevos desarrolladores.

**Prioridad:** Media  
**Riesgo:** Mínimo. `drf-spectacular` es una librería aditiva. Las rutas nuevas (`/api/schema/`, `/api/schema/swagger-ui/`) no interfieren con las existentes.

**Dependencias:** M2-04 (la dependencia debe estar pineada antes de agregar más).

**Estrategia de validación:**
1. Instalar `drf-spectacular` con versión exacta.
2. Agregar a `INSTALLED_APPS` y `REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS']`.
3. Añadir las URLs de schema al `urlconf` principal.
4. Navegar a `/api/schema/swagger-ui/` y verificar que los endpoints existentes aparecen.
5. Verificar que los endpoints de auth requieren Bearer token en la UI.
6. Verificar que agregar la librería no impacta el tiempo de respuesta de otros endpoints.

**Estrategia de rollback:** Eliminar de `INSTALLED_APPS`, `requirements.txt` y URLs. Sin impacto en funcionalidad existente.

**Archivos:** `backend/league/settings.py`, `backend/league/urls.py`, `requirements.txt`

---

### M3-06 — Validación reactiva en formularios frontend

**Objetivo:** Activar validaciones en tiempo real (on blur / on change) en los formularios de registro de usuario, creación de torneo e inscripción de equipo.

**Justificación:** Actualmente los errores de validación solo se muestran al enviar el formulario (on submit). React Hook Form ya está integrado; solo falta configurar el `mode: "onChange"` o `mode: "onBlur"` y añadir las reglas de validación faltantes.

**Prioridad:** Media  
**Riesgo:** Mínimo para el backend (es cambio puramente de frontend). Riesgo bajo de UX regresión si una validación nueva es demasiado restrictiva.

**Dependencias:** Ninguna técnica.

**Estrategia de validación:**
1. Cambiar `useForm({ mode: "onBlur" })` en los formularios identificados.
2. Agregar reglas: email formato, contraseña longitud/complejidad, fechas (inicio < fin).
3. Verificar que los mensajes de error aparecen al salir de un campo inválido.
4. Verificar que no se puede enviar el formulario con campos inválidos.
5. Verificar que el flujo de envío exitoso sigue funcionando (no hay validaciones que bloqueen datos correctos).

**Estrategia de rollback:** Revertir el `mode` y las reglas añadidas. El formulario retorna a validación on-submit.

**Archivos:** Componentes de formulario en `frontend/src/`

---

### M3-07 — Modales de confirmación en acciones destructivas

**Objetivo:** Añadir un modal de confirmación antes de ejecutar acciones irreversibles: cancelar torneo, rechazar equipo, eliminar criterios.

**Justificación:** Un clic accidental en "Cancelar torneo" durante un evento en vivo no tiene recuperación. La fricción añadida por un modal es mínima para el usuario pero crítica para prevenir errores operativos.

**Prioridad:** Media  
**Riesgo:** Mínimo. Es un cambio puramente de UI que intercepta el evento de clic antes de llamar a la API. No modifica el backend.

**Dependencias:** Ninguna técnica.

**Estrategia de validación:**
1. Usar el componente `AlertDialog` de Radix UI (ya instalado en el proyecto).
2. Implementar en los 3 puntos de mayor riesgo: cancelar torneo, rechazar equipo, eliminar criterio IA.
3. Verificar que al confirmar se ejecuta la acción correctamente.
4. Verificar que al cancelar el modal no se realiza ninguna llamada a la API.

**Estrategia de rollback:** Revertir los componentes afectados. La acción retorna a ejecución directa al clic.

---

### M3-08 — Activar verificación de email en flujo de login

**Objetivo:** Hacer que el estado `NOT_VERIFIED` del usuario tenga efecto real en el login, retornando HTTP 403 con mensaje que indique verificación pendiente.

**Justificación:** El dominio ya tiene el concepto modelado correctamente. No aplicarlo en el flujo de login significa que usuarios registrados sin verificar email tienen acceso completo, lo que puede comprometer la integridad de los datos de torneos y equipos.

**Prioridad:** Media  
**Riesgo:** Alto si hay usuarios en producción con estado `NOT_VERIFIED` que actualmente pueden acceder. **Este cambio requiere una migración previa de datos o un mecanismo de reenvío de verificación antes de activarse.**

**Plan de implementación segura:**
1. **Fase A (sin impacto):** Agregar endpoint `POST /api/auth/resend-verification/` que genera y envía un token.
2. **Fase B (comunicación):** Notificar a usuarios existentes con `NOT_VERIFIED` que deben verificar su email antes de la fecha X.
3. **Fase C (activación):** En `LoginUseCase`, agregar check: `if user.state == UserState.NOT_VERIFIED → raise EmailNotVerified`.

**Dependencias:** Infraestructura de email (SMTP configurado).

**Estrategia de validación:**
1. Verificar que usuarios con estado `ACTIVE` siguen pudiendo hacer login (no regresión).
2. Verificar que un usuario `NOT_VERIFIED` recibe HTTP 403 con mensaje claro en la Fase C.
3. Verificar el flujo completo de verificación: registro → email → clic en link → estado pasa a ACTIVE → login exitoso.

**Estrategia de rollback (por fase):**
- Fase A: Eliminar el endpoint (sin impacto en login).
- Fase B: Sin código que revertir.
- Fase C: Revertir el check en `LoginUseCase`. Usuarios con `NOT_VERIFIED` vuelven a poder acceder.

**Archivos:** `authentication/application/use_cases/login_use_case.py`, nuevo `resend_verification_use_case.py`

---

## WAVE 4 — ESCALABILIDAD + OBSERVABILIDAD

> **Ventana de ejecución:** Días 43-90 (7 semanas)  
> **Prerequisito:** Wave 3 completado. Suite de humo pasando. Coverage > 60%.

---

### M4-01 — Estrategia de backup de PostgreSQL

**Objetivo:** Configurar backups automáticos diarios de la base de datos con retención de 7 días.

**Justificación:** Sin backups, cualquier fallo de disco, error de migración o eliminación accidental de datos es irreversible. Para un sistema que gestiona torneos con datos de participantes y resultados, la pérdida de datos tiene impacto directo en los usuarios.

**Prioridad:** Media  
**Riesgo:** Mínimo. El proceso de backup (`pg_dump`) no bloquea la BD en PostgreSQL moderno.

**Dependencias:** Acceso a infraestructura de almacenamiento (volumen Docker o almacenamiento externo).

**Estrategia de validación:**
1. Configurar un script `backup.sh` que ejecute `pg_dump` y guarde el archivo en un volumen montado.
2. Añadir el script como un servicio `backup` en `docker-compose.yml` con `restart: unless-stopped` y cron interno.
3. Verificar que el backup se genera correctamente restaurándolo en un contenedor temporal.
4. Documentar el proceso de restauración en el README.

**Estrategia de rollback:** Detener el servicio de backup. Los datos existentes no se ven afectados.

---

### M4-02 — Fallback para dependencia OpenRouter

**Objetivo:** Implementar una respuesta degradada cuando OpenRouter no está disponible, en lugar de retornar HTTP 500 al usuario.

**Justificación:** Los endpoints `/api/ia/analizar` y `/api/simulacion/torneo/<id>/simular/` tienen dependencia directa de una API externa. Una caída de OpenRouter hace que funciones centrales del sistema fallen con 500, impactando a usuarios que estén en medio de un torneo.

**Prioridad:** Media  
**Riesgo:** Bajo. El fallback es código aditivo que solo se activa cuando OpenRouter falla.

**Dependencias:** M1-03 (logging necesario para registrar los fallos de OpenRouter).

**Estrategia de validación:**
1. En el cliente de OpenRouter, añadir `try/except` con timeout de 10 segundos.
2. En caso de excepción, retornar una respuesta degradada con HTTP 200 y un flag `"ia_disponible": false` en el JSON.
3. El frontend debe mostrar un toast informativo: "El análisis de IA no está disponible temporalmente. Puede continuar con configuración manual."
4. Simular la caída desconectando la red del contenedor y verificar que el usuario recibe el mensaje degradado en lugar de un error 500.

**Estrategia de rollback:** Revertir los try/except. El comportamiento retorna a propagar el error.

---

### M4-03 — Conectar `AIRecommendations` a rutas de navegación

**Objetivo:** Registrar la página `AIRecommendations` en el router de React y añadirla al Sidebar para los roles que deben verla (MANAGER, ADMIN).

**Justificación:** El componente existe en el código pero no está conectado a ninguna ruta ni enlace de navegación. Los usuarios no tienen forma de acceder a él, haciendo que el trabajo ya realizado en frontend sea inaccesible.

**Prioridad:** Baja  
**Riesgo:** Mínimo. Es un cambio de routing y navegación que no toca lógica de negocio.

**Dependencias:** Verificar que el componente `AIRecommendations` llama a endpoints que ya existen y funcionan.

**Estrategia de validación:**
1. Agregar la ruta `/torneos/:id/recomendaciones` al router de React.
2. Añadir el enlace en el Sidebar bajo `<RoleGuard roles={[SystemRol.MANAGER, SystemRol.ADMIN]}>`.
3. Navegar a la ruta y verificar que el componente renderiza sin errores de consola.
4. Verificar que los roles sin permiso no ven el enlace y reciben 403 si intentan acceder directamente.

**Estrategia de rollback:** Eliminar la ruta y el enlace del Sidebar. El componente vuelve a ser inaccesible.

---

### M4-04 — Versionamiento del modelo XGBoost

**Objetivo:** Implementar un esquema simple de versionamiento del modelo de predicción que permita saber qué versión está en uso y revertir a versiones anteriores.

**Justificación:** El modelo XGBoost actual es un archivo único sin historial. Si se entrena y despliega un nuevo modelo con peor rendimiento, no hay forma de volver al anterior. El versionamiento es la base para un pipeline de ML responsable.

**Prioridad:** Baja  
**Riesgo:** Mínimo si se implementa como capa sobre el archivo existente sin cambiar la interfaz del `PredictionModel`.

**Dependencias:** Ninguna técnica.

**Estrategia de validación:**
1. Renombrar el archivo de modelo a `model_v1.pkl` y crear un archivo `model_current.txt` con el valor `v1`.
2. El `PredictionModel` lee `model_current.txt` para saber qué archivo cargar.
3. Verificar que las predicciones siguen funcionando con el mismo modelo.
4. Documentar el proceso para entrenar un `model_v2.pkl` y actualizar `model_current.txt`.

**Estrategia de rollback:** Revertir `model_current.txt` al valor anterior. El modelo retorna a la versión previa sin reinstalar nada.

---

## RIESGOS DE EJECUCIÓN DEL PLAN

### Riesgos generales del plan

| ID | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| RE-01 | Wave 0 desplegado sin testear en staging primero | Media | Alto | Obligatorio: probar en un ambiente espejo antes de producción |
| RE-02 | Cambio de SECRET_KEY accidental (rotar la clave, no solo moverla) | Baja | Crítico | Verificar en `.env` que la clave es **idéntica** a la actual antes de desplegar |
| RE-03 | Rate limiting demasiado agresivo bloquea usuarios en NAT compartido | Media | Alto | Comenzar con 20/min; ajustar según métricas reales de uso |
| RE-04 | Paginación rompe frontend si no se coordina con equipo frontend | Alta | Alto | Implementar como opt-in primero; no hacer obligatorio hasta que frontend soporte |
| RE-05 | M3-08 (verificación de email) bloquea usuarios activos con NOT_VERIFIED | Media | Alto | Ejecutar siempre en Fase A → B → C con comunicación previa |
| RE-06 | Índices CONCURRENTLY fallan en tabla con alta carga | Baja | Medio | Ejecutar en ventana de bajo tráfico; CONCURRENTLY puede reintentarse |
| RE-07 | Tests de integración (M3-01) revelan bugs adicionales no documentados | Alta | Medio | Es el objetivo; los bugs nuevos se agregan al backlog, no bloquean el plan |

### Orden de ejecución dentro de cada Wave

```
Wave 0:  M0-03 → M0-04 → M0-05 → M0-01 → M0-02
         (Seguridad primero, bugs de dominio después — ambos en el mismo deploy)

Wave 1:  M1-01 → M1-03 → M1-02 → M1-04
         (Infraestructura y observabilidad antes de agregar dependencias)

Wave 2:  M2-04 → M2-03 → M2-01 → M2-02
         (Pinear dependencias primero, luego migración BD, funcionalidad, paginación)

Wave 3:  M3-01 → M3-02 → M3-03 → M3-04 → M3-05 → M3-06 → M3-07 → M3-08
         (Tests primero para tener red de seguridad; correcciones de bugs con esa red)

Wave 4:  M4-01 → M4-02 → M4-03 → M4-04
         (Backup como primera prioridad operacional; resto en cualquier orden)
```

---

## CRITERIOS DE DONE POR WAVE

### Wave 0 — Done cuando:
- [ ] `python manage.py test` pasa (incluye test de regresión M0-01)
- [ ] `docker compose up` arranca sin errores
- [ ] Flujo 1, 2 y 3 de la suite de humo pasan manualmente
- [ ] `git log --oneline` muestra commits atómicos con mensaje descriptivo para cada corrección
- [ ] SECRET_KEY no aparece en ningún archivo versionado (`git grep SECRET_KEY` retorna solo `settings.py` con `os.environ.get`)

### Wave 1 — Done cuando:
- [ ] `docker compose up` tras `docker compose down` muestra `backend healthy` en logs
- [ ] `POST /api/auth/login/` más de 20 veces en 1 minuto retorna HTTP 429
- [ ] Un error 500 forzado aparece en el archivo de log configurado
- [ ] Generación de fixtures con fallo simulado en la mitad no deja partidos huérfanos en BD

### Wave 2 — Done cuando:
- [ ] `GET /api/competencia/all/?page=1&page_size=5` retorna estructura paginada
- [ ] `EXPLAIN ANALYZE` en las queries críticas muestra Index Scan (no Seq Scan)
- [ ] Tabla de posiciones muestra posiciones correctas tras registrar 6 resultados en torneo Round-Robin de 4 equipos
- [ ] `pip install -r requirements.txt` en contenedor limpio instala exactamente las versiones especificadas

### Wave 3 — Done cuando:
- [ ] `python manage.py test` ejecuta tests de integración HTTP sin fallos
- [ ] `coverage report` muestra ≥ 60% de cobertura
- [ ] Swagger UI disponible en `/api/schema/swagger-ui/`
- [ ] Intentar generar fixtures en torneo en estado DRAFT retorna HTTP 409
- [ ] Formulario de registro muestra error de validación al salir de campo con email inválido (sin enviar)
- [ ] Modal de confirmación aparece al hacer clic en "Cancelar torneo"

### Wave 4 — Done cuando:
- [ ] Script de backup genera archivo `.sql` válido restaurable en contenedor vacío
- [ ] Desconectar red del contenedor backend hace que `/api/ia/analizar` retorne 200 con `"ia_disponible": false`
- [ ] Ruta `/torneos/:id/recomendaciones` renderiza sin errores para rol MANAGER
- [ ] `model_current.txt` existe y apunta a `model_v1.pkl`

---

## MÉTRICAS DE ÉXITO DEL PLAN COMPLETO

| Métrica | Baseline (hoy) | Objetivo tras Wave 4 |
|---|---|---|
| Puntaje FURPS+ global | 7.4 / 10 | ≥ 9.0 / 10 |
| Brechas críticas abiertas | 5 | 0 |
| Brechas mayores abiertas | 8 | 0 |
| Cobertura de tests | ~30% (solo unitarios de dominio) | ≥ 80% |
| Tiempo de respuesta `/all/` (1000 registros) | > 2s (estimado) | < 300ms |
| Incidentes de seguridad críticos | 3 activos (RS-01, RS-02, RS-03) | 0 |
| Disponibilidad con fallo de OpenRouter | 0% (500 inmediato) | 100% degradado |

---

*Plan generado a partir de `01_Auditoria_FURPS.md`.*  
*Herramienta: Claude Code — Arquitecto Senior FURPS+*  
*Fecha: 2026-06-12*
