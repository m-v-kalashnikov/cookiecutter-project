"""Test module for project generation."""
import datetime

import pytest
from cookiecutter.exceptions import FailedHookException
from pytest_cookies.plugin import Cookies

from hooks.post_gen_project import License
from tests.utils import BaseBakingMixin


class TestGeneration(BaseBakingMixin):
    """Test of project generation with different parameters."""

    DEPENDENCY_FILE = "pyproject.toml"

    def test_bake_with_defaults(self, cookies: Cookies) -> None:
        """Test project creating with default values."""

        result = self.if_baked(cookies.bake())

        toplevel_files = [e.name for e in result.project_path.iterdir()]
        assert result.context["package_name"] in toplevel_files
        assert self.DEPENDENCY_FILE in toplevel_files
        assert ".gitignore" in toplevel_files
        assert "README.md" in toplevel_files
        assert "tests" in toplevel_files

    @classmethod
    @pytest.mark.parametrize(
        "args",
        [
            ({"package_name": "package_name"}, 0),
            ({"package_name": "package-name"}, -1),
            ({"package_name": "package name"}, -1),
        ],
    )
    def test_package_name(
        cls,
        cookies: Cookies,
        args: list[tuple[dict[str, str], int]],
    ) -> None:
        """Test package name validation."""
        extra_context, exit_code = args
        result = cookies.bake(extra_context=extra_context)

        assert result.exit_code == exit_code

        if exit_code == 0:
            assert result.exception is None
        elif exit_code == -1:
            assert isinstance(result.exception, FailedHookException)
        else:
            assert 0

    @pytest.mark.parametrize(
        "license_info",
        [
            (License.MIT.value, "MIT "),
            (
                License.BSD_3_CLAUSE.value,
                "Redistributions of source code must retain"
                " the above copyright notice, this",
            ),
            (License.ISC.value, "ISC License"),
            (License.APACHE_20.value, "Licensed under the Apache License, Version 2.0"),
            (License.GPL_30_ONLY.value, "GNU GENERAL PUBLIC LICENSE"),
        ],
    )
    def test_bake_with_various_licenses(
        self, cookies: Cookies, license_info: tuple[str, str]
    ) -> None:
        """Test project generation with various licenses."""
        license_type, target_string = license_info
        result = self.if_baked(
            cookies.bake(extra_context={"license_type": license_type})
        )
        assert (
            target_string
            in (self.get_path(result.project_path) / "LICENSE").open().read()
        )
        assert (
            license_type
            in (self.get_path(result.project_path) / "pyproject.toml").open().read()
        )

    def test_year_compute_in_license_file(self, cookies: Cookies) -> None:
        """Test if year in LICENCE match to current year."""
        result = self.if_baked(cookies.bake())
        license_file = self.get_path(result.project_path) / "LICENSE"
        assert license_file.is_file()

        now = datetime.datetime.now()
        assert str(now.year) in license_file.open().read()

    def test_bake_not_open_source(self, cookies: Cookies) -> None:
        """Test if Licence absent when project is not open source."""
        result = self.if_baked(cookies.bake())
        project_path = self.get_path(result.project_path)
        assert (project_path / "LICENSE").is_file()

        dependencies = project_path / self.DEPENDENCY_FILE
        assert dependencies.is_file()
        assert "License" not in dependencies.open().read()
