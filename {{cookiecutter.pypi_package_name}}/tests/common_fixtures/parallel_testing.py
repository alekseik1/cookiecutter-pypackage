"""Logic for @pytest.mark.parallel marker.

All tests that can be run in parallel must be marked as @pytest.mark.parallel
"""
import pytest


def _is_xdist_worker(config) -> bool:
    return hasattr(config, "workerinput")


def pytest_runtest_setup(item: pytest.Item) -> None:
    """
    In xdist-worker run only tests with `parallel` marker.
    The rest are skipped - they will be run in main worker.
    """
    if _is_xdist_worker(item.config):
        if not item.get_closest_marker("parallel"):
            pytest.skip("sequential test: runs in main process only")