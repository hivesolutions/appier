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

The App can be configured by defining its init method:

```python
class HelloApp(appier.App):

    def __init__(self, *args, **kwargs):
        appier.App.__init__(
            self,
            name = "app_name",
            *args, **kwargs
        )
```

The basic `App` should seldom be inherited from, instead opt for inheriting from  `APIApp`
or `WebApp`, depending on whether you're building just an API or a complete Web App with
an user interface. These will provide default behaviours that are more appropriate to each
scenario. For example, by inheriting from `WebApp` instead, the following behaviours are
done by default:

* Provide a default handler for the index route, so that the developer can visit the app
through the browser the moment he launches it (without writing any handlers yet).
* Redirects the user to the login page when acess is denied to a particular resource.
* Provides a default HTML error page.
* Defaults 'service' to False.
