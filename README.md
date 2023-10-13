# [![Appier Framework](res/logo.png)](http://appier.hive.pt)

**Joyful Python Web App development**

Appier is an object-oriented Python web framework built for super-fast app development.
It's as lightweight as possible, but not too lightweight.
It gives you the power of bigger frameworks, without their complexity.

Your first app can be just a few lines long:

```python
import appier

class HelloApp(appier.App):

    @appier.route("/", "GET")
    def hello(self):
        return "Hello World"

HelloApp().serve()
```

The same app using the async/await syntax (Python 3.5+) for async execution reads pretty much the same:

```python
import appier

class HelloApp(appier.App):

    @appier.route("/", "GET")
    async def hello(self):
        await self.send("Hello World")

HelloApp().serve()
```

Running it is just as simple:

```bash
pip install appier
python hello.py
```

For the async version an [ASGI](https://asgi.readthedocs.io) compliant server should be used (eg: [Uvicorn](https://www.uvicorn.org)):

```bash
SERVER=uvicorn python hello.py
```

Your "Hello World" app is now running at [http://localhost:8080](http://localhost:8080).

It features the following:

* Object-oriented
* [WSGI](https://www.python.org/dev/peps/pep-0333/) (Web Server Gateway Interface) compliant
* [ASGI](https://asgi.readthedocs.io) (Asynchronous Server Gateway Interface) ready
* Modular, using dynamically loaded parts
* Python 3 compatible
* RESTful request dispatching
* Asynchronous request handling support
* Templating, using [Jinja2](http://jinja.pocoo.org/)
* Data model layer, currently supports [MongoDB](http://www.mongodb.org/) and [TinyDB](http://tinydb.readthedocs.org/)
* Automatic JSON response encoding for fast API development
* Automatic admin interface, using [Appier Extras](http://appier-extras.hive.pt/)
* Internationalization (i18n) support
* Flexible project configuration
* Out-of-the-box support for multiple [WSGI](https://wsgi.readthedocs.io/) and [ASGI](https://asgi.readthedocs.io/) servers: [Netius](https://netius.hive.pt), [Uvicorn](https://www.uvicorn.org), [Hypercorn](https://pgjones.gitlab.io/hypercorn), [Daphne](https://github.com/django/daphne), etc.

For the purposes of rapid web development, Appier goes well with [Netius](http://netius.hive.pt)
(web-server) and [UXF](http://uxf.hive.pt) (client-side graphical library) as a whole stack.

## Learn more

### Basic

* [Structure](doc/structure.md) - how to setup the basic structure of your app
* [App](doc/app.md) - the application workflow object
* [Configuration](doc/configuration.md) - how to configure your app
* [Models](doc/models.md) - how to save and retrieve data
* [Controllers](doc/controllers.md) - how to route input and output
* [Templates](doc/templates.md) - how to render output
* [Requests](doc/requests.md) - how to handle requests
* [Sessions](doc/sessions.md) - how to keep user data across requests
* [Access Control](doc/access_control.md) - how to protect resources

### Advanced

* [Events](doc/events.md) - how to send information across the app
* [Logging](doc/logging.md) - how to log your app's activity
* [Email](doc/email.md) - how to send emails

## License

Appier is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://app.travis-ci.com/hivesolutions/appier.svg?branch=master)](https://travis-ci.com/github/hivesolutions/appier)
[![Build Status GitHub](https://github.com/hivesolutions/appier/workflows/Main%20Workflow/badge.svg)](https://github.com/hivesolutions/appier/actions)
[![Coverage Status](https://coveralls.io/repos/hivesolutions/appier/badge.svg?branch=master)](https://coveralls.io/r/hivesolutions/appier?branch=master)
[![PyPi Status](https://img.shields.io/pypi/v/appier.svg)](https://pypi.python.org/pypi/appier)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/)
