from __future__ import annotations

import os
from django.conf import settings

from .base import LeagueRepo
from .adapters.mock import MockAdapter
from .adapters.postgres import PostgresAdapter
from .adapters.mongo import MongoAdapter
from .adapters.mysql import MysqlAdapter

_repo_singleton: LeagueRepo | None = None


def get_repo() -> LeagueRepo:
    """
    Jedno miejsce wyboru backendu danych.
    Widoki nie wiedzą, czy dane są z mocka, Postgresa czy Mongo.
    """
    global _repo_singleton
    if _repo_singleton is not None:
        return _repo_singleton

    backend = getattr(settings, "DATA_BACKEND", "mock")

    if backend == "mock":
        _repo_singleton = MockAdapter()
        return _repo_singleton

    if backend == "postgres":
        dsn = getattr(settings, "POSTGRES_DSN", os.environ.get("POSTGRES_DSN", ""))

        if not dsn:
            raise ValueError("Brak POSTGRES_DSN w ustawieniach lub zmiennych środowiskowych.")

        _repo_singleton = PostgresAdapter(dsn=dsn)
        return _repo_singleton

    if backend == "mongo":
        _repo_singleton = MongoAdapter(
            uri=getattr(settings, "MONGO_URI", ""),
            db_name=getattr(settings, "MONGO_DB", ""),
        )
        return _repo_singleton

    if backend == "mysql":
        uri = getattr(settings, "MYSQL_URI", os.environ.get("MYSQL_URI", ""))
        if not uri:
            raise ValueError("Brak MYSQL_URI w ustawieniach lub zmiennych środowiskowych.")
        _repo_singleton = MysqlAdapter(uri=uri)
        return _repo_singleton

    raise ValueError(f"Nieznany DATA_BACKEND={backend}. Użyj: mock|postgres|mongo|mysql.")