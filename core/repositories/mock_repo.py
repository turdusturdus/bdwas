"""
Mock repo – dzisiaj zwraca dane testowe (statycznie).
Jutro podmienisz implementację na adapter do Postgresa / NoSQL,
ale interfejs (funkcje) zostaje taki sam.
"""

LEAGUES = [
    {"id": 1, "name": "Ekstraklasa", "country": "Polska"},
    {"id": 2, "name": "Premier League", "country": "Anglia"},
]

TEAMS = [
    {"id": 1, "name": "Legia Warszawa", "founded_year": 1916, "coach": "Trener A", "stadium": "Stadion A", "league_id": 1},
    {"id": 2, "name": "Lech Poznań", "founded_year": 1922, "coach": "Trener B", "stadium": "Stadion B", "league_id": 1},
    {"id": 3, "name": "Arsenal", "founded_year": 1886, "coach": "Trener C", "stadium": "Emirates", "league_id": 2},
]

PLAYERS = [
    {"id": 1, "name": "Jan Kowalski", "position": "FW", "team_id": 1, "nationality": "Polska"},
    {"id": 2, "name": "Piotr Nowak", "position": "MF", "team_id": 2, "nationality": "Polska"},
    {"id": 3, "name": "John Smith", "position": "DF", "team_id": 3, "nationality": "Anglia"},
]

MATCHES = [
    {
        "id": 1,
        "utc_date": "2025-01-10",
        "matchday": 12,
        "league_id": 1,
        "season": "2024/2025",
        "home_team_id": 1,
        "away_team_id": 2,
        "score": {"half_time": {"home": 1, "away": 0}, "full_time": {"home": 2, "away": 1}},
        "statistics": {"possession": {"home": 55, "away": 45}, "shots": {"home": 12, "away": 8}},
        "referees": [{"name": "Sędzia X", "role": "MAIN"}],
    }
]

def _filter_q(items, q, fields):
    if not q:
        return items
    q_lower = q.lower()
    out = []
    for it in items:
        blob = " ".join(str(it.get(f, "")) for f in fields).lower()
        if q_lower in blob:
            out.append(it)
    return out

def list_leagues(q=None):
    return _filter_q(LEAGUES, q, ["name", "country"])

def get_league(league_id: int):
    return next((l for l in LEAGUES if l["id"] == league_id), None)

def list_teams(q=None):
    return _filter_q(TEAMS, q, ["name", "coach", "stadium"])

def get_team(team_id: int):
    return next((t for t in TEAMS if t["id"] == team_id), None)

def list_players(q=None):
    return _filter_q(PLAYERS, q, ["name", "position", "nationality"])

def get_player(player_id: int):
    return next((p for p in PLAYERS if p["id"] == player_id), None)

def list_matches(q=None):
    return MATCHES  # można dodać filtr po dacie/klubie później

def get_match(match_id: int):
    return next((m for m in MATCHES if m["id"] == match_id), None)

def team_players(team_id: int):
    return [p for p in PLAYERS if p["team_id"] == team_id]

def match_label(match):
    home = get_team(match["home_team_id"])["name"]
    away = get_team(match["away_team_id"])["name"]
    return f"{home} vs {away}"
