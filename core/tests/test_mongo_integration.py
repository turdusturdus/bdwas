import os
from unittest import SkipTest

from django.test import SimpleTestCase, override_settings, tag
from pymongo import MongoClient

import core.repositories.factory as repo_factory


@tag("mongo")
@override_settings(
    DATA_BACKEND="mongo",
    SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies",
    # domyślnie po nazwie kontenera w docker-compose (u Ciebie: bdwas_mongo)
    MONGO_URI=os.getenv("MONGO_URI_TEST", "mongodb://bdwas_mongo:27017"),
    MONGO_DB=os.getenv("MONGO_DB_TEST", "football_app"),
)
class MongoIntegrationTests(SimpleTestCase):
    # te same ID co seed + mock_repo
    L1 = "507f1f77bcf86cd799439011"
    T1 = "507f1f77bcf86cd799439101"
    P1 = "507f1f77bcf86cd799439201"
    M1 = "507f1f77bcf86cd799439301"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        uri = os.getenv("MONGO_URI_TEST", "mongodb://bdwas_mongo:27017")
        dbn = os.getenv("MONGO_DB_TEST", "football_app")

        try:
            c = MongoClient(uri, serverSelectionTimeoutMS=1000)
            c.admin.command("ping")
            if c[dbn].leagues.count_documents({}) == 0:
                raise SkipTest("Mongo działa, ale DB jest pusta (seed nie załadowany?).")
        except SkipTest:
            raise
        except Exception as e:
            raise SkipTest(f"Mongo niedostępne: {e}")

    def setUp(self):
        # Fabryka ma singleton – resetujemy, żeby backend/ustawienia były brane świeżo
        repo_factory._repo_singleton = None

    def test_leagues_list_ok(self):
        r = self.client.get("/leagues/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Ekstraklasa")

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

    def test_match_detail_ok(self):
        r = self.client.get(f"/matches/{self.M1}/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Do przerwy")
        self.assertContains(r, "Koniec")
        self.assertContains(r, "Statystyki")
