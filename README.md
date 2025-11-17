# adjunct

_adjunct_ is a collection of miscellaneous modules.

It's intended that this will eventually end up as a namespace package.

## Development and Testing

You should make sure you've [just](https://just.systems/) installed, as it's
used for running maintenance tasks.

You're expected to make sure you've [uv](https://docs.astral.sh/uv/) installed
as it's used for managing the project. Also, for linting and code fixes, make
sure you've [ruff](https://docs.astral.sh/ruff/) installed too. If you've _uv_
installed already, install _ruff_ with:

```console
uv tool install ruff
```

For normal development, you can run the test suite with:

```console
just tests
```

If you want to run the test suite across all supported Python runtimes, you'll
need [tox](https://tox.wiki/en/4.32.0/). Like with _ruff_, you can install it
with _uv_. You'll need to make sure that you have the _tox-uv_ plugin installed
too:

```console
uv tool install tox --with tox-uv
```
