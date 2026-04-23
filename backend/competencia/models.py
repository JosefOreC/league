# Punto de entrada de modelos para el sistema de migraciones de Django.
# Los modelos reales están en infrastructure/adapters/output/models.py
# para mantener la arquitectura hexagonal limpia.
from competencia.infrastructure.adapters.output.models import (  # noqa: F401
    TournamentRuleModel,
    TournamentModel,
)
