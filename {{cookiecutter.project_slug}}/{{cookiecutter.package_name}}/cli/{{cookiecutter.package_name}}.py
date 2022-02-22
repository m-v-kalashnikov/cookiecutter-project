{% if cookiecutter.command_line_interface|lower == 'yes' -%}
"""Console script for {{cookiecutter.project_slug}}."""

import typer

from {{ cookiecutter.package_name }} import __author__

main: typer.Typer = typer.Typer()


@main.command()
def info() -> None:
    """CLI entrypoint."""
    greeting = f"{{ cookiecutter.project_slug }} by {__author__}"
    typer.secho(greeting, fg=typer.colors.BRIGHT_WHITE)
    typer.secho("=" * len(greeting), fg=typer.colors.BRIGHT_WHITE)
    typer.secho(
        "{{ cookiecutter.project_short_description }}",
        fg=typer.colors.BRIGHT_WHITE,
    )


if __name__ == "__main__":
    main()  # pragma: no cover
{%- endif %}
