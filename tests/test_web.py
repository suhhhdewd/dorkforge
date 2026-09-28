import json

from fastapi.testclient import TestClient

from dorkforge.web.app import app

client = TestClient(app)


def test_index_returns_html() -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "dork" in resp.text.lower()
    assert "Rules of Engagement" in resp.text


def test_build_broad_returns_rows() -> None:
    resp = client.post("/api/build", json={"mode": "broad", "surface": "Google"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["rows"], list) and data["rows"]
    assert data["broad"] is True
    assert data["notice"]


def test_build_targeted_without_authorized_is_400() -> None:
    resp = client.post(
        "/api/build",
        json={"mode": "targeted", "surface": "Google", "values": {"domain": "example.com"}},
    )
    assert resp.status_code == 400
    assert "authoriz" in resp.json()["detail"].lower()


def test_build_targeted_authorized_contains_domain() -> None:
    resp = client.post(
        "/api/build",
        json={
            "mode": "targeted",
            "surface": "Google",
            "values": {"domain": "example.com"},
            "authorized": True,
        },
    )
    assert resp.status_code == 200
    rows = resp.json()["rows"]
    assert rows
    assert all("example.com" in row["query"] for row in rows)


def test_export_json_and_csv_non_empty() -> None:
    payload = {"mode": "broad", "surface": "Google"}

    resp = client.post("/api/export", json={**payload, "format": "json"})
    assert resp.status_code == 200
    assert "application/json" in resp.headers["content-type"]
    assert "attachment" in resp.headers["content-disposition"]
    data = json.loads(resp.content)
    assert isinstance(data, list) and data

    resp = client.post("/api/export", json={**payload, "format": "csv"})
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert resp.content
    assert b"id,category,risk,surface,mode,advisory,purpose,query,url" in resp.content


def test_serve_defaults_to_localhost() -> None:
    import inspect

    from dorkforge.cli import serve

    params = inspect.signature(serve).parameters
    assert params["host"].default == "127.0.0.1"
    assert params["port"].default == 8765
