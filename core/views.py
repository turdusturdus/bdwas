from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from .repositories import mock_repo as repo

def get_role(request):
    # role: guest | user | admin
    return request.session.get("role", "guest")

def require_admin(request):
    if get_role(request) != "admin":
        return False
    return True

# ---- Errors ----
def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)

def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)

# ---- Dashboard ----
def home(request):
    role = get_role(request)
    ctx = {
        "role": role,
        "counts": {
            "leagues": len(repo.list_leagues()),
            "teams": len(repo.list_teams()),
            "players": len(repo.list_players()),
            "matches": len(repo.list_matches()),
        }
    }
    return render(request, "dashboard/home.html", ctx)

# ---- Auth (statycznie/session) ----
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        # Prosta atrapa: admin jeśli wpiszesz "admin"
        request.session["role"] = "admin" if username.lower() == "admin" else "user"
        return redirect("home")
    return render(request, "auth/login.html", {"role": get_role(request)})

def logout_view(request):
    request.session["role"] = "guest"
    return redirect("home")

# ---- Browse + Search/Filter (q=...) ----
def leagues_list(request):
    q = request.GET.get("q")
    items = repo.list_leagues(q=q)
    return render(request, "leagues/list.html", {"role": get_role(request), "items": items, "q": q})

def league_detail(request, league_id: int):
    league = repo.get_league(league_id)
    if not league:
        return error_404(request)
    teams = [t for t in repo.list_teams() if t["league_id"] == league_id]
    return render(request, "leagues/detail.html", {"role": get_role(request), "league": league, "teams": teams})

def teams_list(request):
    q = request.GET.get("q")
    items = repo.list_teams(q=q)
    return render(request, "teams/list.html", {"role": get_role(request), "items": items, "q": q})

def team_detail(request, team_id: int):
    team = repo.get_team(team_id)
    if not team:
        return error_404(request)
    players = repo.team_players(team_id)
    return render(request, "teams/detail.html", {"role": get_role(request), "team": team, "players": players})

def players_list(request):
    q = request.GET.get("q")
    items = repo.list_players(q=q)
    return render(request, "players/list.html", {"role": get_role(request), "items": items, "q": q})

def player_detail(request, player_id: int):
    player = repo.get_player(player_id)
    if not player:
        return error_404(request)
    team = repo.get_team(player["team_id"])
    return render(request, "players/detail.html", {"role": get_role(request), "player": player, "team": team})

def matches_list(request):
    q = request.GET.get("q")
    items = repo.list_matches(q=q)
    # dodajmy label, żeby ładnie wyglądało
    enriched = []
    for m in items:
        m2 = dict(m)
        m2["label"] = repo.match_label(m)
        enriched.append(m2)
    return render(request, "matches/list.html", {"role": get_role(request), "items": enriched, "q": q})

def match_detail(request, match_id: int):
    match = repo.get_match(match_id)
    if not match:
        return error_404(request)
    home = repo.get_team(match["home_team_id"])
    away = repo.get_team(match["away_team_id"])
    return render(request, "matches/detail.html", {
        "role": get_role(request),
        "match": match,
        "home": home,
        "away": away,
    })

# ---- Admin CRUD (atrapy) ----
def admin_index(request):
    if not require_admin(request):
        return HttpResponseForbidden(render(request, "errors/403.html"))
    return render(request, "adminpanel/index.html", {"role": get_role(request)})

# LEAGUES
def admin_leagues_list(request):
    if not require_admin(request):
        return error_403(request)
    return render(request, "adminpanel/leagues_list.html", {"role": get_role(request), "items": repo.list_leagues()})

def admin_leagues_form(request, league_id=None):
    if not require_admin(request):
        return error_403(request)
    league = repo.get_league(league_id) if league_id else None
    if request.method == "POST":
        return redirect("admin_leagues_list")
    return render(request, "adminpanel/leagues_form.html", {"role": get_role(request), "item": league})

def admin_leagues_delete(request, league_id: int):
    if not require_admin(request):
        return error_403(request)
    league = repo.get_league(league_id)
    if request.method == "POST":
        return redirect("admin_leagues_list")
    return render(request, "adminpanel/confirm_delete.html", {"role": get_role(request), "entity": "Liga", "item": league, "back_url": "admin_leagues_list"})

# TEAMS
def admin_teams_list(request):
    if not require_admin(request):
        return error_403(request)
    return render(request, "adminpanel/teams_list.html", {"role": get_role(request), "items": repo.list_teams()})

def admin_teams_form(request, team_id=None):
    if not require_admin(request):
        return error_403(request)
    team = repo.get_team(team_id) if team_id else None
    if request.method == "POST":
        return redirect("admin_teams_list")
    return render(request, "adminpanel/teams_form.html", {"role": get_role(request), "item": team})

def admin_teams_delete(request, team_id: int):
    if not require_admin(request):
        return error_403(request)
    team = repo.get_team(team_id)
    if request.method == "POST":
        return redirect("admin_teams_list")
    return render(request, "adminpanel/confirm_delete.html", {"role": get_role(request), "entity": "Drużyna", "item": team, "back_url": "admin_teams_list"})

# PLAYERS
def admin_players_list(request):
    if not require_admin(request):
        return error_403(request)
    return render(request, "adminpanel/players_list.html", {"role": get_role(request), "items": repo.list_players()})

def admin_players_form(request, player_id=None):
    if not require_admin(request):
        return error_403(request)
    player = repo.get_player(player_id) if player_id else None
    if request.method == "POST":
        return redirect("admin_players_list")
    return render(request, "adminpanel/players_form.html", {"role": get_role(request), "item": player})

def admin_players_delete(request, player_id: int):
    if not require_admin(request):
        return error_403(request)
    player = repo.get_player(player_id)
    if request.method == "POST":
        return redirect("admin_players_list")
    return render(request, "adminpanel/confirm_delete.html", {"role": get_role(request), "entity": "Zawodnik", "item": player, "back_url": "admin_players_list"})

# MATCHES
def admin_matches_list(request):
    if not require_admin(request):
        return error_403(request)
    items = repo.list_matches()
    enriched = []
    for m in items:
        m2 = dict(m)
        m2["label"] = repo.match_label(m)
        enriched.append(m2)
    return render(request, "adminpanel/matches_list.html", {"role": get_role(request), "items": enriched})

def admin_matches_form(request, match_id=None):
    if not require_admin(request):
        return error_403(request)
    match = repo.get_match(match_id) if match_id else None
    if request.method == "POST":
        return redirect("admin_matches_list")
    return render(request, "adminpanel/matches_form.html", {"role": get_role(request), "item": match})

def admin_matches_delete(request, match_id: int):
    if not require_admin(request):
        return error_403(request)
    match = repo.get_match(match_id)
    if request.method == "POST":
        return redirect("admin_matches_list")
    return render(request, "adminpanel/confirm_delete.html", {"role": get_role(request), "entity": "Mecz", "item": match, "back_url": "admin_matches_list"})
