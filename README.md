







# 1. Clonar el repo
git clone https://github.com/JosefOreC/league

# 2. Levantar todo el entorno
docker-compose up -d

# 3. Verificar los 3 contenedores corriendo
docker-compose ps
Muestra la salida de docker-compose ps con los tres servicios activos (postgres_db, django_backend, react_frontend) y señala que las migraciones corren automáticamente porque el comando del backend es:
command: sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
Explica las variables de entorno del docker-compose.yml: DB_NAME, DB_USER, DB_HOST que conectan el backend con PostgreSQL sin configuración manual.
3. Resolución de conflictos y pruebas funcionales
Qué mostrar: los conflictos que resolviste al hacer el merge y que el sistema funciona después.
Para la resolución de conflictos, muestra el historial git:
git log --oneline -5
Explica que al traer main hacia feature/frontend hubo conflictos porque main reorganizó toda la estructura del proyecto (de frontend/ a competencia/infrastructure/.../react/). Muestra el conflicto más representativo que resolviste en RegisterTeam.tsx: el campo tournament.nombre → tournament.name que no coincidía con el tipo actualizado.
Para las pruebas funcionales, ejecuta estos tres en vivo:
# Prueba 1 — Login (autenticación)
curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@league.com","password":"admin123"}' | python -m json.tool

# Prueba 2 — Análisis NLP
curl -s -X POST http://localhost:8000/api/ia/analizar/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"texto":"torneo de robotica para 8 equipos de secundaria nivel avanzado knockout"}' | python -m json.tool

# Prueba 3 — Generación de criterios IA
curl -s -X POST http://localhost:8000/api/ia/generar-criterios/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"torneo_id":"<id>","tipo_torneo":"KNOCKOUT","nivel":"AVANZADO","categoria":"SECONDARY","descripcion":"torneo de sumo"}' | python -m json.tool
Cada prueba demuestra un punto de integración distinto: autenticación, NLP y generación de IA.


Integración de modelos o servicios de inteligencia artificial
El sistema integra un módulo de IA propio sin servicios externos. Se compone de dos partes: un analizador NLP basado en reglas regex que extrae parámetros estructurados desde texto libre (número de equipos, categoría, nivel técnico, formato), y un generador automático de rúbricas implementado en rubrica_generator.py que produce criterios de evaluación con pesos que suman exactamente 100%, usando Decimal para evitar errores de precisión.
Procesamiento y análisis de datos del sistema
El sistema recibe texto libre del organizador, lo normaliza y aplica patrones regex para extraer cada parámetro, asignando un nivel de confianza (0.0–1.0) a cada extracción. Con esos datos selecciona una de 9 plantillas (3 formatos × 3 niveles), inyecta hasta 2 criterios adicionales según palabras clave en la descripción ("sumo", "laberinto", "seguidor de línea"), y redistribuye los pesos proporcionalmente. Cada análisis queda guardado en la tabla competencia_nlp_analysis de PostgreSQL.
Documentación del flujo IA con frontend/backend
El organizador interactúa desde AIRecommendations.tsx, que llama a POST /api/ia/generar-criterios. El backend genera los criterios y los retorna con un sesion_ia_id. El usuario puede ajustar pesos (cada cambio llama a PUT /api/ia/criterios/{id}) y al confirmar se llama a POST /api/ia/criterios/{sesion_id}/confirmar, que valida que la suma sea 100% ±0.01 — si no, retorna HTTP 422; si sí, marca todos como ACEPTADO en base de datos.



ITEGRADOR
. Integración completa frontend, backend e IA
Qué mostrar: que los tres servicios se comunican entre sí en tiempo real.
Cómo demostrarlo:
Abre el navegador en http://localhost:5173, inicia sesión con admin@league.com / admin123, navega a la sección de IA y genera criterios para un torneo. Mientras lo haces, muestra en paralelo los logs del backend:
docker-compose logs -f backend
Verás en tiempo real cómo el frontend llama a POST /api/ia/generar-criterios y el backend responde. Eso demuestra la integración de los tres.
Para explicarlo, señala los tres archivos clave:
Frontend → AIRecommendations.tsx
Backend → ia_views.py
IA → rubrica_generator.py
2. Configuración de entorno y despliegue local
Qué mostrar: el docker-compose.yml y que con un solo comando levanta todo.
Cómo demostrarlo paso a paso:
