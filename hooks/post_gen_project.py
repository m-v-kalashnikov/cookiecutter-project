"""Project post generation hooks."""
import os
import shlex
import subprocess
import sys
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from shutil import rmtree
from typing import Any, Generator, Iterable

import typer


class YesNo(str, Enum):
    """Centralized Yes/No choices."""

    YES = "Yes"
    NO = "No"


class License(str, Enum):
    """Centralized License type choices."""

    MIT = "MIT"
    BSD_3_CLAUSE = "BSD-3-Clause"
    ISC = "ISC"
    APACHE_20 = "Apache-2.0"
    GPL_30_ONLY = "GPL-3.0-only"
    NO_LICENSE = "No-license"

    @classmethod
    def get_item(cls, name_or_value: str | Any) -> "License":
        """Return Licence type by name or value."""
        if isinstance(name_or_value, License):
            return name_or_value

        return getattr(
            License,
            str(name_or_value)
            .upper()
            .replace(".", "")
            .replace("-", "_")
            .replace(" ", "_"),
            License.NO_LICENSE,
        )


post_gen = typer.Typer()
state: dict[str, YesNo | License | Path | str] = {}


def run_command(command: str) -> bytes:
    """Run command in sh format and return output."""
    return subprocess.check_output(shlex.split(command))


@contextmanager
def inside_dir(directory: Path) -> Generator[None, None, None]:
    """Execute code from inside the given directory."""
    old_path = Path.cwd()

    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(old_path)


def clear(root: Path, to_remove: Iterable[str]) -> None:
    """Deletes all specified paths in specified directory."""
    for element in to_remove:
        _element = root / element.strip("/")

        if _element.is_file():
            _element.unlink()

        if _element.is_dir():
            rmtree(_element, ignore_errors=True)


@post_gen.command()
def git_init() -> None:
    """Initialize git repository in generated project."""
    project_root = state["project_root"]
    assert isinstance(project_root, Path)

    git = project_root / ".git"

    if not git.is_dir():
        with inside_dir(project_root):
            run_command("git init -b main")
            run_command("git add .")


@post_gen.command()
def pre_commit_hooks() -> None:
    """Install pre commit hooks."""
    if state["install_pre_commit_hooks"] == YesNo.YES:
        project_root = state["project_root"]
        assert isinstance(project_root, Path)

        with inside_dir(project_root):
            pre_commit_installed: bool = b"pre-commit" in run_command(
                f"{sys.executable} -m pip list"
            )

            if not pre_commit_installed:
                run_command(
                    f"{sys.executable} -m "
                    f"pip install --upgrade --no-input --quiet pre-commit"
                )

            run_command(f"{sys.executable} -m pre_commit install")

            if not pre_commit_installed:
                run_command(
                    f"{sys.executable} -m pip uninstall --yes --quiet pre-commit"
                )


@post_gen.command()
def cleanup() -> None:
    """Remove unnecessary files in generated project."""
    project_root = state["project_root"]
    assert isinstance(project_root, Path)

    if state["command_line_interface"] == YesNo.NO:
        clear(root=project_root / state["package_name"], to_remove=("cli.py",))

    if state["license_type"] == License.NO_LICENSE:
        clear(root=project_root, to_remove=("LICENSE",))

    if state["install_pre_commit_hooks"] == YesNo.NO:
        clear(root=project_root, to_remove=(".pre-commit-config.yaml",))


@post_gen.callback(invoke_without_command=True)
# pylint: disable-next=too-many-arguments
def main(
    ctx: typer.Context,
    project_root: Path = typer.Option(
        Path.cwd(), help="Path to generated project.", show_default=False
    ),
    project_slug: str = typer.Option(
        "{{ cookiecutter.project_slug }}", help="Slug of project.", show_default=False
    ),
    package_name: str = typer.Option(
        "{{ cookiecutter.package_name }}", help="Name of project.", show_default=False
    ),
    command_line_interface: YesNo = typer.Option(
        (
            YesNo.NO
            if "{{ cookiecutter.command_line_interface }}" == YesNo.NO.value
            else YesNo.YES
        ),
        case_sensitive=False,
        help="Add CLI to project or not.",
        show_default=False,
    ),
    license_type: License = typer.Option(
        License.get_item("{{ cookiecutter.license_type }}"),
        case_sensitive=False,
        help="Which license to use.",
        show_default=False,
    ),
    install_pre_commit_hooks: YesNo = typer.Option(
        (
            YesNo.YES
            if "{{ cookiecutter.install_pre_commit_hooks }}" == YesNo.YES.value
            else YesNo.NO
        ),
        case_sensitive=False,
        help="Add pre commit hooks or not.",
        show_default=False,
    ),
) -> None:
    """Main entrypoint of post generation hooks."""
    state.update(
        dict(
            license_type=license_type,
            project_root=project_root,
            package_name=package_name,
            project_slug=project_slug,
            command_line_interface=command_line_interface,
            install_pre_commit_hooks=install_pre_commit_hooks,
        )
    )

    if ctx.invoked_subcommand is None:
        cleanup()
        git_init()
        pre_commit_hooks()


if __name__ == "__main__":
    post_gen()  # pragma: no cover
