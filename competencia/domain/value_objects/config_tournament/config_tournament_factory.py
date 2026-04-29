from .config_tournament import ConfigTournament
from .config_knockout import ConfigKnockout


class ConfigTournamentFactory:
    __configs = {
        "knockout": ConfigKnockout,
    }

    @staticmethod
    def create_config_tournament(tournament_type: str, data: dict) -> ConfigTournament:
        return ConfigTournamentFactory.__configs[tournament_type](**data)