from __future__ import annotations

from django.conf import settings

from .base import LeagueRepo
from .adapters.mock import MockAdapter
from .adapters.postgres import PostgresAdapter
from .adapters.mongo import MongoAdapter

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
        _repo_singleton = PostgresAdapter(dsn=getattr(settings, "POSTGRES_DSN", ""))
        return _repo_singleton

    if backend == "mongo":
        _repo_singleton = MongoAdapter(
            uri=getattr(settings, "MONGO_URI", ""),
            db_name=getattr(settings, "MONGO_DB", ""),
        )
        return _repo_singleton

    raise ValueError(f"Nieznany DATA_BACKEND={backend}. Użyj: mock|postgres|mongo.")
