"""Project pre generation hooks."""
import re

import typer

pre_gen = typer.Typer()


@pre_gen.command()
def main(package_name: str = "{{ cookiecutter.package_name }}") -> None:
    """Main entrypoint of pre generation hooks."""
    if not re.match(r"^[_a-zA-Z][_a-zA-Z0-9]+$", package_name):
        typer.secho(
            f"ERROR: The package name ({package_name})"
            f" is not a valid Python module name."
            f" Please do not use a - and use _ instead",
            err=True,
            fg=typer.colors.BRIGHT_RED,
        )

        raise typer.Exit(code=1)


if __name__ == "__main__":
    pre_gen()  # pragma: no cover
