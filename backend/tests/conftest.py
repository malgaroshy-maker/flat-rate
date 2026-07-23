"""Shared fixtures for backend tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from main import app
import dictionary_store as dictionary_store_module


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def isolate_dictionary_store(tmp_path, monkeypatch):
    """dictionary_store is a module-level singleton backed by the real
    backend/data/dictionary.json — live production data served to real
    users via /api/dictionary. Without this, every test run (test_create_term,
    test_list_terms, test_add_pending, ...) writes real API calls straight
    into that file, permanently accumulating junk entries like
    "فرامل_اختبار" and duplicate "باطني" rows. Point the singleton at an
    empty temp file for the duration of each test and restore its real
    in-memory state after, so tests never touch the real data.
    """
    store = dictionary_store_module.dictionary_store
    real_terms, real_pending = store._terms, store._pending
    real_storage_file = dictionary_store_module.STORAGE_FILE

    monkeypatch.setattr(dictionary_store_module, "STORAGE_FILE", tmp_path / "dictionary.json")
    store._terms, store._pending = {}, {}

    yield

    store._terms, store._pending = real_terms, real_pending
    monkeypatch.setattr(dictionary_store_module, "STORAGE_FILE", real_storage_file)
