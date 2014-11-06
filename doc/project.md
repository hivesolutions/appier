# Project

Appier projects are typically composed of an [App](doc/app.md) file, a [Configuration](doc/configuration.md) 
file, [Models](doc/models.md), [Controllers](doc/controllers.md), [Templates](doc/templates.md), 
and Static resources.

## App file

The App object encapsulates the application's event loop. It's typically defined and executed
in the same file, making it app's executable file. An example ``hello.py`` file would look like this:

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
you'll get ``Hello World`` as the response.

## Configuration file

The configuration file is a JSON file with settings that can be consulted during the app's runtime. It must be 
named ``appier.json`` and be in the same path as the executable file (in this case ``hello.py``). An example 
file could look like this:

```json
{
    "BASE_URL" : "http://www.test.com"
}
```

The configuration file is optional, it doesn't need to exist for the app to work. Also, settings can be passed
to the app in ways other than from the project configuration file.  check out the [Configuration](doc/configuration.md) documentation.

## Models

Models are a layer of abstraction from the underlying data source. They are kept in the ``models`` folder,
in the root of the project (the ``models`` folder is in the same place as the ``hello.py`` file), with one file
defining each model. A ``Cat`` model could be defined by creating the following ``cat.py`` file in the ``models`` 
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

The ``models`` folder must have an ``__init__.py`` file, importing every model. An example ``__init__.py`` 
file importing the``Cat`` model, and another hypothetical ``Dog`` model, would look like this:

```python
from . import cat
from . import dog

from .cat import Cat
from .dog import Dog
```

There's no need to have an ``__init__.py`` file next to the app file (``hello.py``) to import the ``models``
package, since that package is already imported automatically by Appier.

For more details check out the [Models](doc/models.md) documentation.

## Controllers

Controllers are the bridge from the outside world to the app. They define handlers that listen to requested
URLs, perform logic, and return a response. Typically an handler upon receiving a request will do the following:

* Retrieve entities (instances of a model stored in the data source)
* Invoke their logic (application logic should be encapsulated in the model files)
* Process a template using the retrieved entities
* Return the result of that template having been processed as the response

Controllers are kept in the ``controllers`` folder, in the root of the project (the ``controllers`` folder is 
in the same place as the ``hello.py`` file), with one file defining each controller. A ``CatController`` 
could be defined by creating the following ``cat.py`` file in the ``controllers`` folder:

```python
import appier

import models

class CatController(appier.Controller):

    @appier.route("/cats", "GET")
    def list(self):
    	cats = models.Cat.find()
    	for cat in cats: message.meow()
        return self.template(
            "cat/list.html.tpl",
            cats = cats
        )
```

The ``controllers`` folder must have an ``__init__.py`` file, importing every controller. An example ``__init__.py`` 
file importing the``Cat`` controller, and another hypothetical ``Dog`` controller, would look like this:

```python
from . import cat
from . import dog

from .cat import CatController
from .dog import DogController
```

For more details check out the [Controllers](doc/controllers.md) documentation.

## Templates

Templates are files with logic defined in [Jinja2](http://jinja.pocoo.org/) syntax, whose result after being 
processed is static content:

```python
<table>
    {% for cat in cats %}
    	<tr>
    		<td>{{ cat.name }}</td>
    	</tr>
    {% endfor %}
</table>
```

Templates are kept in the ``templates`` folder, in the root of the project (the ``templates`` folder is 
in the same place as the ``hello.py`` file). Templates can be grouped into sub folders. When templates 
are being processed in a controller, for example, the path provided will be the relative path from the 
``templates`` folder:

```python
return self.template(
    "cat/list.html.tpl",
    cats = cats
)
```

For more details check out the [Templates](doc/templates.md) documentation.

## Static files

Static files are CSS, Images, Javascript files, or any other resource that is to be served to the requesting
application (eg: the browser), without any modifications (as opposed to templates, which are processed before
being served).

Static files are kept in the ``static`` folder, in the root of the project (the ``static`` folder is 
in the same place as the ``hello.py`` file). Static files can be grouped into sub folders. When static 
files are being referenced in a template, for example, the path provided will be the relative path from the 
``static`` folder. For example, here's how to reference a Javascript file located in ``static/js/main.js``:

```html
<script type="text/javascript" src="{{ url_for('static', filename = 'js/main.js') }}"></script>
```
