from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from ..base import LeagueRepo, Payload


class PostgresAdapter(LeagueRepo):
    """
    Szkielet adaptera pod Twój schemat SQL (countries/leagues/teams/...).
    Tu docelowo będą zapytania SQL albo warstwa DAO.
    """

    def __init__(self, dsn: str):
        self.dsn = dsn

    # Browse
    def list_leagues(self, *, q: Optional[str] = None, filters=None) -> Sequence[Mapping[str, Any]]:
        raise NotImplementedError("PostgresAdapter.list_leagues: do zrobienia po integracji DB")

    def get_league(self, league_id: int):
        raise NotImplementedError

    def list_teams(self, *, q: Optional[str] = None, filters=None):
        raise NotImplementedError

    def get_team(self, team_id: int):
        raise NotImplementedError

    def list_players(self, *, q: Optional[str] = None, filters=None):
        raise NotImplementedError

    def get_player(self, player_id: int):
        raise NotImplementedError

    def team_players(self, team_id: int):
        raise NotImplementedError

    def list_matches(self, *, q: Optional[str] = None, filters=None):
        raise NotImplementedError

    def get_match(self, match_id: int):
        raise NotImplementedError

    def match_label(self, match: Mapping[str, Any]) -> str:
        # opcjonalnie: w postgresie label można już budować w SQL JOINem
        home = match.get("home_team_name", "HOME")
        away = match.get("away_team_name", "AWAY")
        return f"{home} vs {away}"

    # CRUD
    def create_league(self, data: Payload):
        raise NotImplementedError

    def update_league(self, league_id: int, data: Payload):
        raise NotImplementedError

    def delete_league(self, league_id: int) -> bool:
        raise NotImplementedError

    def create_team(self, data: Payload):
        raise NotImplementedError

    def update_team(self, team_id: int, data: Payload):
        raise NotImplementedError

    def delete_team(self, team_id: int) -> bool:
        raise NotImplementedError

    def create_player(self, data: Payload):
        raise NotImplementedError

    def update_player(self, player_id: int, data: Payload):
        raise NotImplementedError

    def delete_player(self, player_id: int) -> bool:
        raise NotImplementedError

    def create_match(self, data: Payload):
        raise NotImplementedError

    def update_match(self, match_id: int, data: Payload):
        raise NotImplementedError

    def delete_match(self, match_id: int) -> bool:
        raise NotImplementedError
