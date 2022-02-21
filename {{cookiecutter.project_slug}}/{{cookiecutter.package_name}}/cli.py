{% if cookiecutter.command_line_interface|lower == 'yes' -%}
"""Console script for {{cookiecutter.package_name}}."""

import typer

main: typer.Typer = typer.Typer()


@main.command()
def info() -> None:
    """CLI entrypoint."""
    typer.secho("{{ cookiecutter.project_slug }}", fg=typer.colors.BRIGHT_WHITE)
    typer.secho("=" * len("{{ cookiecutter.project_slug }}"), fg=typer.colors.BRIGHT_WHITE)
    typer.secho(
        "{{ cookiecutter.project_short_description }}",
        fg=typer.colors.BRIGHT_WHITE,
    )


if __name__ == "__main__":
    main()  # pragma: no cover
{%- endif %}
