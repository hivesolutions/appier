## App

The App object encapsulates the application's event loop. An example app would look like this:

```python
import appier

class HelloApp(appier.App):

    @appier.route("/", "GET")
    def hello(self): 
        return "Hello World"
```

To start the app do the following:

```python
HelloApp().serve()
```
