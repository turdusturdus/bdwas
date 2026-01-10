from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence
import psycopg2
from psycopg2.extras import RealDictCursor

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

    def list_matches(self, *, q: Optional[str] = None, filters=None):
        sql = """
              SELECT m.match_id::text as id, m.utc_date, \
                     m.matchday, \
                     ht.name as home_name, \
                     at.name as away_name
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
                "utc_date": r["utc_date"].isoformat() if r["utc_date"] else str(r["utc_date"]),
                "matchday": r["matchday"],
                "label": f"{r['home_name']} vs {r['away_name']}",
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
            "utc_date": row["utc_date"].isoformat() if row["utc_date"] else str(row["utc_date"]),
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
        return f'{match.get("home_name","HOME")} vs {match.get("away_name","AWAY")}'

    def create_league(self, data: Payload): raise NotImplementedError
    def update_league(self, league_id: str, data: Payload): raise NotImplementedError
    def delete_league(self, league_id: str) -> bool: raise NotImplementedError

    def create_team(self, data: Payload): pass
    def update_team(self, team_id: str, data: Payload): pass
    def delete_team(self, team_id: str) -> bool: pass
    def create_player(self, data: Payload): pass
    def update_player(self, player_id: str, data: Payload): pass
    def delete_player(self, player_id: str) -> bool: pass
    def create_match(self, data: Payload): pass
    def update_match(self, match_id: str, data: Payload): pass
    def delete_match(self, match_id: str) -> bool: pass