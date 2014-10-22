# [Appier Framework](http://appier.hive.pt)

**Joyful Python Web App development**

Appier is a Python framework built for super fast web app development. It provides:

* WSGI compliant;
* RESTful request dispatching;
* Templating, using [Jinja](http://jinja.pocoo.org/);
* Built-in object-relational mapper;
* Automatic JSON response encoding for fast API development;
* Automatic admin interface, using [Appier Extras](https://github.com/hivesolutions/appier_extras);
* Internationalization support.

For the purposes of rapid web development, Appier goes well with [Netius](https://github.com/hivesolutions/netius) 
(web server) and [UXF](https://github.com/hivesolutions/uxf) (client side graphical library) as a whole stack.

## Installation

```bash
pip install appier
```

Or download the source from [GitHub](https://github.com/hivesolutions/appier).

Appier has no dependencies, and is therefore cross-platform.

## Example

Creating a simple app takes only a few lines. Just run the following
Python script and check out the result by going to [http://localhost:8080](http://localhost:8080).

```python
import appier

class HelloApp(appier.App):
    
    @appier.route("/", "GET")
    def hello(self): 
        return "hello world"

HelloApp().serve()
```

And adding templating and error handling to the mix is just as easy:

```python
import appier

class HelloApp(appier.App):

    @appier.route("/", "GET")
    def hello(self):
        return self.template(
            "hello.html.tpl",
            message = "hello world"
        )
        
    @appier.error_handler(404)
    def not_found_code(self, error):
        return "404 - The page you requested was not found"

HelloApp().serve()
```

Just don't forget to create a template at "templates/hello.html.tpl":

```html
<p style="font-weight: bold;">
    {{ message }}
</p>
```

### Advanced topics

More information can be found in the [Advanced Topics](advanced.md) page.

## Build Automation

[![Build Status](https://travis-ci.org/hivesolutions/appier.png?branch=master)](https://travis-ci.org/hivesolutions/appier)
