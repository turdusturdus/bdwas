from django.shortcuts import render, redirect
from .repositories.factory import get_repo

def get_role(request): return request.session.get("role", "guest")
def require_admin(request): return get_role(request) == "admin"

def error_403(request, exception=None): return render(request, "errors/403.html", status=403)
def error_404(request, exception=None): return render(request, "errors/404.html", status=404)
def error_500(request): return render(request, "errors/500.html", status=500)

def home(request):
    repo = get_repo()
    role = get_role(request)
    return render(request, "dashboard/home.html", {
        "role": role,
        "counts": {
            "leagues": len(repo.list_leagues()),
            "teams": len(repo.list_teams()),
            "players": len(repo.list_players()),
            "matches": len(repo.list_matches()),
        }
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        request.session["role"] = "admin" if username.lower() == "admin" else "user"
        return redirect("home")
    return render(request, "auth/login.html", {"role": get_role(request)})

def logout_view(request):
    request.session["role"] = "guest"
    return redirect("home")

def leagues_list(request):
    repo = get_repo()
    q = request.GET.get("q")
    return render(request, "leagues/list.html", {"role": get_role(request), "items": repo.list_leagues(q=q), "q": q})

def league_detail(request, league_id: str):
    repo = get_repo()
    league = repo.get_league(league_id)
    if not league: return error_404(request)
    teams = [t for t in repo.list_teams() if str(t.get("league_id")) == str(league_id)]
    return render(request, "leagues/detail.html", {"role": get_role(request), "league": league, "teams": teams})

def teams_list(request):
    repo = get_repo()
    q = request.GET.get("q")
    return render(request, "teams/list.html", {"role": get_role(request), "items": repo.list_teams(q=q), "q": q})

def team_detail(request, team_id: str):
    repo = get_repo()
    team = repo.get_team(team_id)
    if not team: return error_404(request)
    players = repo.team_players(team_id)
    return render(request, "teams/detail.html", {"role": get_role(request), "team": team, "players": players})

def players_list(request):
    repo = get_repo()
    q = request.GET.get("q")
    return render(request, "players/list.html", {"role": get_role(request), "items": repo.list_players(q=q), "q": q})

def player_detail(request, player_id: str):
    repo = get_repo()
    player = repo.get_player(player_id)
    if not player: return error_404(request)
    team = repo.get_team(str(player.get("currentTeamId") or player.get("team_id") or ""))
    return render(request, "players/detail.html", {"role": get_role(request), "player": player, "team": team})

def matches_list(request):
    repo = get_repo()
    q = request.GET.get("q")
    return render(request, "matches/list.html", {"role": get_role(request), "items": repo.list_matches(q=q), "q": q})

def match_detail(request, match_id: str):
    repo = get_repo()
    match = repo.get_match(match_id)
    if not match: return error_404(request)
    home = repo.get_team(match["home_team_id"])
    away = repo.get_team(match["away_team_id"])
    return render(request, "matches/detail.html", {"role": get_role(request), "match": match, "home": home, "away": away})

# Admin jak było – tylko typy id zmienione na str
def admin_index(request):
    if not require_admin(request): return error_403(request)
    return render(request, "adminpanel/index.html", {"role": get_role(request)})

def admin_leagues_list(request):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    return render(request, "adminpanel/leagues_list.html", {"role": get_role(request), "items": repo.list_leagues()})

def admin_leagues_form(request, league_id=None):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    item = repo.get_league(league_id) if league_id else None
    countries = repo.list_countries()
    if request.method == "POST":
        if league_id: repo.update_league(league_id, request.POST)
        else: repo.create_league(request.POST)
        return redirect("admin_leagues_list")
    return render(request, "adminpanel/leagues_form.html", {
        "role": get_role(request), 
        "item": item,
        "countries": countries
    })

def admin_leagues_delete(request, league_id: str):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    item = repo.get_league(league_id)
    if request.method == "POST":
        repo.delete_league(league_id)
        return redirect("admin_leagues_list")
    return render(request, "adminpanel/confirm_delete.html", {"role": get_role(request), "entity": "Liga", "item": item, "back_url": "admin_leagues_list"})

def admin_teams_list(request):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    return render(request, "adminpanel/teams_list.html", {"role": get_role(request), "items": repo.list_teams()})

def admin_teams_form(request, team_id=None):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    item = repo.get_team(team_id) if team_id else None
    coaches = repo.list_coaches()
    stadiums = repo.list_stadiums()
    if request.method == "POST":
        if team_id: repo.update_team(team_id, request.POST)
        else: repo.create_team(request.POST)
        return redirect("admin_teams_list")
    return render(request, "adminpanel/teams_form.html", {
        "role": get_role(request), 
        "item": item,
        "coaches": coaches,
        "stadiums": stadiums
    })

def admin_teams_delete(request, team_id: str):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    item = repo.get_team(team_id)
    if request.method == "POST":
        repo.delete_team(team_id)
        return redirect("admin_teams_list")
    return render(request, "adminpanel/confirm_delete.html", {"role": get_role(request), "entity": "Drużyna", "item": item, "back_url": "admin_teams_list"})

def admin_players_list(request):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    return render(request, "adminpanel/players_list.html", {"role": get_role(request), "items": repo.list_players()})

def admin_players_form(request, player_id=None):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    item = repo.get_player(player_id) if player_id else None
    teams = repo.list_teams()
    countries = repo.list_countries()
    if request.method == "POST":
        if player_id: repo.update_player(player_id, request.POST)
        else: repo.create_player(request.POST)
        return redirect("admin_players_list")
    return render(request, "adminpanel/players_form.html", {
        "role": get_role(request), 
        "item": item,
        "teams": teams,
        "countries": countries
    })

def admin_players_delete(request, player_id: str):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    item = repo.get_player(player_id)
    if request.method == "POST":
        repo.delete_player(player_id)
        return redirect("admin_players_list")
    return render(request, "adminpanel/confirm_delete.html", {"role": get_role(request), "entity": "Zawodnik", "item": item, "back_url": "admin_players_list"})

def admin_matches_list(request):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    return render(request, "adminpanel/matches_list.html", {"role": get_role(request), "items": repo.list_matches()})

def admin_matches_form(request, match_id=None):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    item = repo.get_match(match_id) if match_id else None
    teams = repo.list_teams()
    seasons = repo.list_seasons()
    if request.method == "POST":
        if match_id: repo.update_match(match_id, request.POST)
        else: repo.create_match(request.POST)
        return redirect("admin_matches_list")
    return render(request, "adminpanel/matches_form.html", {
        "role": get_role(request), 
        "item": item,
        "teams": teams,
        "seasons": seasons
    })

def admin_matches_delete(request, match_id: str):
    repo = get_repo()
    if not require_admin(request): return error_403(request)
    item = repo.get_match(match_id)
    if request.method == "POST":
        repo.delete_match(match_id)
        return redirect("admin_matches_list")
    return render(request, "adminpanel/confirm_delete.html", {"role": get_role(request), "entity": "Mecz", "item": item, "back_url": "admin_matches_list"})
