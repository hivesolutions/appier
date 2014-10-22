# [Appier Framework](http://appier.hive.pt)

**Joyful Python Web App development**

Appier is a WSGI Python framework built for super fast web app development. It provides:

* RESTful request dispatching
* Uses Jinja templating
* WSGI compliant
* Built-in object-relational mapper
* Automatic JSON response encoding for fast API development.
* Automatic admin interface (using [Appier Extras](https://github.com/hivesolutions/appier_extras))
* Internationalization support

For the purposes of rapid web development, Appier goes well with [Netius](https://github.com/hivesolutions/netius) 
(web server) and [UXF](https://github.com/hivesolutions/uxf) (client side graphical library) as a whole stack.

## Installation

```bash
pip install appier
```

Or download the source from [GitHub](https://github.com/hivesolutions/appier).

Appier has no dependencies, and is therefore cross-platform.

## Example

```python
import appier

class HelloApp(appier.App):

    def __init__(self):
        appier.App.__init__(self, name = "hello")

    @appier.route("/hello", "GET")
    def hello(self):
        return dict(
            message = "hello world"
        )

    @appier.route("/hello/<int:count>", "GET")    
    def hello_count(self, count):
        return dict(
            message = "hello world %d" % count
        )

    @appier.route("/hello.tpl", "GET")
    def hello_template(self):
        return self.template(
            "hello.txt",
            message = "hello world"
        )

    @appier.exception_handler(appier.NotFoundError)
    def not_found(self, error):
        return "Not found error"

    @appier.error_handler(404)
    def not_found_code(self, error):
        return "404 - Not found"

app = HelloApp()
app.serve()
```

### Advanced topics

More information can be found in the [Advanced Topics](advanced.md) page.

## Build Automation

[![Build Status](https://travis-ci.org/hivesolutions/appier.png?branch=master)](https://travis-ci.org/hivesolutions/appier)
