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


    def create_league(self, data: Payload):
        country_id = data.get("country_id")
        doc = {
            "name": data.get("name"),
            "countryId": oid(country_id) if country_id else None,
            "iconUrl": data.get("icon_url", ""),
            "europeanSpots": {
                "championsLeague": int(data.get("cl_spot") or 0),
                "europaLeague": int(data.get("uel_spot") or 0),
                "relegation": int(data.get("relegation_spot") or 0),
            },
        }
        res = self.db.leagues.insert_one(doc)
        return {**data, "id": str(res.inserted_id)}

    def update_league(self, league_id: str, data: Payload):
        country_id = data.get("country_id")
        update = {
            "name": data.get("name"),
            "countryId": oid(country_id) if country_id else None,

        }

        self.db.leagues.update_one(
            {"_id": oid(league_id)},
            {"$set": update}
        )
        return self.get_league(league_id)

    def delete_league(self, league_id: str) -> bool:
        self.db.leagues.delete_one({"_id": oid(league_id)})
        return True

    def create_team(self, data: Payload):
        stadium_name = data.get("stadium_id")
        coach_name = data.get("coach_id")
        
        stadium_doc = {"name": stadium_name or "Unknown", "location": "Unknown", "capacity": 0}
        
        # Get default nationality if needed
        first_country = self.db.countries.find_one()
        default_nat_id = first_country["_id"] if first_country else None
        
        coach_doc = {"name": coach_name or "Unknown", "nationalityId": default_nat_id}

        # Inherit details if stadium/coach exists in another team
        if stadium_name:
            existing = self.db.teams.find_one({"stadium.name": stadium_name}, {"stadium": 1})
            if existing:
                stadium_doc = existing.get("stadium", stadium_doc)

        if coach_name:
            existing = self.db.teams.find_one({"coach.name": coach_name}, {"coach": 1})
            if existing:
                coach_doc = existing.get("coach", coach_doc)

        doc = {
            "name": data.get("name"),
            "foundedYear": int(data.get("founded_year") or 1900),
            "crestUrl": "",
            "countryId": default_nat_id,
            "leagueId": oid(data.get("league_id")) if data.get("league_id") else None,
            "stadium": stadium_doc,
            "coach": coach_doc
        }
        
        # Infer countryId from league if possible
        if doc["leagueId"]:
            league = self.db.leagues.find_one({"_id": doc["leagueId"]})
            if league:
                doc["countryId"] = league.get("countryId")

        res = self.db.teams.insert_one(doc)
        return {**data, "id": str(res.inserted_id)}

    def update_team(self, team_id: str, data: Payload):
        stadium_name = data.get("stadium_id")
        coach_name = data.get("coach_id")
        

        old_team = self.db.teams.find_one({"_id": oid(team_id)})
        
        stadium_doc = old_team.get("stadium") if old_team else {"name": "Unknown", "location": "Unknown", "capacity": 0}
        if stadium_name and stadium_doc["name"] != stadium_name:
             # Look for existing stadium details or reset
             existing = self.db.teams.find_one({"stadium.name": stadium_name}, {"stadium": 1})
             if existing:
                 stadium_doc = existing.get("stadium")
             else:
                 stadium_doc = {"name": stadium_name, "location": "Unknown", "capacity": 0}

        coach_doc = old_team.get("coach") if old_team else {"name": "Unknown", "nationalityId": None}
        if coach_name and coach_doc.get("name") != coach_name:
             existing = self.db.teams.find_one({"coach.name": coach_name}, {"coach": 1})
             if existing:
                 coach_doc = existing.get("coach")
             else:
                 # Need valid nationalityId
                 first_country = self.db.countries.find_one()
                 nid = first_country["_id"] if first_country else None
                 coach_doc = {"name": coach_name, "nationalityId": nid}

        update = {
            "name": data.get("name"),
            "foundedYear": int(data.get("founded_year") or 1900),
            "stadium": stadium_doc,
            "coach": coach_doc,
        }
        
        self.db.teams.update_one({"_id": oid(team_id)}, {"$set": update})
        return self.get_team(team_id)

    def delete_team(self, team_id: str) -> bool:
        self.db.teams.delete_one({"_id": oid(team_id)})
        return True

    def create_player(self, data: Payload):
        doc = {
            "name": data.get("name"),
            "position": data.get("position"),
            "dateOfBirth": datetime.now(),
            "nationalityId": oid(data.get("nationality_id")) if data.get("nationality_id") else None,
            "currentTeamId": oid(data.get("team_id")) if data.get("team_id") else None,
        }
        res = self.db.players.insert_one(doc)
        return {**data, "id": str(res.inserted_id)}

    def update_player(self, player_id: str, data: Payload):
        update = {
            "name": data.get("name"),
            "position": data.get("position"),
            "nationalityId": oid(data.get("nationality_id")) if data.get("nationality_id") else None,
            "currentTeamId": oid(data.get("team_id")) if data.get("team_id") else None,
        }
        self.db.players.update_one({"_id": oid(player_id)}, {"$set": update})
        return self.get_player(player_id)

    def delete_player(self, player_id: str) -> bool:
        self.db.players.delete_one({"_id": oid(player_id)})
        return True

    def create_match(self, data: Payload):
        doc = {
            "utcDate": datetime.fromisoformat(data.get("utc_date")) if data.get("utc_date") else datetime.now(),
            "matchday": int(data.get("matchday") or 1),
            "seasonId": oid(data.get("season_id")) if data.get("season_id") else None,
            "homeTeamId": oid(data.get("home_team_id")),
            "awayTeamId": oid(data.get("away_team_id")),
            "score": {
                "halfTime": {"home": 0, "away": 0},
                "fullTime": {"home": 0, "away": 0},
                "winner": None
            },
            "statistics": None,
            "referees": []
        }
        res = self.db.matches.insert_one(doc)
        return {**data, "id": str(res.inserted_id)}

    def update_match(self, match_id: str, data: Payload):
        update = {
            "utcDate": datetime.fromisoformat(data.get("utc_date")) if data.get("utc_date") else datetime.now(),
            "matchday": int(data.get("matchday") or 1),
        }
        if data.get("home_team_id"):
            update["homeTeamId"] = oid(data.get("home_team_id"))
        if data.get("away_team_id"):
            update["awayTeamId"] = oid(data.get("away_team_id"))
            
        self.db.matches.update_one({"_id": oid(match_id)}, {"$set": update})
        return self.get_match(match_id)

    def delete_match(self, match_id: str) -> bool:
        self.db.matches.delete_one({"_id": oid(match_id)})
        return True

    # Helper methods for form dropdowns
    def list_countries(self) -> list[dict]:
        out = []
        for x in self.db.countries.find().sort("name", 1):
             out.append({"id": str(x["_id"]), "name": x["name"]})
        return out

    def list_stadiums(self) -> list[dict]:

        pipeline = [
            {"$group": {"_id": "$stadium.name", "doc": {"$first": "$stadium"}}},
            {"$sort": {"_id": 1}}
        ]
        out = []
        for x in self.db.teams.aggregate(pipeline):
             s = x.get("doc")
             if s and s.get("name"):
                 # Use name as ID because we don't have separate stadium IDs
                 out.append({"id": s["name"], "name": s["name"], "location": s.get("location")})
        return out

    def list_coaches(self) -> list[dict]:

        pipeline = [
            {"$group": {"_id": "$coach.name", "doc": {"$first": "$coach"}}},
            {"$lookup": {"from": "countries", "localField": "doc.nationalityId", "foreignField": "_id", "as": "nat"}},
            {"$unwind": {"path": "$nat", "preserveNullAndEmptyArrays": True}},
            {"$sort": {"_id": 1}}
        ]
        out = []
        for x in self.db.teams.aggregate(pipeline):
             c = x.get("doc")
             if c and c.get("name"):
                 nat_name = x.get("nat", {}).get("name", "")
                 out.append({"id": c["name"], "name": c["name"], "nationality": nat_name})
        return out

    def list_seasons(self) -> list[dict]:
        out = []

        pipeline = [
             {"$lookup": {"from": "leagues", "localField": "leagueId", "foreignField": "_id", "as": "league"}},
             {"$unwind": {"path": "$league", "preserveNullAndEmptyArrays": True}},
             {"$sort": {"year": -1}}
        ]
        for x in self.db.seasons.aggregate(pipeline):
             x = str_id(x)
             l_name = x.get("league", {}).get("name", "Unknown")
             out.append({"id": x["id"], "year": x.get("year"), "league_name": l_name})
        return out
