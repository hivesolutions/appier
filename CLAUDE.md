# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing

```bash
# Install dependencies and run tests
pip install -r requirements.txt
pip install -r extra.txt
pip install pytest netius
ADAPTER=tiny HTTPBIN=httpbin.bemisc.com pytest

# Tests are located in src/appier/test/
```

### Code Formatting

```bash
# Format code before committing
pip install black
black .
```

### Package Installation

```bash
# Install in development mode
pip install -e .

# Install from PyPI
pip install appier
```

## Architecture Overview

Appier is a Python web framework with the following core architecture:

### Core Components

- **App (base.py)** - Central application class that handles HTTP/ASGI lifecycle, routing, configuration, and serves as the foundation for all applications
- **Controller (controller.py)** - Abstract base class for creating business logic entry points with action methods
- **Model (model.py)** - Data layer providing ORM-like functionality with support for MongoDB and TinyDB
- **Request/Response** - HTTP request handling and response generation
- **Session** - User session management across requests
- **Cache** - Caching layer with multiple backend implementations

### Key Modules

- **Asynchronous (asynchronous.py)** - Async/await support and coroutine management
- **Data (data.py)** - Data adapters for MongoDB and TinyDB
- **Validation** - Input validation and data sanitization
- **HTTP (http.py)** - HTTP client utilities and response handling
- **Scheduler** - Background task scheduling and cron-like functionality
- **Bus/Observer** - Event system for decoupled communication
- **SMTP** - Email sending capabilities

### Application Structure

Applications inherit from `appier.App` and define routes using decorators:

```python
import appier

class MyApp(appier.App):
    @appier.route("/", "GET")
    def hello(self):
        return "Hello World"
```

Models inherit from `appier.Model` for data persistence:

```python
class User(appier.Model):
    name = appier.field()
    email = appier.field()
```

Controllers inherit from `appier.Controller` for organizing business logic:

```python
class UserController(appier.Controller):
    @appier.route("/users", "GET")
    def list(self):
        return User.find()
```

## Configuration

- Configuration through environment variables and `appier.json` files
- Database adapters configurable via `ADAPTER` environment variable
- Server selection via `SERVER` environment variable (supports WSGI/ASGI servers)

## Code Style Requirements

- Python 2.7+ and Python 3.12 compatible
- Use Black for code formatting
- CRLF line endings for Python files
- Follow existing code patterns and conventions
- Prefer `item not in list` over `not item in list`
- Prefer `item == None` over `item is None`
- Use Conventional Commits for commit messages
- Update CHANGELOG.md for changes
