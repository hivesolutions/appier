# Requests

Appier maps request URLs to methods using a `route` decorator on handler methods:

```python
import appier

class HelloApp(appier.App):

    @appier.route("/", "GET")
    def hello(self):
        return "hello from /"

HelloApp().serve()
```

The previous code will handle the base URL. If you go to [http://localhost:8080](http://localhost:8080),
you should get an hello message as the response.

You can handle a longer URL path:

```python
@appier.route("/cats/garfield", "GET")
def hello(self):
    return "hello from garfield"
```

Handling `POST` requests instead of `GET` is just as easy:

```python
@appier.route("/cats/garfield", "POST")
def hello(self):
    return "hello from /cats/garfield"
```

The same handler can also handle both request types:

```python
@appier.route("/cats/garfield", ("GET", "POST"))
def hello(self):
    return "hello from /cats/garfield"
```

It can also handle multiple URLs:

```python
@appier.route("/cats/garfield", "GET")
@appier.route("/cats/felix", "GET")
def hello(self):
    return "hello from garfield or felix (not sure which)"
```

## Parameters

You can easily capture parts of the URL:

```python
@appier.route("/cats/<name>", "GET")
def hello(self, name):
    return "hello from %s" % name
```

Those parts can be automatically casted for you by specifying their type:

```python
@appier.route("/numbers/<int:number>", "GET")
def hello(self, number):
    return "this is number %d" % number
```

If you were to call [http://localhost:8080/cats?name=garfield](http://localhost:8080/cats?name=garfield),
here's how you would retrieve the name parameter (same goes for form data):

```python
@appier.route("/cats", ("GET", "POST"))
def hello(self):
    name = self.field("name")
    return "hello from %s" % name
```

Parameters can also be casted for you by specifying their type:

```python
@appier.route("/numbers", ("GET", "POST"))
def hello(self):
    number = self.field("number", int)
    return "this is number %d" % number
```

## Errors

You can return custom responses for specific error codes:

```python
@appier.error_handler(404)
def not_found_code(self, error):
    return "404 - The page you requested was not found"
```

You can also return custom responses to unhandled exceptions
(eg: an object you tried to retrieve was not found):

```python
@appier.exception_handler(appier.NotFoundError)
def not_found(self, error):
    return "The object you requested was not found"
```

## Access control

Routes can be protected so that they can be accessed only by
certain authenticated users. To learn more, read the [Access Control](access_control.md)
documentation.
