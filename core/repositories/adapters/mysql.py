from __future__ import annotations

import json
from typing import Any, Mapping, Optional, Sequence
from urllib.parse import urlparse
import mysql.connector

from ..base import LeagueRepo, Payload


class MysqlAdapter(LeagueRepo):
    def __init__(self, uri: str):
        parsed = urlparse(uri)
        self.config = {
            'user': parsed.username,
            'password': parsed.password,
            'host': parsed.hostname,
            'port': parsed.port or 3306,
            'database': parsed.path.lstrip('/'),
            'autocommit': False,
        }

        try:
            conn = self._get_connection()
            conn.close()
            print(f"Connected to MySQL: {parsed.hostname}")
        except Exception as e:
            print(f"MySQL connection failed: {e}")

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def _fetchall(self, query: str, params: tuple = None) -> list[dict]:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(query, params or ())
                return cur.fetchall()
        finally:
            conn.close()

    def _fetchone(self, query: str, params: tuple = None) -> dict | None:
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(query, params or ())
                return cur.fetchone()
        finally:
            conn.close()

    def _execute(self, query: str, params: tuple = None) -> int:
        """Executes query, commits, and returns lastrowid (for auto_increment)."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                last_id = cur.lastrowid
            conn.commit()
            return last_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def list_leagues(self, *, q: Optional[str] = None, filters=None) -> Sequence[Mapping[str, Any]]:
        sql = """
              SELECT l.league_id as id, l.name, c.name as country
              FROM leagues l
                       LEFT JOIN countries c ON l.country_id = c.country_id \
              """
        params = []
        if q:
            sql += " WHERE l.name LIKE %s"
            params.append(f"%{q}%")

        sql += " ORDER BY l.name"
        return self._fetchall(sql, tuple(params))

    def get_league(self, league_id: str):
        sql = """
              SELECT l.league_id as id, l.name, c.name as country
              FROM leagues l
                       LEFT JOIN countries c ON l.country_id = c.country_id
              WHERE l.league_id = %s \
              """
        try:
            return self._fetchone(sql, (int(league_id),))
        except ValueError:
            return None

    def create_league(self, data: Payload):
        country_id = int(data.get("country_id") or 1)

        sql = """
              INSERT INTO leagues (name, country_id)
              VALUES (%s, %s) \
              """
        self._execute(sql, (data.get("name"), country_id))

    def update_league(self, league_id: str, data: Payload):
        sql = "UPDATE leagues SET name = %s WHERE league_id = %s"
        self._execute(sql, (data.get("name"), int(league_id)))

    def delete_league(self, league_id: str) -> bool:
        self._execute("DELETE FROM leagues WHERE league_id = %s", (int(league_id),))
        return True

    def list_teams(self, *, q: Optional[str] = None, filters=None):
        sql = """
              SELECT t.team_id as id, \
                     t.name, \
                     t.founded_year, \
                     c.name    as coach, \
                     s.name    as stadium, \
                     (SELECT sn.league_id
                      FROM standings st
                               JOIN seasons sn ON st.season_id = sn.season_id
                      WHERE st.team_id = t.team_id
                      ORDER BY sn.year DESC
                      LIMIT 1) as league_id
              FROM teams t
                       LEFT JOIN coaches c ON t.coach_id = c.coach_id
                       LEFT JOIN stadiums s ON t.stadium_id = s.stadium_id \
              """
        params = []
        if q:
            sql += " WHERE t.name LIKE %s"
            params.append(f"%{q}%")
        sql += " ORDER BY t.name"
        return self._fetchall(sql, tuple(params))

    def get_team(self, team_id: str):
        sql = """
              SELECT t.team_id as id, \
                     t.name, \
                     t.founded_year, \
                     c.name    as coach, \
                     s.name    as stadium, \
                     (SELECT sn.league_id
                      FROM standings st
                               JOIN seasons sn ON st.season_id = sn.season_id
                      WHERE st.team_id = t.team_id
                      ORDER BY sn.year DESC
                      LIMIT 1) as league_id
              FROM teams t
                       LEFT JOIN coaches c ON t.coach_id = c.coach_id
                       LEFT JOIN stadiums s ON t.stadium_id = s.stadium_id
              WHERE t.team_id = %s \
              """
        try:
            return self._fetchone(sql, (int(team_id),))
        except ValueError:
            return None

    def create_team(self, data: Payload):
        founded = int(data["founded_year"]) if data.get("founded_year") else None
        sql = "INSERT INTO teams (name, founded_year) VALUES (%s, %s)"
        self._execute(sql, (data.get("name"), founded))

    def update_team(self, team_id: str, data: Payload):
        founded = int(data["founded_year"]) if data.get("founded_year") else None
        sql = "UPDATE teams SET name = %s, founded_year = %s WHERE team_id = %s"
        self._execute(sql, (data.get("name"), founded, int(team_id)))

    def delete_team(self, team_id: str) -> bool:
        self._execute("DELETE FROM teams WHERE team_id = %s", (int(team_id),))
        return True

    def list_players(self, *, q: Optional[str] = None, filters=None):
        sql = """
              SELECT p.player_id as id, \
                     p.name, \
                     p.position, \
                     cn.name     as nationality, \
                     p.team_id, \
                     p.team_id   as currentTeamId
              FROM players p
                       LEFT JOIN countries cn ON p.nationality_id = cn.country_id \
              """
        params = []
        if q:
            sql += " WHERE p.name LIKE %s"
            params.append(f"%{q}%")
        sql += " ORDER BY p.name"
        return self._fetchall(sql, tuple(params))

    def get_player(self, player_id: str):
        sql = """
              SELECT p.player_id as id, \
                     p.name, \
                     p.position, \
                     cn.name     as nationality, \
                     p.team_id, \
                     p.team_id   as currentTeamId
              FROM players p
                       LEFT JOIN countries cn ON p.nationality_id = cn.country_id
              WHERE p.player_id = %s \
              """
        try:
            return self._fetchone(sql, (int(player_id),))
        except ValueError:
            return None

    def team_players(self, team_id: str):
        sql = "SELECT player_id as id, name, position FROM players WHERE team_id = %s"
        try:
            return self._fetchall(sql, (int(team_id),))
        except ValueError:
            return []

    def list_matches(self, *, q: Optional[str] = None, filters=None):
        sql = """
              SELECT m.match_id as id, \
                     m.utc_date, \
                     m.matchday, \
                     ht.name    as home_name, \
                     at.name    as away_name, \
                     sn.year    as season_name
              FROM matches m
                       JOIN teams ht ON m.home_team_id = ht.team_id
                       JOIN teams at ON m.away_team_id = at.team_id
                       JOIN seasons sn ON m.season_id = sn.season_id
              ORDER BY m.utc_date DESC \
              """
        rows = self._fetchall(sql)

        out = []
        for r in rows:
            out.append({
                "id": str(r["id"]),
                "utc_date": str(r["utc_date"]),
                "matchday": r["matchday"],
                "label": f"[{r['season_name']}] {r['home_name']} vs {r['away_name']}",
            })
        return out

    def get_match(self, match_id: str):
        sql = """
              SELECT m.match_id                       as id, \
                     m.utc_date, \
                     m.matchday, \
                     sn.year                          as season_name, \
                     m.home_team_id, \
                     m.away_team_id, \

                     s.full_time_home, \
                     s.full_time_away, \
                     s.half_time_home, \
                     s.half_time_away, \

                     (SELECT JSON_ARRAYAGG(
                                     JSON_OBJECT(
                                             'name', r.name,
                                             'role', mr.role,
                                             'nationality', c.name
                                     )
                             )
                      FROM match_referees mr
                               JOIN referees r ON mr.referee_id = r.referee_id
                               LEFT JOIN countries c ON r.nationality_id = c.country_id
                      WHERE mr.match_id = m.match_id) as referees_data, \

                     (SELECT JSON_OBJECTAGG(ms.stat_key, ms.stat_value)
                      FROM match_statistics ms
                      WHERE ms.match_id = m.match_id) as statistics_data

              FROM matches m
                       JOIN seasons sn ON m.season_id = sn.season_id
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

        stats = row["statistics_data"]
        if isinstance(stats, (str, bytes)):
            try:
                stats = json.loads(stats)
            except:
                stats = {}

        refs = row["referees_data"]
        if isinstance(refs, (str, bytes)):
            try:
                refs = json.loads(refs)
            except:
                refs = []

        return {
            "id": str(row["id"]),
            "utc_date": str(row["utc_date"]),
            "matchday": row["matchday"],
            "season": row["season_name"],
            "home_team_id": str(row["home_team_id"]),
            "away_team_id": str(row["away_team_id"]),
            "score": {
                "full_time": {"home": row["full_time_home"], "away": row["full_time_away"]},
                "half_time": {"home": row["half_time_home"], "away": row["half_time_away"]},
            },
            "statistics": stats or {},
            "referees": refs or [],
        }

    def match_label(self, match: Mapping[str, Any]) -> str:
        return str(match.get("label", ""))

    def create_player(self, data: Payload):
        pass

    def update_player(self, player_id: str, data: Payload):
        pass

    def delete_player(self, player_id: str) -> bool:
        return False

    def create_match(self, data: Payload):
        pass

    def update_match(self, match_id: str, data: Payload):
        pass

    def delete_match(self, match_id: str) -> bool:
        return False
