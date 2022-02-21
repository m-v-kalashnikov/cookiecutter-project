"""Tests for `{{ cookiecutter.package_name }}` package."""
{% if cookiecutter.command_line_interface|lower == 'yes' -%}
from typer.testing import CliRunner

from {{cookiecutter.package_name}} import cli

{%- endif %}


{%- if cookiecutter.command_line_interface|lower == 'yes' %}


class TestCLI:
    """Test the CLI."""

    runner = CliRunner()

    def test_main(self) -> None:
        """Test main call of CLI."""

        result = self.runner.invoke(cli.main)
        assert result.exit_code == 0
        assert "{{ cookiecutter.project_slug }}" in result.output

    def test_help(self) -> None:
        """Test --help call of CLI."""

        result = self.runner.invoke(cli.main, ["--help"])
        assert result.exit_code == 0

        help_lines = list(
            filter(lambda line: "--help" in line, result.output.split("\n"))
        )
        assert len(help_lines) == 1

        help_text = help_lines[0]
        assert "Show this message and exit." in help_text
{%- endif %}
