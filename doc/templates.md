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

And finally, here's how to access static resources in the app:

```html
<img src="{{ url_for('static', filename = 'images/cats/felix.png') }}" />
```

The previous example will output a link to `static/images/cats/felix.png` from
the root of your app location. All static resources like CSS, Javascript, Images,
and others, should be stored inside the `static` directory (read the [Structure](structure.md)
documentation for more details on how the app file structure works).

## Access control

The template can be processed in such a way, as to show different content depending 
on whether a user is logged in or not, and what access rights that user has. To learn
more, read the [Access Control](access_control.md) documentation.

## Internationalization i18n

Appier supports both the localization thought template output using the `locale` filter
and the localization using multiple template files `x.LOCALE.xxx`.

The framework also sets the global operative system level locale value and so the operative
system must be ready to handle this changes.

Under Unix it's important to generate the appropriate locales for proper usage, otherwise
this global setting would fail to be set.

```bash
less /usr/share/i18n/SUPPORTED
sudo locale-gen pt_PT
sudo locale-gen pt_PT.utf8
```
