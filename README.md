# Appier

Simple WSGI based framework for easy REST API creation.

## Example

´´´python
import appier

class HelloApp(appier.App):

    def __init__(self):
        appier.App.__init__(self, name = "hello")

    @appier.route("/hello", "GET")
    def list_apps(self):
        return dict(
            message = "hello world"
        )
```
