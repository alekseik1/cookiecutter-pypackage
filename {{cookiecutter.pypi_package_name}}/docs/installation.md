# Installation

## From source

The source files for {{ cookiecutter.project_name }} can be downloaded from the [Github repo](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}).

You can either clone the public repository:

```sh
git clone https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}
```

Or download the [tarball](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/tarball/main):

```sh
curl -OJL https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/tarball/main
```

Once you have a copy of the source, you can install it with:

```sh
cd {{ cookiecutter.project_slug }}
uv sync
```
