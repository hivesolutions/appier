# [Appier Framework](http://appier.hive.pt)

**Joyful Python Web App development**

Appier is a Python framework built for super fast web app development, where your first app is just a few lines long:

```python
import appier

class HelloApp(appier.App):
    
    @appier.route("/", "GET")
    def hello(self): 
        return "hello world"

HelloApp().serve()
```

Running it is just as simple:

```bash
pip install appier
python hello.py
```

It includes the following goodies:

* Object-oriented;
* WSGI compliant;
* RESTful request dispatching;
* Templating, using [Jinja](http://jinja.pocoo.org/);
* Built-in object-relational mapper;
* Automatic JSON response encoding for fast API development;
* Automatic admin interface, using [Appier Extras](https://github.com/hivesolutions/appier_extras);
* Internationalization support.

For the purposes of rapid web development, Appier goes well with [Netius](https://github.com/hivesolutions/netius) 
(web server) and [UXF](https://github.com/hivesolutions/uxf) (client side graphical library) as a whole stack.

### Advanced topics

More information can be found in the [Advanced Topics](advanced.md) page.

## Build Automation

[![Build Status](https://travis-ci.org/hivesolutions/appier.png?branch=master)](https://travis-ci.org/hivesolutions/appier)
