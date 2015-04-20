# Templates

Templates in Appier are rendered using [Jinja2](http://jinja.pocoo.org/). Learning
its syntax is not the purpose of this guide, and is best learned from its
[website](http://jinja.pocoo.org/).

Here's how to render a template and return it as a response:

```python
import appier

class CatController(appier.Controller):

    @appier.route("/cats", "GET")
    def list(self):
        return self.template(
            "cat/list.html.tpl"
        )
```

The `list` handler in this example would render the template in
`templates/cats/list.html.tpl` (read the [Structure](structure.md)
documentation for more details on how the app file structure works).
To improve the example, we would need to retrieve the cats and use
them in the template:

```python
cats = models.Cat.find()
return self.template(
    "cat/list.html.tpl",
    cats = cats
)
```

Any keyword arguments passed to the `template` method becomes available in the template:

```html
<table>
    {% for cat in cats %}
        <tr>
            <td>{{ cat.name }}</td>
        </tr>
    {% endfor %}
</table>
```

At the moment, the only detail specific to Appier that is worth noticing, is how to resolve
URLs for handlers specified in controllers. Here's how you would render a link to the
`list` handler in `CatController`:

```html
<a href="{{ url_for('cat.list') }}">List Cats</a>
```

The `url_for` method will resolve a path relative to the host. In order to resolve an absolute path
(links sent out in emails must be absolute URLs for example) do the following:

```html
<a href="{{ url_for('cat.list', absolute = True) }}">List Cats</a>
```

The `absolute` named argument will make the resolved URL be prefixed with the value specified
in the `BASE_URL` configuration setting. To learn more, read the [Configuration](configuration.md)
documentation.

Here's how to access static resources in the app:

```html
<img src="{{ url_for('static', filename = 'images/cats/felix.png') }}" />
```

In case you want the resource to be compressed to lessen bandwidth usage, you can pass the `compress` flag.

```html
<img src="{{ url_for('static', filename = 'images/cats/felix.png', compress = True) }}" />
```

In this example, the flag will have a behaviour appropriate to the specified resource.
In this case, it would return a JPEG instead of a PNG (the JPEG would be created on-the-fly 
and cached, so future requests won't trigger compression again).

The previous example will output a link to `static/images/cats/felix.png` from
the root of your app location. All static resources like CSS, Javascript, Images,
and others, should be stored inside the `static` directory (read the [Structure](structure.md)
documentation for more details on how the app file structure works).

## Reserved variables

A series of variables are injected into the template for easy reference. For example,
if you wanted to print the email of the currently logged in user (provided is email
is set in the session object), you could do the following:

```html
<p>Logged in as {{ session.email }}</p>
```

Here is the of variables that are always accessible in a template:

* `own` - the [controller](controllers.md) where the template was rendered
* `request` - the [request](requests.md) whose handler rendered the template
* `session` - the [session](sessions.md) object for the user
* `location` - the relative path for the URL whose handling resulted in the rendering of the template
* `config` - the settings defined in the app [configuration](configuration.md)

## Access control

The template can be processed in such a way, as to show different content depending
on whether a user is logged in or not, and what access rights that user has. To learn
more, read the [Access Control](access_control.md) documentation.

## Internationalization (i18n)

To support multiple languages, specify the locale before the extension of each template.
For example, if you had an index template named `index.html.tpl`, and wanted to add support
for English and Portuguese, you should have the following two files instead: `index.pt_pt.html.tpl`
and `index.en_us.html.tpl`.
