# {{ cookiecutter.project_name }}

{{ cookiecutter.project_short_description }}

* Created by **[{{ cookiecutter.full_name }}]({{ cookiecutter.author_website if cookiecutter.author_website else 'https://github.com/' + cookiecutter.github_username }})**
{%- if cookiecutter.author_website %}
  * GitHub: https://github.com/{{ cookiecutter.github_username }}
{%- endif %}
* Free software: MIT License

## Documentation

Documentation is built with [Zensical](https://zensical.org/).

* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

API documentation is auto-generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

## Development

To set up for local development:

```bash
# Clone your fork
git clone git@github.com:your_username/{{ cookiecutter.pypi_package_name }}.git
cd {{ cookiecutter.pypi_package_name }}

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available when you run `{{ cookiecutter.project_slug }}`.

Run tests: `just testall`.

Run quality checks (format, lint, type check, test): `just qa`.

## Author

{{ cookiecutter.project_name }} was created in {% now 'local', '%Y' %} by {{ cookiecutter.full_name }}.
