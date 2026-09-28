import json

from typer.testing import CliRunner

from dorkforge.cli import app

runner = CliRunner()


def test_list_exits_zero_and_shows_total() -> None:
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Total dorks:" in result.stdout


def test_targeted_build_without_authorized_exits_nonzero() -> None:
    result = runner.invoke(app, ["build", "--target", "example.com", "--surface", "Google"])
    assert result.exit_code != 0
    assert "--authorized" in result.stdout


def test_targeted_build_with_authorized_returns_queries_and_urls() -> None:
    result = runner.invoke(
        app,
        ["build", "--authorized", "--target", "example.com", "--surface", "Google", "--limit", "5"],
    )
    assert result.exit_code == 0
    assert "example.com" in result.stdout
    assert "google.com/search" in result.stdout
    assert "Rules of Engagement" in result.stdout


def test_broad_build_runs_without_authorized_and_shows_notice() -> None:
    result = runner.invoke(app, ["build", "--broad", "--surface", "Google", "--limit", "5"])
    assert result.exit_code == 0
    assert "research-only" in result.stdout


def test_export_writes_json_and_csv(tmp_path) -> None:
    json_path = tmp_path / "out.json"
    result = runner.invoke(
        app,
        [
            "export",
            "--authorized",
            "--target",
            "example.com",
            "--surface",
            "Google",
            "--format",
            "json",
            "--out",
            str(json_path),
        ],
    )
    assert result.exit_code == 0
    assert json_path.exists() and json_path.stat().st_size > 0
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert isinstance(data, list) and data

    csv_path = tmp_path / "out.csv"
    result = runner.invoke(
        app,
        [
            "export",
            "--authorized",
            "--target",
            "example.com",
            "--surface",
            "Google",
            "--format",
            "csv",
            "--out",
            str(csv_path),
        ],
    )
    assert result.exit_code == 0
    assert csv_path.exists() and csv_path.stat().st_size > 0
    assert "id,category,risk,surface,mode,advisory,purpose,query,url" in csv_path.read_text(
        encoding="utf-8"
    )


def test_filter_narrows_by_surface() -> None:
    result = runner.invoke(app, ["build", "--broad", "--surface", "Shodan", "--limit", "50"])
    assert result.exit_code == 0
    assert "Shodan" in result.stdout
    assert "google.com/search" not in result.stdout
    assert "shodan.io/search" in result.stdout
