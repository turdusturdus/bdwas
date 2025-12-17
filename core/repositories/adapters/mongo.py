from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence
from datetime import datetime

from pymongo import MongoClient
from bson import ObjectId

from ..base import LeagueRepo, Payload


def oid(s: str) -> ObjectId:
    return ObjectId(s)


def str_id(doc: Mapping[str, Any]) -> dict[str, Any]:
    d = dict(doc)
    d["id"] = str(d.pop("_id"))
    return d


class MongoAdapter(LeagueRepo):
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    # ---- Leagues ----
    def list_leagues(self, *, q: Optional[str] = None, filters=None) -> Sequence[Mapping[str, Any]]:
        match: dict[str, Any] = {}
        if q:
            match["name"] = {"$regex": q, "$options": "i"}

        pipeline = [
            {"$match": match},
            {"$lookup": {"from": "countries", "localField": "countryId", "foreignField": "_id", "as": "country"}},
            {"$unwind": {"path": "$country", "preserveNullAndEmptyArrays": True}},
            {"$project": {"_id": 1, "name": 1, "country": "$country.name"}},
        ]
        return [str_id(x) for x in self.db.leagues.aggregate(pipeline)]

    def get_league(self, league_id: str):
        pipeline = [
            {"$match": {"_id": oid(league_id)}},
            {"$lookup": {"from": "countries", "localField": "countryId", "foreignField": "_id", "as": "country"}},
            {"$unwind": {"path": "$country", "preserveNullAndEmptyArrays": True}},
            {"$project": {"_id": 1, "name": 1, "country": "$country.name"}},
        ]
        out = list(self.db.leagues.aggregate(pipeline))
        return str_id(out[0]) if out else None

    # ---- Teams ----
    def list_teams(self, *, q: Optional[str] = None, filters=None):
        match: dict[str, Any] = {}
        if q:
            match["name"] = {"$regex": q, "$options": "i"}

        pipeline = [
            {"$match": match},
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "foundedYear": 1,
                    "leagueId": 1,
                    "coach": "$coach.name",
                    "stadium": "$stadium.name",
                }
            },
            {"$sort": {"name": 1}},
        ]

        out = []
        for x in self.db.teams.aggregate(pipeline):
            x = str_id(x)
            out.append(
                {
                    "id": x["id"],
                    "name": x.get("name"),
                    "founded_year": x.get("foundedYear"),
                    "coach": x.get("coach"),
                    "stadium": x.get("stadium"),
                    "league_id": str(x.get("leagueId")) if x.get("leagueId") else None,
                }
            )
        return out

    def get_team(self, team_id: str):
        doc = self.db.teams.find_one({"_id": oid(team_id)})
        if not doc:
            return None
        d = str_id(doc)
        return {
            "id": d["id"],
            "name": d.get("name"),
            "founded_year": d.get("foundedYear"),
            "coach": (d.get("coach") or {}).get("name"),
            "stadium": (d.get("stadium") or {}).get("name"),
            "league_id": str(d.get("leagueId")) if d.get("leagueId") else None,
        }

    # ---- Players ----
    def list_players(self, *, q: Optional[str] = None, filters=None):
        match: dict[str, Any] = {}
        if q:
            match["name"] = {"$regex": q, "$options": "i"}

        pipeline = [
            {"$match": match},
            {"$lookup": {"from": "countries", "localField": "nationalityId", "foreignField": "_id", "as": "nat"}},
            {"$unwind": {"path": "$nat", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "position": 1,
                    "currentTeamId": 1,
                    "nationality": "$nat.name",
                }
            },
            {"$sort": {"name": 1}},
        ]

        out = []
        for x in self.db.players.aggregate(pipeline):
            x = str_id(x)
            out.append(
                {
                    "id": x["id"],
                    "name": x.get("name"),
                    "position": x.get("position"),
                    "nationality": x.get("nationality"),
                    "team_id": str(x.get("currentTeamId")) if x.get("currentTeamId") else None,
                    "currentTeamId": x.get("currentTeamId"),  # dla zgodności z view
                }
            )
        return out

    def get_player(self, player_id: str):
        pipeline = [
            {"$match": {"_id": oid(player_id)}},
            {"$lookup": {"from": "countries", "localField": "nationalityId", "foreignField": "_id", "as": "nat"}},
            {"$unwind": {"path": "$nat", "preserveNullAndEmptyArrays": True}},
            {"$project": {"_id": 1, "name": 1, "position": 1, "currentTeamId": 1, "nationality": "$nat.name"}},
        ]
        out = list(self.db.players.aggregate(pipeline))
        if not out:
            return None
        x = str_id(out[0])
        return {
            "id": x["id"],
            "name": x.get("name"),
            "position": x.get("position"),
            "nationality": x.get("nationality"),
            "currentTeamId": x.get("currentTeamId"),
            "team_id": str(x.get("currentTeamId")) if x.get("currentTeamId") else None,
        }

    def team_players(self, team_id: str):
        return [str_id(x) for x in self.db.players.find({"currentTeamId": oid(team_id)}, {"name": 1, "position": 1})]

    # ---- Matches ----
    def list_matches(self, *, q: Optional[str] = None, filters=None):
        pipeline = [
            {"$lookup": {"from": "teams", "localField": "homeTeamId", "foreignField": "_id", "as": "home"}},
            {"$lookup": {"from": "teams", "localField": "awayTeamId", "foreignField": "_id", "as": "away"}},
            {"$unwind": "$home"},
            {"$unwind": "$away"},
            {"$project": {"_id": 1, "utcDate": 1, "matchday": 1, "homeName": "$home.name", "awayName": "$away.name"}},
            {"$sort": {"utcDate": -1}},
        ]
        out = []
        for x in self.db.matches.aggregate(pipeline):
            x = str_id(x)
            out.append(
                {
                    "id": x["id"],
                    "utc_date": x["utcDate"].date().isoformat() if isinstance(x["utcDate"], datetime) else str(x["utcDate"]),
                    "matchday": x["matchday"],
                    "label": f'{x.get("homeName","HOME")} vs {x.get("awayName","AWAY")}',
                }
            )
        return out

    def get_match(self, match_id: str):
        doc = self.db.matches.find_one({"_id": oid(match_id)})
        if not doc:
            return None
        d = str_id(doc)
        return {
            "id": d["id"],
            "utc_date": d["utcDate"].date().isoformat(),
            "matchday": d["matchday"],
            "season": str(d.get("seasonId")),
            "home_team_id": str(d["homeTeamId"]),
            "away_team_id": str(d["awayTeamId"]),
            "score": {
                "half_time": {"home": d["score"]["halfTime"]["home"], "away": d["score"]["halfTime"]["away"]},
                "full_time": {"home": d["score"]["fullTime"]["home"], "away": d["score"]["fullTime"]["away"]},
            },
            "statistics": d.get("statistics") or {},
            "referees": [],
        }

    def match_label(self, match: Mapping[str, Any]) -> str:
        return str(match.get("label") or "")

    # ---- CRUD (opcjonalnie później) ----
    def create_league(self, data: Payload): raise NotImplementedError
    def update_league(self, league_id: str, data: Payload): raise NotImplementedError
    def delete_league(self, league_id: str) -> bool: raise NotImplementedError

    def create_team(self, data: Payload): raise NotImplementedError
    def update_team(self, team_id: str, data: Payload): raise NotImplementedError
    def delete_team(self, team_id: str) -> bool: raise NotImplementedError

    def create_player(self, data: Payload): raise NotImplementedError
    def update_player(self, player_id: str, data: Payload): raise NotImplementedError
    def delete_player(self, player_id: str) -> bool: raise NotImplementedError

    def create_match(self, data: Payload): raise NotImplementedError
    def update_match(self, match_id: str, data: Payload): raise NotImplementedError
    def delete_match(self, match_id: str) -> bool: raise NotImplementedError
