"""Proves the emit-only guarantee: the runtime opens no outbound connections.

Sockets are patched to fail on any real connection attempt, then a targeted
build, a broad build, and an export run end-to-end. The in-process FastAPI
TestClient must still work under the guard (it uses an ASGI transport, not a
real socket).
"""

import socket

import pytest
from fastapi.testclient import TestClient

from dorkforge.export import serialize
from dorkforge.library import load_dorks
from dorkforge.selection import select_and_render
from dorkforge.web.app import app


class _NetworkAttempted(AssertionError):
    pass


_LOOPBACK = {"127.0.0.1", "::1", "localhost", "0.0.0.0", ""}


def _is_loopback(address) -> bool:
    """True for loopback endpoints (the local GUI, asyncio's own self-pipe).

    CLAUDE.md permits loopback (127.0.0.1); the emit-only guarantee is about
    connections to *external* hosts such as search engines or targets.
    """
    if isinstance(address, tuple) and address:
        return address[0] in _LOOPBACK
    return False


@pytest.fixture
def block_network(monkeypatch):
    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex
    real_create_connection = socket.create_connection

    def guarded_connect(self, address, *args, **kwargs):
        if _is_loopback(address):
            return real_connect(self, address, *args, **kwargs)
        raise _NetworkAttempted(f"runtime attempted an outbound connection to {address!r}")

    def guarded_connect_ex(self, address, *args, **kwargs):
        if _is_loopback(address):
            return real_connect_ex(self, address, *args, **kwargs)
        raise _NetworkAttempted(f"runtime attempted an outbound connection to {address!r}")

    def guarded_create_connection(address, *args, **kwargs):
        if _is_loopback(address):
            return real_create_connection(address, *args, **kwargs)
        raise _NetworkAttempted(f"runtime attempted an outbound connection to {address!r}")

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
    monkeypatch.setattr(socket, "create_connection", guarded_create_connection)
    return guarded_connect


def test_targeted_build_makes_no_connection(block_network):
    result = select_and_render(
        load_dorks(),
        broad=False,
        values={"domain": "example.com"},
        surface="Google",
    )
    assert result.rows
    assert all("example.com" in row.query for row in result.rows)


def test_broad_build_makes_no_connection(block_network):
    result = select_and_render(load_dorks(), broad=True, surface="Shodan")
    assert result.rows
    assert all(row.mode == "broad" for row in result.rows)


def test_export_makes_no_connection(block_network):
    result = select_and_render(load_dorks(), broad=True, surface="Google")
    for fmt in ("txt", "csv", "json", "markdown", "html"):
        assert serialize(result.rows, fmt)


def test_web_build_makes_no_real_connection(block_network):
    # The in-process TestClient must still work while real sockets are blocked.
    client = TestClient(app)
    resp = client.post("/api/build", json={"mode": "broad", "surface": "Google"})
    assert resp.status_code == 200
    assert resp.json()["rows"]


def test_web_export_makes_no_real_connection(block_network):
    client = TestClient(app)
    resp = client.post("/api/export", json={"mode": "broad", "surface": "Google", "format": "csv"})
    assert resp.status_code == 200
    assert resp.content
