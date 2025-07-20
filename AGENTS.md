# AGENTS.md file

## Formatting

Always format the code before commiting using, making sure that the Python code is properly formatted using:

```bash
black .
```

## Testing

Run the full test suite:

```bash
pip install -r requirements.txt
pip install -r extra.txt
pip install pytest netius
ADAPTER=tiny pytest
```

## Style Guide

- Always update `CHANGELOG.md` according to semantic versioning, mentioning your changes in the unreleased section.
- Write commit messages using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
- Never bump the internal package version in `setup.py`. This is handled automatically by the release process.
- Python files use CRLF as the line ending.
- The implementation should be done in Python 2.7+ and compatible with Python 3.12.
- The style should respect the black formatting.
- The implementation should be done in a way that is compatible with the existing codebase.
- Prefer `item not in list` over `not item in list`
- Prefer `item == None` over `item is None`

## License

Appier is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).
