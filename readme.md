# [![Appier Framework](res/logo.png)](http://appier.hive.pt)

**Joyful Python Web App development**

Appier is an object-oriented Python web framework built for super fast app development.
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

Running it is just as simple:

```bash
pip install appier
python hello.py
```

It features the following:

* Object-oriented
* WSGI compliant
* Python 3 compatible
* RESTful request dispatching
* Templating, using [Jinja2](http://jinja.pocoo.org/)
* Data model layer, currently supports [MongoDB](http://www.mongodb.org/)
* Automatic JSON response encoding for fast API development
* Automatic admin interface, using [Appier Extras](http://appier_extras.hive.pt)
* Internationalization (i18n) support
* Flexible project configuration

For the purposes of rapid web development, Appier goes well with [Netius](http://netius.hive.pt) 
(web server) and [UXF](http://uxf.hive.pt) (client side graphical library) as a whole stack.

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

### Advanced
* [Events](doc/events.md) - how to send information across the app
* [Logging](doc/logging.md) - how to log your app's activity
* [Email](doc/email.md) - how to send emails
* [Advanced Topics](doc/advanced.md) - miscellaneous advanced topics

## License

Appier is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://travis-ci.org/hivesolutions/appier.png?branch=master)](https://travis-ci.org/hivesolutions/appier)
[![Coverage Status](https://coveralls.io/repos/hivesolutions/appier/badge.png?branch=master)](https://coveralls.io/r/hivesolutions/appier?branch=master)
[![PyPi Status](https://pypip.in/v/appier/badge.png)](https://pypi.python.org/pypi/appier)
