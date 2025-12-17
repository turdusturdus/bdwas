from django.test import SimpleTestCase, override_settings

@override_settings(
    SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies",
    DATA_BACKEND="mock",
)
class StaticAppTests(SimpleTestCase):
    L1 = "507f1f77bcf86cd799439011"
    T1 = "507f1f77bcf86cd799439101"
    P1 = "507f1f77bcf86cd799439201"
    M1 = "507f1f77bcf86cd799439301"

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

    def test_league_detail_ok(self):
        r = self.client.get(f"/leagues/{self.L1}/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Ekstraklasa")

    def test_team_detail_ok(self):
        r = self.client.get(f"/teams/{self.T1}/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Legia Warszawa")

    def test_player_detail_ok(self):
        r = self.client.get(f"/players/{self.P1}/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Jan Kowalski")

    def test_matches_list_and_detail_ok(self):
        r = self.client.get("/matches/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "vs")

        r = self.client.get(f"/matches/{self.M1}/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Do przerwy")
        self.assertContains(r, "Koniec")
        self.assertContains(r, "Statystyki")
