"""Test module for post_gen_hook."""
import sys
from pathlib import Path
from shutil import rmtree
from typing import Sequence

import pytest
from click import testing
from pytest_cookies.plugin import Cookies
from typer.testing import CliRunner

from hooks.post_gen_project import (
    License,
    YesNo,
    clear,
    inside_dir,
    post_gen,
    run_command,
)
from tests.utils import BaseBakingMixin


def test_get_license_item() -> None:
    """Test of getting license items."""

    assert License.get_item(License.MIT) == License.MIT
    assert License.get_item(License.BSD_3_CLAUSE) == License.BSD_3_CLAUSE
    assert License.get_item(License.ISC) == License.ISC
    assert License.get_item(License.APACHE_20) == License.APACHE_20
    assert License.get_item(License.GPL_30_ONLY) == License.GPL_30_ONLY
    assert License.get_item(License.NO_LICENSE) == License.NO_LICENSE

    assert License.get_item(License.MIT.value) == License.MIT
    assert License.get_item(License.BSD_3_CLAUSE.value) == License.BSD_3_CLAUSE
    assert License.get_item(License.ISC.value) == License.ISC
    assert License.get_item(License.APACHE_20.value) == License.APACHE_20
    assert License.get_item(License.GPL_30_ONLY.value) == License.GPL_30_ONLY
    assert License.get_item(License.NO_LICENSE.value) == License.NO_LICENSE


def test_run_command() -> None:
    """Test of shell commands invocations."""
    assert run_command("echo 'Test'") == b"Test\n"


def test_inside_dir(tmp_path: Path) -> None:
    """Test of execution inside the directory."""
    control_dir = Path.cwd()
    assert control_dir.samefile(Path.cwd())
    assert not control_dir.samefile(tmp_path)

    with inside_dir(tmp_path):
        test_dir = Path.cwd()
        assert test_dir.samefile(tmp_path)
        assert not test_dir.samefile(control_dir)

    assert control_dir.samefile(Path.cwd())


def test_clean(tmp_path: Path) -> None:
    """Test clean the directory."""

    test_file1 = tmp_path / "test.txt"
    test_dir = tmp_path / "tmp"
    test_file2 = test_dir / "test.txt"

    test_file1.open(mode="wb").write(b"Test")
    test_dir.mkdir()
    test_file2.open(mode="wb").write(b"Test")

    assert test_file1.is_file()
    assert test_dir.is_dir()
    assert test_file2.is_file()

    clear(root=tmp_path, to_remove=("test.txt", "tmp"))

    assert not test_file1.exists()
    assert not test_dir.exists()
    assert not test_file2.exists()
    assert not list(tmp_path.iterdir())


class TestPostGen(BaseBakingMixin):
    """Test class for all post generation commands."""

    runner = CliRunner()

    def run_app(self, args: str | Sequence[str] | None) -> testing.Result:
        """Invokes cli runner with post generation hook app."""
        return self.runner.invoke(post_gen, args=args)

    def test_run_app(self, tmp_path: Path) -> None:
        """Test run_app without sub-commands."""
        self.if_successful(
            self.run_app(
                (
                    "--project-root",
                    str(tmp_path),
                    "--command-line-interface",
                    YesNo.YES,
                    "--license-type",
                    License.NO_LICENSE,
                    "--install-pre-commit-hooks",
                    YesNo.YES,
                )
            )
        )

    def test_git_init(self, tmp_path: Path) -> None:
        """Test of git repository initialization."""
        with inside_dir(tmp_path):
            git = tmp_path / ".git"
            assert not git.exists()

            self.if_successful(
                self.run_app(("--project-root", str(tmp_path), "git-init"))
            )
            assert git.is_dir()
            assert (git / "objects").is_dir()
            assert (git / "refs" / "tags").is_dir()
            assert (git / "refs" / "heads").is_dir()

            status = run_command("git status")
            assert b"branch main" in status
            assert b"No commits yet" in status

            rmtree(git, ignore_errors=True)
            assert not git.exists()

            git.mkdir()
            assert git.is_dir()
            assert not list(git.iterdir())

            self.if_successful(
                self.run_app(("--project-root", str(tmp_path), "git-init"))
            )
            assert git.is_dir()
            assert not list(git.iterdir())

    @pytest.mark.parametrize(
        "args",
        tuple(
            map(lambda i: ({"command_line_interface": i.value}, i != YesNo.NO), YesNo)
        ),
    )
    def test_cli_cleanup(
        self, cookies: Cookies, args: tuple[dict[str, str], bool]
    ) -> None:
        """Test of cli cleanup after initialization."""
        context, cli_exists = args
        result = self.if_baked(cookies.bake(extra_context=context))

        project_path, _, package_path = self.project_info(result)
        cli_file = package_path / "cli.py"
        assert cli_file.is_file() == cli_exists

        if cli_exists:
            run_app_args = [
                "--project-root",
                str(project_path),
                "--package-name",
                str(package_path.name),
                "--command-line-interface",
            ]

            _decision: YesNo
            for _decision in YesNo:
                self.if_successful(
                    self.run_app(args=[*run_app_args, _decision.value, "cleanup"])
                )
                assert cli_file.is_file() == (_decision != YesNo.NO)

    @pytest.mark.parametrize(
        "args",
        tuple(
            map(lambda i: ({"license_type": i.value}, i != License.NO_LICENSE), License)
        ),
    )
    def test_license_cleanup(
        self, cookies: Cookies, args: tuple[dict[str, str], bool]
    ) -> None:
        """Test of cli cleanup after initialization."""
        context, license_exists = args
        result = self.if_baked(cookies.bake(extra_context=context))

        project_path, _, _ = self.project_info(result)
        license_file = project_path / "LICENSE"
        assert license_file.is_file() == license_exists

        if license_exists:
            run_app_args = ["--project-root", str(project_path), "--license-type"]

            _licence: License
            for _licence in License:
                self.if_successful(
                    self.run_app(args=[*run_app_args, _licence.value, "cleanup"])
                )
                assert license_file.is_file() == (_licence != License.NO_LICENSE)

    @pytest.mark.parametrize(
        "args",
        tuple(
            map(lambda i: ({"install_pre_commit_hooks": i.value}, i != YesNo.NO), YesNo)
        ),
    )
    def test_pre_commit_cleanup(
        self, cookies: Cookies, args: tuple[dict[str, str], bool]
    ) -> None:
        """Test of pre commit cleanup after initialization."""
        context, pre_commit_exists = args
        result = self.if_baked(cookies.bake(extra_context=context))

        project_path, _, _ = self.project_info(result)
        pre_commit_file = project_path / ".pre-commit-config.yaml"
        assert pre_commit_file.is_file() == pre_commit_exists

        if pre_commit_exists:
            run_app_args = [
                "--project-root",
                str(project_path),
                "--install-pre-commit-hooks",
            ]

            _decision: YesNo
            for _decision in YesNo:
                self.if_successful(
                    self.run_app(args=[*run_app_args, _decision.value, "cleanup"])
                )
                assert pre_commit_file.is_file() == (_decision != YesNo.NO)

    @pytest.mark.parametrize(
        "args",
        (
            (True, True),
            (True, False),
            (False, False),
            (False, True),
        ),
    )
    def test_pre_commit(self, tmp_path: Path, args: tuple[bool, bool]) -> None:
        """Test of install-pre-commit-hooks command."""
        to_install, installed = args
        pre_commit_installed: bool = b"pre-commit" in run_command(
            f"{sys.executable} -m pip list"
        )

        pre_params = "uninstall --yes" if installed else "install --upgrade --no-input"
        run_command(f"{sys.executable} -m pip {pre_params} --quiet pre-commit")

        self.if_successful(self.run_app(("--project-root", str(tmp_path), "git-init")))

        option = YesNo.YES.value if to_install else YesNo.NO.value
        self.if_successful(
            self.run_app(
                (
                    "--project-root",
                    str(tmp_path),
                    "--install-pre-commit-hooks",
                    option,
                    "pre-commit-hooks",
                )
            )
        )

        pre_commit_path = tmp_path / ".git" / "hooks" / "pre-commit"
        assert pre_commit_path.is_file() == to_install

        post_params = (
            "install --upgrade --no-input"
            if pre_commit_installed
            else "uninstall --yes"
        )
        run_command(f"{sys.executable} -m pip {post_params} --quiet pre-commit")
