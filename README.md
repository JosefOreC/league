







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

