# Structure

Appier projects are typically composed of an [App](app.md) file, a [Configuration](configuration.md)
file, [Models](models.md), [Controllers](controllers.md), [Templates](templates.md), and Static resources.

## App file

The App object encapsulates the application's event loop. It's usually defined and executed
in the same file, making it the app's executable file. An example `hello.py` file could look like this:

```python
import appier

class HelloApp(appier.App):

    @appier.route("/", "GET")
    def hello(self):
        return "Hello World"

HelloApp().serve()
```

The app could then be executed by running:

```python
python hello.py
```

If you then point your browser to [http://localhost:8080/hello](http://localhost:8080/hello),
you'll get `Hello World` as the response.

## Configuration file

The configuration file is a JSON file with settings that can be consulted during the app's runtime. It must be
named `appier.json` and be in the same path as the executable file (in this case `hello.py`). An example
file could look like this:

```json
{
    "BASE_URL" : "http://www.hive.pt"
}
```

The configuration file is optional, it doesn't need to exist for the app to work. Also, settings can be passed
to the app in ways other than from the project configuration file.

For more details, check out the [Configuration](configuration.md) documentation.

## Models

Models are a layer of abstraction from the underlying data source. They are kept in the `models` folder,
at the root of the project (the `models` folder is in the same place as the `hello.py` file), with one file
defining each model. A `Cat` model could be defined by creating the following `cat.py` file in the `models`
folder:

```python
import appier

class Cat(appier.Model):

    id = appier.field(
        type = int,
        index = True,
        increment = True
    )
```

For more details, check out the [Models](models.md) documentation.

## Controllers

Controllers are the bridge from the outside world to the app. They define handlers that listen to requested
URLs, perform logic and return a response. Typically a handler upon receiving a request will do the following:

1. Retrieve entities (instances of a model stored in the data source)
2. Invoke their logic (application logic should be encapsulated in the model files)
3. Process a template using the retrieved entities
4. Return the result of that template having been processed as the response

Controllers are kept in the `controllers` folder, at the root of the project (the `controllers` folder is
in the same place as the `hello.py` file), with one file defining each controller. A `CatController`
could be defined by creating the following `cat.py` file in the `controllers` folder:

```python
import appier

import models

class CatController(appier.Controller):

    @appier.route("/cats", "GET")
    def list(self):
        cats = models.Cat.find()
        for cat in cats: cat.meow()
        return self.template(
            "cat/list.html.tpl",
            cats = cats
        )
```

For more details, check out the [Controllers](controllers.md) documentation.

## Templates

Templates are files with logic defined in [Jinja2](http://jinja.pocoo.org/) syntax, whose result after being
processed is static content:

```python
<table>
    {% for cat in cats %}
        <tr>
            <td>{{ cat.name }}</td>
        </tr>
    {% endfor %}
</table>
```

Templates are kept in the `templates` folder, at the root of the project (the `templates` folder is
in the same place as the `hello.py` file). For better organization, they can be grouped into sub-folders.
When templates are being processed in a controller, for example, the path provided will be the relative
path from the `templates` folder:

```python
return self.template(
    "cat/list.html.tpl",
    cats = cats
)
```

For more details, check out the [Templates](templates.md) documentation.

## Static files

Static files are CSS, Images, Javascript files, or any other resource that is to be served to the requesting
application (eg: the browser), without any modifications (as opposed to templates, which are processed before
being served).

These files are kept in the `static` folder, at the root of the project (the `static` folder is
in the same place as the `hello.py` file), and can be grouped into sub-folders. When static
files are being referenced in a template, for example, the path provided will be the relative path from the
`static` folder. For example, here's how to reference a Javascript file located in `static/js/main.js`:

```html
<script type="text/javascript" src="{{ url_for('static', filename = 'js/main.js') }}"></script>
```
