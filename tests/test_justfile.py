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
    "test-cmd",
    "test-integration",
    "format",
    "docs-build",
    "clean-build",
    "clean-pyc",
    "clean-test",
    "clean",
]

# Excluded targets:
# - tag, publish: require network (git push / PyPI)
# - docs-serve, type-check-watch: block indefinitely (server / file watcher)
# - testall, coverage: require Python 3.12 + 3.13 + 3.14 all installed


@pytest.mark.skipif(sys.platform == "win32", reason="justfile not supported on Windows")
@pytest.mark.parametrize("target", JUSTFILE_TARGETS)
def test_just_target(cookies, target):
    result = cookies.bake()
    assert result.exit_code == 0

    proc = subprocess.run(["just", target], cwd=str(result.project_path), capture_output=True)
    # 0 - command ok, 5 - no tests collected
    assert proc.returncode in (0, 5)
