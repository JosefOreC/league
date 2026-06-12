# EJECUCIÓN DEL PLAN FURPS+ — ZOIDS LEAGUE
**Versión:** 1.0  
**Fecha:** 2026-06-12  
**Rama:** Auditoria-Furps  
**Entrada:** `02_Plan_FURPS.md`  
**Principio rector:** EL SISTEMA YA FUNCIONA — ningún cambio rompe funcionalidad existente.

---

## RESUMEN

Se ejecutó el subconjunto **seguro, incremental y verificable** del plan: la totalidad de Wave 0 (crítico), la mayor parte de Wave 1 (confiabilidad base) y los ítems de bajo riesgo de Wave 2 y Wave 3 que no requieren infraestructura externa ni decisiones de despliegue.

Antes de modificar nada se **verificó cada hallazgo contra el código real**. Esto reveló que **2 hallazgos de la auditoría ya estaban resueltos** y que **1 hallazgo era un falso positivo**. No se modificó código que ya funcionaba correctamente.

| Estado | Cantidad | Mejoras |
|---|---|---|
| ✅ Ejecutado en esta sesión | 8 | M0-02, M0-03, M0-04, M1-01, M1-02, M1-03, M2-04, M3-02 |
| ✔️ Ya estaba resuelto (verificado) | 2 | M0-01, M0-05 |
| ⚠️ Falso positivo (no se toca) | 1 | M3-04 |
| ⏸️ Diferido (requiere infra/decisión) | resto | Ver sección "Diferido" |

---

## CAMBIOS EJECUTADOS

### ✅ M0-02 — Corrección de `set_es_bye()` → `set_bye()`  [CRÍTICO]
**Archivo:** `competencia/application/use_cases/generate_fixtures_use_case.py:108`  
**Cambio:** `match.set_es_bye(True)` → `match.set_bye(True)`  
**Verificación previa:** Confirmado bug real — la entidad `Match` solo expone `set_bye()` ([match.py:58](competencia/domain/entities/match.py#L58)). La llamada anterior producía `AttributeError` al generar cualquier fixture con byes (número de equipos que no es potencia de 2).  
**Validación:** Compilación sintáctica OK. Validación funcional pendiente en Docker (ver "Cómo validar").  
**Rollback:** `git revert` del commit; cambio de una línea sin efectos colaterales.

### ✅ M0-03 — `SECRET_KEY` y `DEBUG` leídos del entorno  [CRÍTICO]
**Archivo:** `config/settings.py`  
**Cambio:**
```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '<dev-insecure-default>')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() in ('true', '1', 'yes')
```
**Decisión de diseño (do-no-harm):** En lugar de fallar el arranque si la variable falta (como sugería el plan), se conserva un **valor por defecto de desarrollo** con prefijo `django-insecure-`. Esto:
- Elimina el riesgo de que la **clave de producción** viva en el código (producción la define vía `DJANGO_SECRET_KEY`).
- **No rompe** `manage.py test` ni el contenedor de desarrollo, que siguen funcionando sin configuración adicional.

**Validación:** Compila. El contenedor dev mantiene comportamiento idéntico (mismo valor por defecto).  
**Rollback:** `git revert`. Los tokens existentes siguen válidos (la clave por defecto no cambió).

### ✅ M0-04 — `ALLOWED_HOSTS` configurable por entorno  [CRÍTICO]
**Archivo:** `config/settings.py`  
**Cambio:** `ALLOWED_HOSTS` se construye desde `DJANGO_ALLOWED_HOSTS` (lista separada por comas).  
**Decisión de diseño (do-no-harm):** El valor por defecto es `'*'` (comportamiento actual). **Motivo:** el sistema puede estar desplegado bajo un dominio que no conozco; restringir a una lista adivinada **rompería producción**. La mejora entrega la *capacidad* de restringir vía entorno y se documenta como acción obligatoria de hardening en `.env.example`. La restricción efectiva es responsabilidad del operador que conoce sus dominios.  
**Rollback:** `git revert`. Sin impacto en sesiones ni datos.

### ✅ M1-01 — Healthchecks en Docker Compose  [ALTO]
**Archivo:** `docker-compose.yml`  
**Cambios:**
- `healthcheck` en servicio `db` con `pg_isready -U admin -d league_db`.
- `depends_on: db: condition: service_healthy` en `backend` (arranque ordenado).
- `healthcheck` en `backend` (comprueba que el puerto 8000 acepta conexiones).

**Validación:** Revisión manual de YAML (Docker no disponible en el entorno local de ejecución).  
**Rollback:** Eliminar los bloques `healthcheck` y restaurar `depends_on: - db`.

### ✅ M1-02 — `transaction.atomic` en generación de fixtures  [ALTO]
**Archivo:** `competencia/application/use_cases/generate_fixtures_use_case.py`  
**Cambio:** El bloque `delete_by_tournament` + bucle de `save` + `tournament.update` se envuelve en `with transaction.atomic():`. Si la inserción falla a mitad, no quedan partidos huérfanos ni el torneo en estado inconsistente.  
**Validación:** Compila. El comportamiento en el camino feliz es idéntico; solo cambia el comportamiento ante fallo (ahora consistente).  
**Rollback:** Quitar el `with transaction.atomic():` y el import.

### ✅ M1-03 — Logging estructurado  [ALTO]
**Archivo:** `config/settings.py`  
**Cambio:** Bloque `LOGGING` aditivo con handler de consola y nivel controlado por `LOG_LEVEL` (default WARNING). Captura errores 500 y excepciones que antes eran invisibles.  
**Validación:** Compila. Configuración puramente aditiva, no altera lógica de la aplicación.  
**Rollback:** Eliminar el bloque `LOGGING`.

### ✅ M2-04 — Acotar versiones mayores de dependencias  [MEDIO]
**Archivo:** `requirements.txt`  
**Cambio:** `openai>=1.0.0` → `openai>=1.0.0,<2.0.0`; `python-dotenv>=1.0.0` → `python-dotenv>=1.0.0,<2.0.0`.  
**Decisión de diseño:** Se usa cota superior de major en vez de pin exacto, porque no se puede ejecutar `pip freeze` en este entorno para conocer la versión exacta instalada. La cota previene el riesgo real (un salto de major con breaking changes) sin arriesgar un pin que no coincida con lo desplegado. El archivo se reescribió de **UTF-16 a UTF-8** (estándar para pip); todos los demás pins se preservaron exactos.  
**Rollback:** `git revert` de `requirements.txt`.

### ✅ M3-02 — Configuración de cobertura (`coverage.py`)  [MEDIO]
**Archivo nuevo:** `.coveragerc`  
**Cambio:** Configuración de cobertura con `fail_under=60`, excluyendo migraciones, tests y archivos de arranque. `coverage==7.13.5` **ya estaba** en `requirements.txt`, por lo que no se añadió dependencia.  
**Uso:** `coverage run manage.py test && coverage report`  
**Rollback:** Eliminar `.coveragerc`.

### Archivo de soporte creado
**`.env.example`** — documenta todas las variables de entorno del backend (DB, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `LOG_LEVEL`, `OPENROUTER_API_KEY`) con instrucciones de hardening para producción. Permitido por `.gitignore` (`!.env.example`).

---

## VERIFICACIONES QUE CAMBIARON EL PLAN

### ✔️ M0-01 — `Match.set_estado()` ya estaba corregido
El working tree ya tenía `self.__estado = value` (corrección de `==` a `=`) en [match.py:63](competencia/domain/entities/match.py#L63), sin commitear. No se requirió acción; queda incluido en este lote.

### ✔️ M0-05 — API key ya estaba fuera de docker-compose
[docker-compose.yml:49](docker-compose.yml#L49) ya usaba `OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}` (leída del entorno). La auditoría reflejaba un estado anterior; el commit `e1edcac` ya lo había resuelto. Sin acción.

### ⚠️ M3-04 — `ConfigKnockout.validate_for_start()` es un FALSO POSITIVO
La auditoría (HF-04) afirmaba que el `range(1, n)` era incorrecto. Se analizó la lógica real ([config_knockout.py:50-57](competencia/domain/value_objects/config_tournament/config_knockout.py#L50-L57)):
- count=4 → True · count=6 → raise · count=8 → True · count=16 → True · count=5 → raise.

La función **valida correctamente** que el número de equipos sea potencia de 2. No es elegante, pero es correcta. **No se modifica** código funcional (principio do-no-harm).

---

## DIFERIDO (requiere infraestructura, dependencias o decisión humana)

| Mejora | Motivo del diferimiento |
|---|---|
| **M1-04** Rate limiting | Requiere instalar `django-ratelimit` (no está en requirements). Aplicar el decorador con la librería ausente rompería los imports de las vistas de auth al arrancar. Debe hacerse junto con la instalación y rebuild del contenedor. |
| **M2-01** Completar `Standing` | Cambio funcional de tamaño medio que requiere definir el contrato exacto de desempates y TDD previo. Necesita validación con datos reales de un torneo. |
| **M2-02** Paginación | Riesgo Alto de romper el frontend (cambia la forma de la respuesta). Requiere coordinación con el equipo frontend e implementación opt-in. |
| **M2-03** Índices BD | Requiere migración con `CREATE INDEX CONCURRENTLY` ejecutada contra la BD real en ventana de bajo tráfico. |
| **M3-01** Tests de integración HTTP | Requiere entorno con BD de test (Postgres) para `APITestCase`. No ejecutable en este entorno local sin dependencias. |
| **M3-03** Validación de estado en fixtures | Cambio de comportamiento (de permisivo a estricto) que podría romper flujos de producción no documentados. Requiere confirmar con el dominio si se regeneran fixtures desde otros estados. |
| **M3-05** OpenAPI/Swagger | Requiere instalar `drf-spectacular` y rebuild. |
| **M3-06 / M3-07** UX frontend | Cambios de frontend (validación reactiva, modales) fuera del alcance de esta sesión backend. |
| **M3-08** Verificación de email | Requiere infraestructura SMTP y migración/comunicación previa a usuarios `NOT_VERIFIED` existentes. Alto riesgo de bloquear usuarios activos. |
| **Wave 4 completo** (M4-01..04) | Backup, fallback IA, routing frontend y versionado de modelo: requieren infraestructura de almacenamiento, decisiones operativas y trabajo de frontend. |

---

## CÓMO VALIDAR (en el entorno Docker del proyecto)

El entorno local de ejecución no tiene las dependencias Python instaladas (viven en el contenedor). La validación de runtime debe correrse en Docker:

```bash
# 1. Levantar el stack (verifica M1-01: backend espera a db healthy)
docker compose up --build

# 2. System check de Django (valida settings tras M0-03/M0-04/M1-03)
docker compose exec backend python manage.py check

# 3. Suite de tests + cobertura (valida M0-01/M0-02 y M3-02)
docker compose exec backend coverage run manage.py test
docker compose exec backend coverage report

# 4. Suite de humo manual (flujos críticos del plan):
#    Login → Crear torneo → Configurar reglas → Inscribir equipo →
#    Aprobar → Cerrar inscripciones → Generar fixtures (verifica M0-02) →
#    Registrar resultado (verifica M0-01) → Ver posiciones
```

### Validación ya realizada en esta sesión
- ✅ `py_compile` de los 3 archivos Python modificados → sin errores de sintaxis.
- ✅ Revisión manual de indentación y estructura de `docker-compose.yml`.
- ✅ Verificación de cada hallazgo contra el código fuente real antes de modificar.

---

## ACCIONES DE HARDENING PARA PRODUCCIÓN (operador)

Para que las mejoras de seguridad surtan efecto en producción, el operador debe definir en el entorno del contenedor:

```env
DJANGO_SECRET_KEY=<clave-única-generada>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<dominios-reales-separados-por-coma>
LOG_LEVEL=WARNING
```

Sin estas variables el sistema funciona igual que antes (compatibilidad hacia atrás), pero **no** queda endurecido. Esta es una decisión deliberada para no romper despliegues existentes.

---

*Reporte de ejecución generado a partir de `02_Plan_FURPS.md`.*  
*Herramienta: Claude Code — Arquitecto Senior FURPS+*  
*Fecha: 2026-06-12*
