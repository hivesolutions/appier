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

The ``list`` handler in this example would render the template in 
``templates/cats/list.html.tpl``. To improve the example, we would need 
to retrieve the cats and use them in the template:

```python
cats = models.Cat.find()
return self.template(
    "cat/list.html.tpl",
    cats = cats
)
```

Any keyword arguments passed to the ``template`` method becomes available in the template:

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
``list`` handler in ``CatController``:

```html
<a href="{{ url_for('cat.list') }}">List Cats</a>
```

The ``url_for`` method will check for the existence of a ``BASE_URL`` setting in the app (to
learn how to change app settings check out the [Configuration](doc/configuration.md) documentation),
and in case it is present, it will prefix the resolved URL with that base URL. For example, without
such a setting, processing the previous template would result in:

```html
<a href="/cats">List Cats</a>
```

But if ``BASE_URL`` was set to ``http://www.hive.pt``, then the result would be:

```html
<a href="http://www.hive.pt/cats">List Cats</a>
```
