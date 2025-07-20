# AGENTS.md file

## Formatting

Always format the code before commiting using, making sure that the Python code is properly formatted using:

```bash
black .
```

## Testing

Run the full test suite:

```bash
pytest
```

## Style Guide

- Always update `CHANGELOG.md` according to semantic versioning, mentioning your changes in the unreleased section.
- Write commit messages using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
- Never bump the internal package version in `setup.py`. This is handled automatically by the release process.
- Python files use CRLF line endings.

## License

Appier is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).
