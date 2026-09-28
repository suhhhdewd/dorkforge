from importlib.resources import files

import yaml
from typer.testing import CliRunner

import dorkforge
from dorkforge.cli import app
from dorkforge.executors import Executor
from dorkforge.models import RunMode


def test_version_command() -> None:
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == dorkforge.__version__


def test_run_modes() -> None:
    assert {m.value for m in RunMode} == {"targeted", "broad"}


def test_no_executors_implemented() -> None:
    assert Executor.__subclasses__() == []


def test_dork_library_is_packaged() -> None:
    data = yaml.safe_load(files("dorkforge.data").joinpath("dorks.yaml").read_text())
    assert "dorks" in data
