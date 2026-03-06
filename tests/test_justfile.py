import subprocess
import sys

import pytest

JUSTFILE_TARGETS = [
    "list",
    "version",
    "build",
    "type-check",
    "qa",
    "test",
    "test-integration",
    "format",
    "docs-build",
    "clean-build",
    "clean-pyc",
    "clean-test",
    "clean",
]


@pytest.mark.skipif(sys.platform == "win32", reason="justfile not supported on Windows")
@pytest.mark.parametrize("target", JUSTFILE_TARGETS)
def test_just_target(cookies, target):
    result = cookies.bake()
    assert result.exit_code == 0

    proc = subprocess.run(["just", target], cwd=str(result.project_path), capture_output=True)
    assert proc.returncode == 0
