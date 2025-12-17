LEAGUES = [
  {"id": "507f1f77bcf86cd799439011", "name": "Ekstraklasa", "country": "Polska"},
  {"id": "507f1f77bcf86cd799439012", "name": "Premier League", "country": "Anglia"},
]

TEAMS = [
  {"id": "507f1f77bcf86cd799439101", "name": "Legia Warszawa", "founded_year": 1916, "coach": "Trener A", "stadium": "Stadion A", "league_id": LEAGUES[0]["id"]},
  {"id": "507f1f77bcf86cd799439102", "name": "Lech Poznań", "founded_year": 1922, "coach": "Trener B", "stadium": "Stadion B", "league_id": LEAGUES[0]["id"]},
]

PLAYERS = [
  {"id": "507f1f77bcf86cd799439201", "name": "Jan Kowalski", "position": "FW", "team_id": TEAMS[0]["id"], "nationality": "Polska"},
  {"id": "507f1f77bcf86cd799439202", "name": "Piotr Nowak", "position": "MF", "team_id": TEAMS[1]["id"], "nationality": "Polska"},
]

MATCHES = [
  {
    "id": "507f1f77bcf86cd799439301",
    "utc_date": "2025-01-10",
    "matchday": 12,
    "league_id": LEAGUES[0]["id"],
    "season": "2024/2025",
    "home_team_id": TEAMS[0]["id"],
    "away_team_id": TEAMS[1]["id"],
    "score": {"half_time": {"home": 1, "away": 0}, "full_time": {"home": 2, "away": 1}},
    "statistics": {"possession": {"home": 55, "away": 45}},
    "referees": [{"name": "Sędzia X", "role": "MAIN"}],
  }
]

def _filter_q(items, q, fields):
  if not q:
    return items
  ql = q.lower()
  return [it for it in items if ql in " ".join(str(it.get(f, "")) for f in fields).lower()]

def list_leagues(q=None): return _filter_q(LEAGUES, q, ["name", "country"])
def get_league(league_id: str): return next((l for l in LEAGUES if l["id"] == league_id), None)

def list_teams(q=None): return _filter_q(TEAMS, q, ["name", "coach", "stadium"])
def get_team(team_id: str): return next((t for t in TEAMS if t["id"] == team_id), None)

def list_players(q=None): return _filter_q(PLAYERS, q, ["name", "position", "nationality"])
def get_player(player_id: str): return next((p for p in PLAYERS if p["id"] == player_id), None)

def list_matches(q=None): return MATCHES
def get_match(match_id: str): return next((m for m in MATCHES if m["id"] == match_id), None)

def team_players(team_id: str): return [p for p in PLAYERS if p["team_id"] == team_id]
def match_label(match):
  home = get_team(match["home_team_id"])["name"]
  away = get_team(match["away_team_id"])["name"]
  return f"{home} vs {away}"
