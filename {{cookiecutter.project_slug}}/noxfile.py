"""Nox commands."""
from pathlib import Path
from shutil import rmtree

import nox

nox.options.sessions = ("main",)


@nox.session(py="3.10")
def install(session: nox.Session) -> None:
    """Install all dependencies from pyproject."""
    session.run("poetry", "update", external=True)
    session.run("poetry", "install", external=True)


@nox.session(py="3.10")
def isort(session: nox.Session) -> None:
    """Runs isort."""
    args = session.posargs or ("{{cookiecutter.package_name}}", "tests", "noxfile.py")
    session.run("poetry", "run", "isort", *args, external=True)


@nox.session(py="3.10")
def black(session: nox.Session) -> None:
    """Runs blake."""
    args = session.posargs or ("{{cookiecutter.package_name}}", "tests", "noxfile.py")
    session.run("poetry", "run", "black", *args, external=True)


@nox.session(py="3.10")
def pylint(session: nox.Session) -> None:
    """Runs pylint."""
    args = session.posargs or ("{{cookiecutter.package_name}}", "tests", "noxfile.py")
    session.run("poetry", "run", "pylint", *args, external=True)


@nox.session(py="3.10")
def pydocstyle(session: nox.Session) -> None:
    """Runs pydocstyle."""
    args = session.posargs or ("{{cookiecutter.package_name}}", "tests", "noxfile.py")
    session.run("poetry", "run", "pydocstyle", *args, external=True)


@nox.session(py="3.10")
def mypy(session: nox.Session) -> None:
    """Runs mypy."""
    args = session.posargs or ("{{cookiecutter.package_name}}", "tests", "noxfile.py")
    session.run("poetry", "run", "mypy", *args, external=True)


@nox.session(py="3.10")
def pytest(session: nox.Session) -> None:
    """Runs pytest."""
    args = session.posargs or []
    session.run("poetry", "run", "pytest", *args, external=True)


@nox.session(py="3.10")
def coverage(session: nox.Session) -> None:
    """Runs coverage."""
    args = session.posargs or []
    session.run("poetry", "run", "pytest", "--cov", *args, external=True)


@nox.session(name="clear", py="3.10")
def clear_(_session: nox.Session) -> None:
    """Clean up project."""
    project_dir = Path(__file__).parent
    to_remove = (".mypy_cache", ".pytest_cache", ".coverage", ".nox")

    for item in to_remove:
        remove = project_dir / item

        if remove.is_file():
            remove.unlink()

        rmtree(remove, ignore_errors=True)


@nox.session(name="format", py="3.10")
def format_(session: nox.Session) -> None:
    """Runs formatting commands."""
    session.notify("install")
    session.notify("isort")
    session.notify("black")


@nox.session(py="3.10")
def lint(session: nox.Session) -> None:
    """Runs linting commands."""
    session.notify("install")
    session.notify("pylint")
    session.notify("pydocstyle")
    session.notify("mypy")


@nox.session(py="3.10")
def main(session: nox.Session) -> None:
    """Runs default commands."""
    session.notify("install")
    session.notify("isort")
    session.notify("black")
    session.notify("pylint")
    session.notify("pydocstyle")
    session.notify("mypy")
    session.notify("coverage")
    session.notify("clear")
