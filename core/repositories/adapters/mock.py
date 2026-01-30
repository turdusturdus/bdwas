from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from ..base import LeagueRepo, Payload
from .. import mock_repo


class MockAdapter(LeagueRepo):
    """Mock adapter using in-memory list."""


    def list_leagues(self, *, q: Optional[str] = None, filters=None) -> Sequence[Mapping[str, Any]]:
        return mock_repo.list_leagues(q=q)

    def get_league(self, league_id: int):
        return mock_repo.get_league(league_id)

    def list_teams(self, *, q: Optional[str] = None, filters=None):
        return mock_repo.list_teams(q=q)

    def get_team(self, team_id: int):
        return mock_repo.get_team(team_id)

    def list_players(self, *, q: Optional[str] = None, filters=None):
        return mock_repo.list_players(q=q)

    def get_player(self, player_id: int):
        return mock_repo.get_player(player_id)

    def team_players(self, team_id: int):
        return mock_repo.team_players(team_id)

    def list_matches(self, *, q: Optional[str] = None, filters=None):

        out = []
        for m in mock_repo.list_matches(q=q):
            m2 = dict(m)
            m2["label"] = mock_repo.match_label(m)
            out.append(m2)
        return out

    def get_match(self, match_id: int):
        return mock_repo.get_match(match_id)

    def match_label(self, match: Mapping[str, Any]) -> str:
        return mock_repo.match_label(match)


    def _next_id(self, items, key="id") -> int:
        return (max((x.get(key, 0) for x in items), default=0) + 1)

    def create_league(self, data: Payload):
        name = str(data.get("name", "")).strip() or "Nowa liga"
        country = str(data.get("country", "")).strip() or "Nieznany kraj"
        new_item = {"id": self._next_id(mock_repo.LEAGUES), "name": name, "country": country}
        mock_repo.LEAGUES.append(new_item)
        return new_item

    def update_league(self, league_id: int, data: Payload):
        item = mock_repo.get_league(league_id)
        if not item:
            return None
        item["name"] = str(data.get("name", item["name"])).strip() or item["name"]
        item["country"] = str(data.get("country", item["country"])).strip() or item["country"]
        return item

    def delete_league(self, league_id: int) -> bool:
        before = len(mock_repo.LEAGUES)
        mock_repo.LEAGUES[:] = [x for x in mock_repo.LEAGUES if x["id"] != league_id]
        return len(mock_repo.LEAGUES) != before

    def create_team(self, data: Payload):
        name = str(data.get("name", "")).strip() or "Nowa drużyna"
        founded_year = int(data.get("founded_year") or 2000)
        coach = str(data.get("coach", "")).strip() or "Trener"
        stadium = str(data.get("stadium", "")).strip() or "Stadion"
        league_id = int(data.get("league_id") or 1)
        new_item = {
            "id": self._next_id(mock_repo.TEAMS),
            "name": name,
            "founded_year": founded_year,
            "coach": coach,
            "stadium": stadium,
            "league_id": league_id,
        }
        mock_repo.TEAMS.append(new_item)
        return new_item

    def update_team(self, team_id: int, data: Payload):
        item = mock_repo.get_team(team_id)
        if not item:
            return None
        item["name"] = str(data.get("name", item["name"])).strip() or item["name"]
        item["founded_year"] = int(data.get("founded_year") or item.get("founded_year") or 2000)
        item["coach"] = str(data.get("coach", item["coach"])).strip() or item["coach"]
        item["stadium"] = str(data.get("stadium", item["stadium"])).strip() or item["stadium"]
        return item

    def delete_team(self, team_id: int) -> bool:
        before = len(mock_repo.TEAMS)
        mock_repo.TEAMS[:] = [x for x in mock_repo.TEAMS if x["id"] != team_id]
        return len(mock_repo.TEAMS) != before

    def create_player(self, data: Payload):
        name = str(data.get("name", "")).strip() or "Nowy zawodnik"
        position = str(data.get("position", "")).strip() or "MF"
        nationality = str(data.get("nationality", "")).strip() or "PL"
        team_id = int(data.get("team_id") or 1)
        new_item = {
            "id": self._next_id(mock_repo.PLAYERS),
            "name": name,
            "position": position,
            "team_id": team_id,
            "nationality": nationality,
        }
        mock_repo.PLAYERS.append(new_item)
        return new_item

    def update_player(self, player_id: int, data: Payload):
        item = mock_repo.get_player(player_id)
        if not item:
            return None
        item["name"] = str(data.get("name", item["name"])).strip() or item["name"]
        item["position"] = str(data.get("position", item["position"])).strip() or item["position"]
        item["nationality"] = str(data.get("nationality", item["nationality"])).strip() or item["nationality"]
        return item

    def delete_player(self, player_id: int) -> bool:
        before = len(mock_repo.PLAYERS)
        mock_repo.PLAYERS[:] = [x for x in mock_repo.PLAYERS if x["id"] != player_id]
        return len(mock_repo.PLAYERS) != before

    def create_match(self, data: Payload):

        new_item = {
            "id": self._next_id(mock_repo.MATCHES),
            "utc_date": str(data.get("utc_date", "2025-01-01")),
            "matchday": int(data.get("matchday") or 1),
            "league_id": 1,
            "season": "2024/2025",
            "home_team_id": 1,
            "away_team_id": 2,
            "score": {"half_time": {"home": 0, "away": 0}, "full_time": {"home": 0, "away": 0}},
            "statistics": {},
            "referees": [],
        }
        mock_repo.MATCHES.append(new_item)
        return new_item

    def update_match(self, match_id: int, data: Payload):
        item = mock_repo.get_match(match_id)
        if not item:
            return None
        item["utc_date"] = str(data.get("utc_date", item.get("utc_date")))
        item["matchday"] = int(data.get("matchday") or item.get("matchday") or 1)
        return item

    def delete_match(self, match_id: int) -> bool:
        before = len(mock_repo.MATCHES)
        mock_repo.MATCHES[:] = [x for x in mock_repo.MATCHES if x["id"] != match_id]
        return len(mock_repo.MATCHES) != before


    def list_countries(self) -> list[dict]:

        return [
            {"id": 1, "name": "England"},
            {"id": 2, "name": "Spain"},
            {"id": 3, "name": "Poland"},
            {"id": 4, "name": "Germany"},
            {"id": 5, "name": "France"},
            {"id": 6, "name": "Italy"},
        ]

    def list_stadiums(self) -> list[dict]:
        return [
            {"id": 1, "name": "Etihad Stadium", "location": "Manchester"},
            {"id": 2, "name": "Anfield", "location": "Liverpool"},
            {"id": 3, "name": "Old Trafford", "location": "Manchester"},
            {"id": 4, "name": "Emirates Stadium", "location": "London"},
        ]

    def list_coaches(self) -> list[dict]:
        return [
            {"id": 1, "name": "Pep Guardiola", "nationality": "Spain"},
            {"id": 2, "name": "Jurgen Klopp", "nationality": "Germany"},
            {"id": 3, "name": "Erik ten Hag", "nationality": "Netherlands"},
            {"id": 4, "name": "Mikel Arteta", "nationality": "Spain"},
        ]

    def list_seasons(self) -> list[dict]:
        return [
            {"id": 1, "year": "2023-2024", "league_name": "Premier League"},
            {"id": 2, "year": "2024-2025", "league_name": "Premier League"},
        ]
