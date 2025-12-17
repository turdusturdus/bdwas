from django.test import SimpleTestCase, override_settings


# Ustawiamy sesje na cookies, żeby testy NIE wymagały bazy sesji.
# (To nadal nie testuje integracji z waszą bazą domenową – tylko zachowanie UI/flow).
@override_settings(SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies")
class StaticAppTests(SimpleTestCase):
    def test_home_page_ok(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Dashboard")

    def test_guest_can_browse_lists(self):
        for url, title in [
            ("/leagues/", "Ligi"),
            ("/teams/", "Drużyny"),
            ("/players/", "Zawodnicy"),
            ("/matches/", "Mecze"),
        ]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, f"<h1>{title}</h1>", html=True)

    def test_leagues_search_filter_q(self):
        # powinno znaleźć "Ekstraklasa"
        r = self.client.get("/leagues/?q=ekstra")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Ekstraklasa")

        # powinno znaleźć po kraju "Anglia" -> Premier League
        r = self.client.get("/leagues/?q=anglia")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Premier League")

    def test_teams_search_filter_q(self):
        r = self.client.get("/teams/?q=lech")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Lech Poznań")

    def test_players_search_filter_q(self):
        r = self.client.get("/players/?q=FW")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Jan Kowalski")

    def test_league_detail_ok(self):
        r = self.client.get("/leagues/1/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Ekstraklasa")
        self.assertContains(r, "Drużyny w lidze")

    def test_team_detail_ok(self):
        r = self.client.get("/teams/1/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Legia Warszawa")
        self.assertContains(r, "Zawodnicy")

    def test_player_detail_ok(self):
        r = self.client.get("/players/1/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Jan Kowalski")

    def test_matches_list_and_detail_ok(self):
        r = self.client.get("/matches/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "vs")  # label "Home vs Away"

        r = self.client.get("/matches/1/")
        self.assertEqual(r.status_code, 200)
        # sprawdzamy, że jest sekcja wyników i statystyk
        self.assertContains(r, "Do przerwy")
        self.assertContains(r, "Koniec")
        self.assertContains(r, "Statystyki")

    def test_login_sets_user_role_and_logout_resets(self):
        # Gość widzi "Zaloguj"
        r = self.client.get("/")
        self.assertContains(r, "Zaloguj")

        # Logowanie jako zwykły user
        r = self.client.post("/login/", {"username": "user", "password": "x"}, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "rola: user")
        self.assertContains(r, "Wyloguj")

        # Logout -> guest
        r = self.client.get("/logout/", follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "rola: guest")
        self.assertContains(r, "Zaloguj")

    def test_admin_access_control(self):
        # gość nie ma dostępu
        r = self.client.get("/manage/")
        self.assertEqual(r.status_code, 403)

        r = self.client.get("/manage/leagues/")
        self.assertEqual(r.status_code, 403)

        # logowanie jako admin
        r = self.client.post("/login/", {"username": "admin", "password": "x"}, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "rola: admin")

        # admin ma dostęp
        r = self.client.get("/manage/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Panel administratora")

        # CRUD listy działają (atrapy)
        for url in ["/manage/leagues/", "/manage/teams/", "/manage/players/", "/manage/matches/"]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)

    def test_not_found_returns_404_template(self):
        r = self.client.get("/leagues/9999/")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "404", status_code=404)

