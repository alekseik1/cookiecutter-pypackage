"""Tests for README author attribution rendering."""


def test_readme_created(cookies):
    """With no author_website, name links to GitHub profile."""
    result = cookies.bake(
        extra_context={
            "pypi_package_name": "attr-test",
            "full_name": "Audrey M. Roy Greenfeld",
            "github_username": "audreyfeldroy",
            "pypi_username": "audreyfeldroy",
            "author_website": "",
        },
    )
    assert result.exit_code == 0
    (result.project_path / "README.md").read_text()
