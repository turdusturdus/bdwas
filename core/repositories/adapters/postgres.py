from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, cast
import psycopg2
from psycopg2.extras import RealDictCursor
import json

from ..base import LeagueRepo, Payload


class PostgresAdapter(LeagueRepo):
    def __init__(self, dsn: str):
        self.dsn = dsn

    def _get_connection(self):
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        return conn

    def _fetchall(self, query: str, params: tuple = None) -> list[dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                return cur.fetchall()

    def _fetchone(self, query: str, params: tuple = None) -> dict | None:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                return cur.fetchone()

    def _execute(self, query: str, params: tuple = None) -> Any:
        """Executes query and returns the first column of the first row if available (e.g. ID)."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                try:
                    return cur.fetchone()[0]
                except (psycopg2.ProgrammingError, TypeError):
                    return None

    def list_leagues(self, *, q: Optional[str] = None, filters=None) -> Sequence[Mapping[str, Any]]:
        sql = """
            SELECT 
                l.league_id as id, 
                l.name, 
                c.name as country
            FROM leagues l
            LEFT JOIN countries c ON l.country_id = c.country_id
        """
        params = []

        if q:
            sql += " WHERE l.name ILIKE %s"
            params.append(f"%{q}%")

        sql += " ORDER BY l.name"

        return self._fetchall(sql, tuple(params))

    def get_league(self, league_id: str):
        sql = """
            SELECT 
                l.league_id as id, 
                l.name, 
                l.country_id,
                c.name as country
            FROM leagues l
            LEFT JOIN countries c ON l.country_id = c.country_id
            WHERE l.league_id = %s
        """
        try:
            lid = int(league_id)
        except ValueError:
            return None

        return self._fetchone(sql, (lid,))

    def create_league(self, data: Payload):
        country_id = data.get("country_id")
        if country_id:
            country_id = int(country_id)
        else:
            country_id = None

        sql = "INSERT INTO leagues (name, country_id) VALUES (%s, %s) RETURNING league_id"
        new_id = self._execute(sql, (data.get("name"), country_id))
        return {**data, "id": str(new_id)}

    def update_league(self, league_id: str, data: Payload):
        country_id = data.get("country_id")
        if country_id:
            country_id = int(country_id)
        else:
            country_id = None
        
        sql = "UPDATE leagues SET name = %s, country_id = %s WHERE league_id = %s"
        self._execute(sql, (data.get("name"), country_id, int(league_id)))
        return self.get_league(league_id)

    def delete_league(self, league_id: str) -> bool:
        self._execute("DELETE FROM leagues WHERE league_id = %s", (int(league_id),))
        return True

    def list_teams(self, *, q: Optional[str] = None, filters=None):
        sql = """
              SELECT t.team_id::text as id, t.name, \
                     t.founded_year, \
                     c.name as coach, \
                     s.name as stadium, \
                     (SELECT sn.league_id::text
                      FROM standings st
                               JOIN seasons sn ON st.season_id = sn.season_id
                      WHERE st.team_id = t.team_id
                      ORDER BY sn.year DESC \
                               LIMIT 1 ) as league_id
              FROM teams t
                  LEFT JOIN coaches c \
              ON t.coach_id = c.coach_id
                  LEFT JOIN stadiums s ON t.stadium_id = s.stadium_id \
              """
        params = []
        if q:
            sql += " WHERE t.name ILIKE %s"
            params.append(f"%{q}%")

        sql += " ORDER BY t.name"
        return self._fetchall(sql, tuple(params))

    def get_team(self, team_id: str):
        sql = """
              SELECT t.team_id::text as id, t.name, \
                     t.founded_year, \
                     t.coach_id, \
                     t.stadium_id, \
                     c.name as coach, \
                     s.name as stadium, \
                     (SELECT sn.league_id::text
                      FROM standings st
                               JOIN seasons sn ON st.season_id = sn.season_id
                      WHERE st.team_id = t.team_id
                      ORDER BY sn.year DESC \
                               LIMIT 1 ) as league_id
              FROM teams t
                  LEFT JOIN coaches c \
              ON t.coach_id = c.coach_id
                  LEFT JOIN stadiums s ON t.stadium_id = s.stadium_id
              WHERE t.team_id = %s \
              """
        try:
            tid = int(team_id)
        except ValueError:
            return None

        return self._fetchone(sql, (tid,))

    def create_team(self, data: Payload):
        founded = int(data["founded_year"]) if data.get("founded_year") else None
        coach_id = int(data["coach_id"]) if data.get("coach_id") else None
        stadium_id = int(data["stadium_id"]) if data.get("stadium_id") else None
        
        sql = "INSERT INTO teams (name, founded_year, coach_id, stadium_id) VALUES (%s, %s, %s, %s) RETURNING team_id"
        new_id = self._execute(sql, (data.get("name"), founded, coach_id, stadium_id))
        return {**data, "id": str(new_id)}

    def update_team(self, team_id: str, data: Payload):
        founded = int(data["founded_year"]) if data.get("founded_year") else None
        coach_id = int(data["coach_id"]) if data.get("coach_id") else None
        stadium_id = int(data["stadium_id"]) if data.get("stadium_id") else None
        
        sql = "UPDATE teams SET name = %s, founded_year = %s, coach_id = %s, stadium_id = %s WHERE team_id = %s"
        self._execute(sql, (data.get("name"), founded, coach_id, stadium_id, int(team_id)))
        return self.get_team(team_id)

    def delete_team(self, team_id: str) -> bool:
        self._execute("DELETE FROM teams WHERE team_id = %s", (int(team_id),))
        return True

    def team_players(self, team_id: str):
        sql = """
              SELECT p.player_id::text as id, p.name, \
                     p.position
              FROM players p
              WHERE p.team_id = %s \
              """
        try:
            tid = int(team_id)
        except ValueError:
            return []
        return self._fetchall(sql, (tid,))

    def list_players(self, *, q: Optional[str] = None, filters=None):
        sql = """
              SELECT p.player_id::text as id, p.name, \
                     p.position, \
                     cn.name as nationality, \
                     p.team_id::text as "team_id", p.team_id::text as "currentTeamId"
              FROM players p
                       LEFT JOIN countries cn ON p.nationality_id = cn.country_id \
              """
        params = []
        if q:
            sql += " WHERE p.name ILIKE %s"
            params.append(f"%{q}%")

        sql += " ORDER BY p.name"
        return self._fetchall(sql, tuple(params))

    def get_player(self, player_id: str):
        sql = """
              SELECT p.player_id::text as id, p.name, \
                     p.position, \
                     p.nationality_id, \
                     cn.name as nationality, \
                     p.team_id::text as "team_id", p.team_id::text as "currentTeamId"
              FROM players p
                       LEFT JOIN countries cn ON p.nationality_id = cn.country_id
              WHERE p.player_id = %s \
              """
        try:
            pid = int(player_id)
        except ValueError:
            return None
        return self._fetchone(sql, (pid,))

    def create_player(self, data: Payload):
        name = data.get("name", "")
        position = data.get("position", "")
        team_id = int(data["team_id"]) if data.get("team_id") else None
        nationality_id = int(data["nationality_id"]) if data.get("nationality_id") else None
        
        sql = "INSERT INTO players (name, position, team_id, nationality_id) VALUES (%s, %s, %s, %s) RETURNING player_id"
        new_id = self._execute(sql, (name, position, team_id, nationality_id))
        return {"id": str(new_id), "name": name, "position": position}

    def update_player(self, player_id: str, data: Payload):
        name = data.get("name", "")
        position = data.get("position", "")
        team_id = int(data["team_id"]) if data.get("team_id") else None
        nationality_id = int(data["nationality_id"]) if data.get("nationality_id") else None
        
        sql = "UPDATE players SET name = %s, position = %s, team_id = %s, nationality_id = %s WHERE player_id = %s"
        self._execute(sql, (name, position, team_id, nationality_id, int(player_id)))
        return self.get_player(player_id)

    def delete_player(self, player_id: str) -> bool:
        self._execute("DELETE FROM players WHERE player_id = %s", (int(player_id),))
        return True

    def list_matches(self, *, q: Optional[str] = None, filters=None):
        sql = """
              SELECT m.match_id::text as id, m.utc_date, \
                     m.matchday, \
                     ht.name as home_name, \
                     at.name as away_name, \
                     sn.year as season_name
              FROM matches m
                       JOIN teams ht ON m.home_team_id = ht.team_id
                       JOIN teams at \
              ON m.away_team_id = at.team_id
                  JOIN seasons sn ON m.season_id = sn.season_id
              ORDER BY m.utc_date DESC \
              """
        rows = self._fetchall(sql)

        out = []
        for r in rows:
            out.append({
                "id": r["id"],
                "utc_date": r["utc_date"].isoformat() if r["utc_date"] else None,
                "matchday": r["matchday"],
                "label": f"[{r['season_name']}] {r['home_name']} vs {r['away_name']}",
            })
        return out

    def get_match(self, match_id: str):
        sql = """
              SELECT m.match_id::text as id, m.utc_date, \
                     m.matchday, \
                     sn.year as "season_name", \
                     m.home_team_id::text as "home_team_id", m.away_team_id::text as "away_team_id", m.statistics, \
                     (s.full_time).home as ft_home,
                (s.full_time).away as ft_away,
                (s.half_time).home as ht_home,
                (s.half_time).away as ht_away,
                (
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            'name', r.name, 
                            'role', mr.role, 
                            'nationality', c.name
                        )
                    )
                    FROM match_referees mr
                    JOIN referees r ON mr.referee_id = r.referee_id
                    LEFT JOIN countries c ON r.nationality_id = c.country_id
                    WHERE mr.match_id = m.match_id
                ) as referees_data
              FROM matches m
                  JOIN seasons sn \
              ON m.season_id = sn.season_id
                  LEFT JOIN scores s ON m.match_id = s.match_id
              WHERE m.match_id = %s \
              """
        try:
            mid = int(match_id)
        except ValueError:
            return None

        row = self._fetchone(sql, (mid,))
        if not row:
            return None

        return {
            "id": row["id"],
            "utc_date": row["utc_date"].isoformat() if row["utc_date"] else None,
            "matchday": row["matchday"],
            "season": row["season_name"],
            "home_team_id": row["home_team_id"],
            "away_team_id": row["away_team_id"],
            "score": {
                "full_time": {"home": row["ft_home"], "away": row["ft_away"]},
                "half_time": {"home": row["ht_home"], "away": row["ht_away"]},
            },
            "statistics": row["statistics"] or {},
            "referees": row["referees_data"] or [],
        }

    def match_label(self, match: Mapping[str, Any]) -> str:
        return str(match.get("label", ""))

    def create_match(self, data: Payload):
        utc_date = data.get("utc_date", "")
        matchday = int(data.get("matchday") or 1)
        home_team_id = int(data["home_team_id"]) if data.get("home_team_id") else None
        away_team_id = int(data["away_team_id"]) if data.get("away_team_id") else None
        season_id = int(data["season_id"]) if data.get("season_id") else None
        
        sql = """
              INSERT INTO matches (utc_date, matchday, home_team_id, away_team_id, season_id)
              VALUES (%s, %s, %s, %s, %s)
              RETURNING match_id
              """
        new_id = self._execute(sql, (utc_date, matchday, home_team_id, away_team_id, season_id))
        return {"id": str(new_id), "utc_date": utc_date, "matchday": matchday}

    def update_match(self, match_id: str, data: Payload):
        utc_date = data.get("utc_date", "")
        matchday = int(data.get("matchday") or 1)
        home_team_id = data.get("home_team_id")
        away_team_id = data.get("away_team_id")
        
        if home_team_id and away_team_id:
            sql = """
                  UPDATE matches 
                  SET utc_date = %s, matchday = %s, home_team_id = %s, away_team_id = %s 
                  WHERE match_id = %s
                  """
            self._execute(sql, (utc_date, matchday, int(home_team_id), int(away_team_id), int(match_id)))
        else:
            sql = "UPDATE matches SET utc_date = %s, matchday = %s WHERE match_id = %s"
            self._execute(sql, (utc_date, matchday, int(match_id)))
        return self.get_match(match_id)

    def delete_match(self, match_id: str) -> bool:
        self._execute("DELETE FROM matches WHERE match_id = %s", (int(match_id),))
        return True


    
    def list_countries(self) -> list[dict]:
        sql = "SELECT country_id as id, name FROM countries ORDER BY name"
        return self._fetchall(sql)

    def list_stadiums(self) -> list[dict]:
        sql = "SELECT stadium_id as id, name, location FROM stadiums ORDER BY name"
        return self._fetchall(sql)

    def list_coaches(self) -> list[dict]:
        sql = """
              SELECT c.coach_id as id, c.name, cn.name as nationality
              FROM coaches c
              LEFT JOIN countries cn ON c.nationality_id = cn.country_id
              ORDER BY c.name
              """
        return self._fetchall(sql)

    def list_seasons(self) -> list[dict]:
        sql = """
              SELECT s.season_id as id, s.year, l.name as league_name
              FROM seasons s
              JOIN leagues l ON s.league_id = l.league_id
              ORDER BY s.year DESC, l.name
              """
        return self._fetchall(sql)