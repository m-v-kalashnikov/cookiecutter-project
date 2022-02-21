"""Common methods for all tests."""
from pathlib import Path
from typing import Any

from click import testing
from pytest_cookies import plugin


class BaseBakingMixin:
    """Mixin for common test methods."""

    @staticmethod
    def get_path(to_check: Any) -> Path:
        """Get path or raise error in argument in not path."""
        assert isinstance(to_check, Path)
        return to_check

    @staticmethod
    def if_successful(
        result: plugin.Result | testing.Result,
    ) -> plugin.Result | testing.Result:
        """Check if result was successful."""
        assert result.exit_code == 0
        assert result.exception is None
        return result

    def if_baked(self, result: plugin.Result | testing.Result) -> plugin.Result:
        """Checks if project was generated successfully and has appropriate type."""
        _result = self.if_successful(result)
        assert isinstance(result, plugin.Result)
        return _result

    def project_info(self, result: plugin.Result) -> tuple[Path, str, Path]:
        """Get toplevel dir, project_slug, and project dir from baked cookies."""
        project_path = self.get_path(result.project_path)
        project_slug = project_path.name
        package_path = project_path / result.context["package_name"]

        return project_path, project_slug, package_path
