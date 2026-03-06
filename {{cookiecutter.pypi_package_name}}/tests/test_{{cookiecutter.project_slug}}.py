"""Tests for `{{ cookiecutter.project_slug }}` package."""

import pytest

import {{ cookiecutter.project_slug }}


def test_import():
    """Verify the package can be imported."""
    assert {{ cookiecutter.project_slug }}


@pytest.mark.integration
def test_integration_example():
    assert 1
