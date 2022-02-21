"""Test module for pre_gen_hook."""
import pytest
from typer.testing import CliRunner

from hooks.pre_gen_project import pre_gen


@pytest.mark.parametrize(
    "args", [("package_name", 0), ("package-name", 1), ("package name", 1)]
)
def test_app(args: tuple[str, bool]) -> None:
    """Run pre gen hook cli app."""
    runner = CliRunner()
    package_name, exit_code = args

    result = runner.invoke(pre_gen, ["--package-name", package_name])

    assert result.exit_code == exit_code
