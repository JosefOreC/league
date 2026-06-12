# AUDITORÍA DE IMPLEMENTACIÓN FURPS+ — ZOIDS LEAGUE
**Versión:** 1.0  
**Fecha:** 2026-06-12  
**Rol:** Auditor Independiente de Implementación  
**Rama:** Auditoria-Furps  
**Entradas:** `01_Auditoria_FURPS.md`, `02_Plan_FURPS.md`, estado actual del working tree.  
**Método:** Verificación estática contra el código real (`git diff`, lectura de archivos, inspección de bytes, `py_compile`, `grep`). **No se asumió ninguna mejora como aplicada.**

> **Limitación de alcance declarada:** las dependencias Python (Django, dotenv, etc.) y Docker **no están instaladas en el entorno de auditoría**; viven en el contenedor. Por tanto **no fue posible ejecutar `manage.py test`, `manage.py check` ni `docker compose`**. Toda afirmación de runtime se marca como tal. La evidencia presentada es **estática y verificable** (números de línea, bytes, resultados de compilación sintáctica).

---

## RESUMEN DE CUMPLIMIENTO

| Veredicto | Mejoras |
|---|---|
| ✅ **Implementada** (evidencia confirmada) | M0-01, M0-02, M0-03, M0-04*, M0-05, M1-01†, M1-03, M3-02 |
| ⚠️ **Parcialmente implementada** | M1-02 (con incompatibilidad), **M2-04 (defecto de encoding — riesgo de build)** |
| ❌ **No implementada** (diferida, declarada en `03_Ejecucion_FURPS.md`) | M1-04, M2-01, M2-02, M2-03, M3-01, M3-03, M3-05, M3-06, M3-07, M3-08, Wave 4 |
| ⚠️ **Falso positivo correctamente NO modificado** | M3-04 |

`*` M0-04 implementada como *capacidad*; el hardening no es efectivo por defecto (ver detalle).  
`†` M1-01 verificada estáticamente (YAML); **sin verificación de runtime** (Docker no disponible).

**2 hallazgos independientes nuevos** que el reporte de ejecución (`03_Ejecucion_FURPS.md`) **no reporta o reporta de forma inexacta** (ver §"Regresiones y errores nuevos").

---

## 1. ESTADO DE CADA MEJORA (con evidencia)

### ✅ M0-01 — `Match.set_estado()` asigna correctamente
**Veredicto:** Implementada.  
**Evidencia:** [match.py:63-64](competencia/domain/entities/match.py#L63-L64)
```python
def set_estado(self, value):
    self.__estado = value      # antes: self.__estado == value
```
**Antes/después:** `==` (comparación sin efecto) → `=` (asignación). `git diff` confirma el cambio de 1 carácter. Corrección real.

### ✅ M0-02 — `set_es_bye()` → `set_bye()`
**Veredicto:** Implementada.  
**Evidencia:** [generate_fixtures_use_case.py:114](competencia/application/use_cases/generate_fixtures_use_case.py#L114) ahora llama `match.set_bye(True)`.  
**Verificación de regresión:** `grep set_es_bye` sobre todos los `*.py` → **0 coincidencias**. No quedan otros call-sites rotos. El método `set_bye` existe en [match.py:58](competencia/domain/entities/match.py#L58). Confirmada la eliminación total del `AttributeError`.

### ✅ M0-03 — `SECRET_KEY` y `DEBUG` desde entorno
**Veredicto:** Implementada.  
**Evidencia:** [settings.py:24-40](config/settings.py#L24-L40)
```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-...')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() in ('true', '1', 'yes')
```
**Observación de auditor:** la clave de desarrollo permanece como *fallback* en el código. El riesgo de "clave de producción en el repositorio" se elimina **solo si** el operador define `DJANGO_SECRET_KEY` en producción. La capacidad está correctamente implementada; la efectividad depende de configuración externa (documentada en `.env.example`).

### ⚠️→✅ M0-04 — `ALLOWED_HOSTS` configurable
**Veredicto:** Implementada como *capacidad* — **hardening NO efectivo por defecto**.  
**Evidencia:** [settings.py:42-45](config/settings.py#L42-L45)
```python
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',') if h.strip()]
```
**Antes/después:** `["*"]` fijo → `["*"]` por defecto, configurable por entorno.  
**Observación de auditor:** el valor por defecto sigue siendo `*`. La vulnerabilidad RS-02 (Host Header Injection) **permanece abierta** salvo que el operador defina `DJANGO_ALLOWED_HOSTS`. Es una decisión consciente de compatibilidad (documentada), pero el riesgo de seguridad **no queda mitigado por el código por sí solo**. Riesgo residual: ver §3.

### ✅ M0-05 — API key fuera de docker-compose
**Veredicto:** Implementada (preexistente, no atribuible a esta sesión).  
**Evidencia:** [docker-compose.yml:49](docker-compose.yml#L49) → `OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}`. Confirmado que ya estaba resuelto en commit previo; el reporte de ejecución lo declara correctamente.

### ✅ M1-01 — Healthchecks en Docker Compose
**Veredicto:** Implementada (verificación estática) — **runtime NO verificado**.  
**Evidencia:** [docker-compose.yml:21-27](docker-compose.yml#L21-L27) (healthcheck `db` con `pg_isready`), [docker-compose.yml:51-63](docker-compose.yml#L51-L63) (`depends_on: db: condition: service_healthy` + healthcheck `backend`).  
**Verificación:** estructura e indentación YAML revisadas manualmente y consistentes. **No se pudo ejecutar `docker compose config`** (Docker ausente), por lo que la validez semántica del compose y el funcionamiento real de los healthchecks **quedan sin verificar en runtime**.

### ⚠️ M1-02 — `transaction.atomic` en generación de fixtures
**Veredicto:** Parcialmente implementada — **funcionalmente presente, con incompatibilidad introducida**.  
**Evidencia (positiva):** [generate_fixtures_use_case.py:48-58](competencia/application/use_cases/generate_fixtures_use_case.py#L48-L58) — `delete + save loop + update` envueltos en `with transaction.atomic():`. Import en [línea 9](competencia/application/use_cases/generate_fixtures_use_case.py#L9). Compila (`py_compile` OK).  
**Hallazgo de auditor (incompatibilidad):** el import `from django.db import transaction` **acopla la capa de aplicación (use case) al runtime de Django**. Consecuencias verificables:
1. **Violación de arquitectura hexagonal:** un use case del dominio de aplicación ahora depende de la infraestructura ORM. El plan original (02) pedía esto explícitamente, pero el lugar arquitectónicamente correcto sería el repositorio o un `UnitOfWork` (que el propio `01_Auditoria` señala como "declarado en ports, implementación incompleta").
2. **Impacto en pruebas unitarias:** el test existente `test_fixtures_and_standings.py` instancia el use case con **mocks** y lo ejecuta como `unittest` puro. `transaction.atomic()` requiere una conexión de BD configurada por Django. Bajo `manage.py test` funciona; bajo `python -m unittest` aislado, fallaría. (Nota: este test ya falla por otra causa preexistente — ver §2.)

### ✅ M1-03 — Logging estructurado
**Veredicto:** Implementada.  
**Evidencia:** [settings.py:173-207](config/settings.py#L173-L207) — bloque `LOGGING` con handler `console`, formateador `verbose` y nivel por `LOG_LEVEL` (default `WARNING`). Configuración aditiva; `py_compile` OK.

### ⚠️ M2-04 — Acotar versiones de dependencias
**Veredicto:** Parcialmente implementada — **contenido correcto, ENCODING DEFECTUOSO (regresión potencial de build)**.  
**Evidencia (positiva):** decodificado como UTF-16, `requirements.txt` contiene `openai>=1.0.0,<2.0.0` y `python-dotenv>=1.0.0,<2.0.0`. Los demás pins se preservaron. El objetivo funcional (cota de *major*) **sí se cumplió**.  
**Evidencia (defecto) — CRÍTICA:**
```
$ python -c "d=open('requirements.txt','rb').read(); print(len(d), d[:4].hex())"
836  61007300        # 'a','s' en UTF-16 LE  →  el archivo NO es UTF-8
BOM UTF-16 LE (fffe)? False     # ¡y además ya NO tiene BOM!
```
- El reporte `03_Ejecucion_FURPS.md` afirma: *"El archivo se reescribió de UTF-16 a UTF-8"*. **La evidencia lo contradice:** el archivo quedó en **UTF-16 LE SIN BOM**.
- El original era **UTF-16 LE CON BOM** (`FF FE`). pip decodifica `requirements.txt` con `auto_decode`, que detecta el encoding **por el BOM**. Al perderse el BOM, pip intentará decodificar bytes UTF-16 como UTF-8/locale → lectura con bytes nulos → **`pip install -r requirements.txt` puede fallar al construir la imagen**.
- **Esto es una regresión introducida por la ejecución**, más grave que la brecha original (dependencias sin pin). Ver §3 (riesgo residual prioritario).

### ✅ M3-02 — Configuración de cobertura
**Veredicto:** Implementada.  
**Evidencia:** archivo nuevo [.coveragerc](.coveragerc) con `fail_under=60` y exclusiones. `coverage==7.13.5` ya presente en `requirements.txt`. No se añadió dependencia. Correcto.

### ⚠️ M3-04 — `ConfigKnockout.validate_for_start()` (falso positivo)
**Veredicto:** Correctamente **NO modificada**.  
**Evidencia:** `git diff` no muestra cambios en [config_knockout.py](competencia/domain/value_objects/config_tournament/config_knockout.py). Verificación independiente de la lógica `range(1, n)`: para count ∈ {4,8,16}→`True`; {5,6,7}→`raise`. La función valida potencias de 2 correctamente. El auditor confirma que **HF-04 del informe 01 era un falso positivo** y que la decisión de no tocar código funcional fue correcta (principio do-no-harm respetado).

### ❌ Mejoras NO implementadas (diferidas)
**Veredicto:** No implementadas — declaradas explícitamente como diferidas en `03_Ejecucion_FURPS.md` con justificación.  
**Verificación independiente (muestreo):**
- **M1-04 (rate limiting):** `grep ratelimit` → 0 coincidencias en código. `django-ratelimit` ausente de `requirements.txt`. Confirmado no implementado.
- **M2-02 (paginación):** sin `PageNumberPagination` ni `REST_FRAMEWORK` con paginación en settings. Confirmado.
- **M3-05 (Swagger):** sin `drf-spectacular`. Confirmado.
- **M3-08 (verificación email):** `LoginUseCase` no consultado en esta sesión, pero ausencia de endpoint `resend-verification` confirmada.
Estas exclusiones son **transparentes y consistentes** con el reporte de ejecución; no constituyen incumplimiento oculto.

---

## 2. REGRESIONES, FUNCIONALIDADES ROTAS Y PRUEBAS FALLIDAS

### 🔴 R-01 — `requirements.txt` en UTF-16 sin BOM (regresión introducida)
Detallado en M2-04. **Severidad: Alta.** Puede romper la construcción de la imagen Docker (`pip install`). Es el hallazgo más accionable de esta auditoría.

### 🟠 R-02 — Acoplamiento Django en capa de aplicación (incompatibilidad de pruebas)
Detallado en M1-02. El use case ahora requiere contexto de BD de Django incluso en pruebas con mocks. **Severidad: Media.**

### 🟡 P-01 — Prueba PREEXISTENTE rota (no es regresión, pero invalida claims de "tests pasan")
**Hallazgo independiente, no atribuible a esta sesión, pero relevante:** el test `test_fixtures_and_standings.py` **ya estaba roto antes del plan**.
**Evidencia estática (TypeError garantizado):**
- [test_fixtures_and_standings.py:16](competencia/test/application/test_fixtures_and_standings.py#L16):
  ```python
  self.generate_use_case = GenerateFixturesUseCase(self.match_repo, self.tournament_repo)  # 2 args
  ```
- El constructor exige **3** argumentos ([generate_fixtures_use_case.py:13](competencia/application/use_cases/generate_fixtures_use_case.py#L13)):
  ```python
  def __init__(self, match_repository, tournament_repository, team_repository):
  ```
  → `TypeError: __init__() missing 1 required positional argument: 'team_repository'` en `setUp` → **el test falla siempre**.
- Adicional: [test_fixtures_and_standings.py:37](competencia/test/application/test_fixtures_and_standings.py#L37) verifica `tournament_mock.update_state.assert_called_with(...)`, pero `execute()` llama `self.__tournament_repository.update(tournament)`, **no** `tournament.update_state(...)`. Aserción desalineada con la implementación.

**Implicación de auditoría:** las afirmaciones de validación ("compila", "los tests existentes pasan") en `01` y `03` **no pueden sustentarse** para este test: existe pero está roto desde antes. La ejecución del plan **no añadió** la prueba de regresión para M0-01/M0-02 que el propio `02_Plan_FURPS.md` (M0-01, M1-02) recomendaba.

### Verificación de NO-regresión en lo demás
- `py_compile` de `settings.py`, `generate_fixtures_use_case.py`, `match.py` → **sin errores de sintaxis**.
- Tests de dominio (`test_tournament.py`, `test_user.py`, `test_team.py`, `test_institution.py`, `test_tournament_team.py`, `test_create_tournament_use_case.py`, `test_tournament_logic.py`) **no fueron tocados** por los cambios y no dependen de los archivos modificados → sin regresión introducida en ellos (verificación por aislamiento, no por ejecución).

---

## 3. RIESGOS RESIDUALES

| ID | Riesgo | Severidad | Origen | Estado |
|---|---|---|---|---|
| RR-01 | `requirements.txt` UTF-16 sin BOM puede romper `pip install` en el build | 🔴 Alta | **Introducido por la ejecución (M2-04)** | **ABIERTO — requiere remediación inmediata** |
| RR-02 | `ALLOWED_HOSTS` sigue siendo `*` por defecto; RS-02 sin mitigar salvo config del operador | 🟠 Alta | M0-04 (decisión de compatibilidad) | Mitigable solo vía entorno |
| RR-03 | `SECRET_KEY` de dev permanece como fallback; RS-01 sin mitigar salvo config del operador | 🟠 Alta | M0-03 (decisión de compatibilidad) | Mitigable solo vía entorno |
| RR-04 | `transaction.atomic` acopla aplicación↔Django; rompe ejecución unit-test aislada | 🟡 Media | M1-02 | Funcional bajo `manage.py test` |
| RR-05 | M1-01 healthchecks sin verificación de runtime (Docker ausente) | 🟡 Media | Limitación de entorno | Verificar al desplegar |
| RR-06 | Test `test_fixtures_and_standings.py` roto (preexistente) enmascara fallos de fixtures | 🟡 Media | Preexistente | No corregido por el plan |
| RR-07 | Sin ejecución real de suite de tests ni `manage.py check` | 🟡 Media | Limitación de entorno | Pendiente en Docker |

---

## 4. COMPARACIÓN ANTES / DESPUÉS (consolidada)

| Archivo | Antes | Después | Veredicto |
|---|---|---|---|
| `match.py` | `self.__estado == value` | `self.__estado = value` | ✅ Corregido |
| `generate_fixtures_use_case.py` | `set_es_bye()`, persistencia sin transacción | `set_bye()`, `with transaction.atomic()` | ✅/⚠️ Corregido con acoplamiento |
| `config/settings.py` | `SECRET_KEY` fijo, `DEBUG=False`, `ALLOWED_HOSTS=["*"]`, sin LOGGING | env-driven + `LOGGING` | ✅ Implementado (hardening opt-in) |
| `docker-compose.yml` | sin healthchecks, `depends_on: -db` | healthchecks + `condition: service_healthy` | ✅ Estático (runtime sin verificar) |
| `requirements.txt` | UTF-16+BOM, `openai>=1.0.0`, `dotenv>=1.0.0` | **UTF-16 sin BOM**, pins acotados | ⚠️ Contenido OK / encoding roto |
| `.coveragerc` | inexistente | creado (`fail_under=60`) | ✅ Implementado |
| `.env.example` | inexistente | creado | ✅ Implementado |
| `config_knockout.py` | (correcto) | (sin cambios) | ✅ Correctamente intacto |

---

## 5. CONCLUSIÓN DE CUMPLIMIENTO

**Cumplimiento del plan: PARCIAL-ALTO con un defecto accionable.**

De las mejoras que el plan marcó para ejecución inmediata (Wave 0 y Wave 1 + ítems seguros de Wave 2-3), **la mayoría están correctamente implementadas y respaldadas por evidencia estática**. Los bugs críticos de funcionalidad (M0-01, M0-02) están **genuinamente corregidos** y verificados (incluido el barrido que confirma cero call-sites rotos restantes). La disciplina de compatibilidad hacia atrás se respetó: los cambios de seguridad son *opt-in* y no rompen el comportamiento actual del contenedor.

Sin embargo, esta auditoría **no puede declarar cumplimiento total** por:

1. **Un defecto introducido (RR-01):** `requirements.txt` quedó en UTF-16 **sin BOM**, contradiciendo lo afirmado en el reporte de ejecución y arriesgando el build de la imagen. **Debe remediarse reescribiéndolo en UTF-8 real antes de cualquier despliegue.**
2. **Verificación de runtime ausente:** sin Django ni Docker en el entorno, **no se ejecutaron `manage.py test`, `manage.py check` ni `docker compose`**. La conformidad funcional de M1-01, M1-02 y de los flujos críticos **queda pendiente de validación en el contenedor**.
3. **Hardening de seguridad no efectivo por defecto (RR-02, RR-03):** RS-01 y RS-02 solo se mitigan si el operador define variables de entorno; el código por sí solo no cierra esas vulnerabilidades.
4. **Deuda de pruebas preexistente (P-01):** existe un test roto que el plan no corrigió ni reemplazó, lo que debilita la red de seguridad de regresión sobre la generación de fixtures.

**Recomendación del auditor (orden de prioridad):**
1. **Remediar RR-01 de inmediato:** reescribir `requirements.txt` en UTF-8 sin BOM y verificar `pip install -r requirements.txt` en un build limpio.
2. Ejecutar en Docker: `docker compose exec backend python manage.py check` y `coverage run manage.py test`, y registrar el resultado real.
3. Corregir el test preexistente roto (constructor de 3 args + aserción `update` vs `update_state`) y añadir la prueba de regresión de M0-01/M0-02.
4. Para producción: definir `DJANGO_SECRET_KEY` y `DJANGO_ALLOWED_HOSTS` (cerrar RR-02/RR-03).
5. Evaluar mover `transaction.atomic` a la capa de repositorio/`UnitOfWork` para resolver RR-04.

---

*Auditoría de implementación basada exclusivamente en evidencia observable del working tree de la rama `Auditoria-Furps`.*  
*Herramienta: Claude Code — Auditor Independiente FURPS+*  
*Fecha: 2026-06-12*
