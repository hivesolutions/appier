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

class Message(appier.Model):

    id = appier.field(
        index = True,
        increment = True
    )

    text = appier.field()

class HelloApp(appier.App):

    @appier.route("/messages/new", "GET")
    def new_message(self):
        message = Message.new()
        message.text = "hello world %d" % (Message.count() + 1)
        message.save()
        return "created message %s" % message.text

    @appier.route("/messages/<int:id>.json", "GET")
    def show_message_json(self, id):
        return Message.get(id = id, map = True)

    @appier.route("/messages.json", "GET")
    def list_messages_json(self):
        return Message.find(map = True)

    @appier.route("/messages.tpl", "GET")
    def list_messages_tpl(self):
        return self.template(
            "messages.html.tpl",
            messages = Message.find(map = True)
        )

    @appier.error_handler(404)
    def not_found_code(self, error):
        return "404 - The page you requested was not found"

app = HelloApp()
app.serve()
```

### Advanced topics

More information can be found in the [Advanced Topics](advanced.md) page.

## Build Automation

[![Build Status](https://travis-ci.org/hivesolutions/appier.png?branch=master)](https://travis-ci.org/hivesolutions/appier)
