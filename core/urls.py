from django.urls import path, register_converter
from .converters import ObjectIdConverter
from . import views

# register_converter(ObjectIdConverter, "oid")

urlpatterns = [
    path("", views.home, name="home"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("leagues/", views.leagues_list, name="leagues_list"),
    path("leagues/<str:league_id>/", views.league_detail, name="league_detail"),

    path("teams/", views.teams_list, name="teams_list"),
    path("teams/<str:team_id>/", views.team_detail, name="team_detail"),

    path("players/", views.players_list, name="players_list"),
    path("players/<str:player_id>/", views.player_detail, name="player_detail"),

    path("matches/", views.matches_list, name="matches_list"),
    path("matches/<str:match_id>/", views.match_detail, name="match_detail"),

    path("manage/", views.admin_index, name="admin_index"),

    path("manage/leagues/", views.admin_leagues_list, name="admin_leagues_list"),
    path("manage/leagues/new/", views.admin_leagues_form, name="admin_leagues_new"),
    path("manage/leagues/<str:league_id>/edit/", views.admin_leagues_form, name="admin_leagues_edit"),
    path("manage/leagues/<str:league_id>/delete/", views.admin_leagues_delete, name="admin_leagues_delete"),

    path("manage/teams/", views.admin_teams_list, name="admin_teams_list"),
    path("manage/teams/new/", views.admin_teams_form, name="admin_teams_new"),
    path("manage/teams/<str:team_id>/edit/", views.admin_teams_form, name="admin_teams_edit"),
    path("manage/teams/<str:team_id>/delete/", views.admin_teams_delete, name="admin_teams_delete"),

    path("manage/players/", views.admin_players_list, name="admin_players_list"),
    path("manage/players/new/", views.admin_players_form, name="admin_players_new"),
    path("manage/players/<str:player_id>/edit/", views.admin_players_form, name="admin_players_edit"),
    path("manage/players/<str:player_id>/delete/", views.admin_players_delete, name="admin_players_delete"),

    path("manage/matches/", views.admin_matches_list, name="admin_matches_list"),
    path("manage/matches/new/", views.admin_matches_form, name="admin_matches_new"),
    path("manage/matches/<str:match_id>/edit/", views.admin_matches_form, name="admin_matches_edit"),
    path("manage/matches/<str:match_id>/delete/", views.admin_matches_delete, name="admin_matches_delete"),
]
