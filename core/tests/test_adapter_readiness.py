import inspect
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

import core.views
from core.repositories.factory import get_repo
import core.repositories.factory as repo_factory
from core.repositories.adapters.mock import MockAdapter
from core.repositories.adapters.postgres import PostgresAdapter
from core.repositories.adapters.mongo import MongoAdapter


@override_settings(SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies")
class AdapterReadinessTests(SimpleTestCase):
    def setUp(self):
        # Fabryka ma singleton – resetujemy, żeby każdy test był niezależny.
        repo_factory._repo_singleton = None

    def test_views_use_factory_not_direct_mock_repo(self):
        """
        Gwarancja architektury:
        views.py nie powinien importować mock_repo bezpośrednio.
        """
        src = inspect.getsource(core.views)
        self.assertIn("get_repo", src)
        self.assertNotIn("mock_repo", src)
        self.assertNotIn("from .repositories import mock_repo", src)

    @override_settings(DATA_BACKEND="mock")
    def test_factory_returns_mock_adapter(self):
        repo_factory._repo_singleton = None
        repo = get_repo()
        self.assertIsInstance(repo, MockAdapter)

    @override_settings(DATA_BACKEND="postgres", POSTGRES_DSN="postgresql://example")
    def test_factory_returns_postgres_adapter(self):
        repo_factory._repo_singleton = None
        repo = get_repo()
        self.assertIsInstance(repo, PostgresAdapter)

    @override_settings(DATA_BACKEND="mongo", MONGO_URI="mongodb://example", MONGO_DB="db")
    def test_factory_returns_mongo_adapter(self):
        repo_factory._repo_singleton = None
        repo = get_repo()
        self.assertIsInstance(repo, MongoAdapter)

    @override_settings(DATA_BACKEND="mock")
    def test_mock_adapter_contract_for_matches_list_contains_label(self):
        """
        Przygotowanie pod adaptery = widoki i template'y nie powinny robić 'logiki wzbogacania'.
        MockAdapter powinien zwracać dane w formacie gotowym dla template'ów.
        """
        repo_factory._repo_singleton = None
        repo = get_repo()
        matches = repo.list_matches()
        self.assertTrue(len(matches) >= 1)
        self.assertIn("label", matches[0])  # template listy meczów używa label

    def test_postgres_and_mongo_adapters_exist_and_are_stubs(self):
        """
        Gotowość do adapterów = są klasy adapterów i da się je importować/instancjować.
        Na razie mogą rzucać NotImplementedError.
        """
        pg = PostgresAdapter(dsn="postgresql://example")
        mg = MongoAdapter(uri="mongodb://example", db_name="db")

        with self.assertRaises(NotImplementedError):
            pg.list_leagues()

        with self.assertRaises(NotImplementedError):
            mg.list_leagues()

    @override_settings(DATA_BACKEND="mock")
    def test_admin_views_call_repo_methods_not_inline_logic(self):
        """
        Sprawdza, że CRUD w adminie jest spięty przez repo (adapter),
        a nie zaszyty w widokach.
        """
        # logujemy się jako admin (ustawia role w sesji)
        r = self.client.post("/login/", {"username": "admin", "password": "x"}, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "rola: admin")

        fake_repo = Mock()
        fake_repo.list_leagues.return_value = []
        fake_repo.get_league.return_value = None
        fake_repo.create_league.return_value = {"id": 999, "name": "X", "country": "Y"}

        # Patchujemy get_repo używany w views, żeby mieć pewność, że widoki wołają repo.
        with patch("core.views.get_repo", return_value=fake_repo):
            # GET listy
            r = self.client.get("/manage/leagues/")
            self.assertEqual(r.status_code, 200)
            fake_repo.list_leagues.assert_called()

            # POST create (powinien wywołać create_league i zrobić redirect)
            r = self.client.post("/manage/leagues/new/", {"name": "Nowa", "country": "PL"})
            self.assertEqual(r.status_code, 302)
            fake_repo.create_league.assert_called()

    @override_settings(DATA_BACKEND="mock")
    def test_switching_backend_does_not_break_urls_in_mock_mode(self):
        """
        Minimalna gwarancja: przy mock backendzie cała nawigacja nadal działa.
        """
        for url in ["/", "/leagues/", "/teams/", "/players/", "/matches/"]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)
