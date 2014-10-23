# [![Netius](res/logo.png)](http://appier.hive.pt)

**Joyful Python Web App development**

Appier is an object-oriented Python web framework built for super fast app development. It's as lightweight as possible, but not too lightweight. It gives you the power of bigger frameworks, without their complexity.

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

It includes the following goodies:

* Object-oriented
* WSGI compliant
* Python 3 compatible
* RESTful request dispatching
* Templating, using [Jinja](http://jinja.pocoo.org/)
* Data model laye, currently supports [MongoDB](http://www.mongodb.org/)
* Automatic JSON response encoding for fast API development
* Automatic admin interface, using [Appier Extras](https://github.com/hivesolutions/appier_extras)
* Internationalization support
* Flexible project configuration

For the purposes of rapid web development, Appier goes well with [Netius](https://github.com/hivesolutions/netius) 
(web server) and [UXF](https://github.com/hivesolutions/uxf) (client side graphical library) as a whole stack.

## Learn more

* [Requests](doc/requests.md)
* [Models](doc/models.md)
* [Events](doc/events.md)
* [Configuration](doc/configuration.md)
* [Internationalization](doc/i18n.md)

More information can be found in the [Advanced Topics](doc/advanced.md) page.

## Licensing

Appier is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://travis-ci.org/hivesolutions/appier.png?branch=master)](https://travis-ci.org/hivesolutions/appier)
