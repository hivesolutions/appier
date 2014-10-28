# Requests

Appier maps request URLs to methods using the ``route`` decorator on top of each handler method:

```python
import appier

class HelloApp(appier.App):

    @appier.route("/", "GET")
    def hello(self):
        return "hello from /"

HelloApp().serve()
```

The previous code will handle the base URL, so if you go to [http://localhost:8080](http://localhost:8080), you should get an hello message as the response.

You can handle a longer URL path:

```python
@appier.route("/directory/test", "GET")
def hello(self):
    return "hello from /directory/test"
```

Handling ``POST`` requests instead of ``GET`` is just as easy:

```python
@appier.route("/directory/test", "POST")
def hello(self):
    return "hello from /directory/test"
```

Or you can handle both request types with the same handler:

```python
@appier.route("/file", ("GET", "POST"))
def hello(self):
    return "hello from /file"
```

You can capture parameters from the URL:

```python
@appier.route("/directory/<file>", "GET")
def hello(self, file):
    return "hello from /directory/" + file
```

And specify which type those parameters are:

```python
@appier.route("/directory/<int:file_number>", "GET")
def hello(self, file_number):
    return "hello from /directory/%d.txt" + file_number
```

You can handle multiple URLs with the same method:

```python
@appier.route("/file1", "GET")
@appier.route("/file2", "GET")
def hello(self):
    return "hello from /filex"
```

If you were to call [http://localhost:8080/file?file_name=test](http://localhost:8080/file?file_name=test),
here's how you would retrieve the file name parameter (same goes for form data):

```python
@appier.route("/file", ("GET", "POST"))
def hello(self):
    file_name = self.field("file_name")
    return "hello from /file?file_name=%s" % file_name
```

It can also cast those parameters for you:

```python
@appier.route("/file", ("GET", "POST"))
def hello(self):
    file_name = self.field("file_number", int)
    return "hello from /file?file_number=%d" % file_number
```

You can return custom responses for specific error codes:

```python
@appier.error_handler(404)
def not_found_code(self, error):
    return "404 - The page you requested was not found”
```

You can also return custom respones to unhandled exceptions 
(eg: an object you tried to retrieve was not found):

```python
@appier.exception_handler(appier.NotFoundError)
def not_found(self, error):
    return "The object you requested was not found”
```
