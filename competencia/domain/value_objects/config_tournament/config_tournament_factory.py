from __future__ import annotations
from .config_tournament import ConfigTournament
from .config_knockout import ConfigKnockout

from .config_hybrid import ConfigHybrid
from .config_round_robin import ConfigRoundRobin

class ConfigTournamentFactory:
    __configs = {
        "knockout": ConfigKnockout,
        "round_robin": ConfigRoundRobin,
        "hybrid": ConfigHybrid,
    }

    @staticmethod
    def create_config_tournament(tournament_type: str, data: dict) -> ConfigTournament:
        return ConfigTournamentFactory.__configs[tournament_type](**data)