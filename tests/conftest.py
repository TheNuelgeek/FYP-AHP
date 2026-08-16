import importlib

import pytest


class FakeSessionState(dict):
    """Small dict/attribute hybrid matching how the app uses session_state."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


@pytest.fixture(scope="session")
def app_module():
    return importlib.import_module("app")


@pytest.fixture()
def fake_state(monkeypatch, app_module):
    state = FakeSessionState()
    monkeypatch.setattr(app_module.st, "session_state", state)
    return state
