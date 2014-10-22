# Routing

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
