# Templates

Templates in Appier are rendered using [Jinja](http://jinja.pocoo.org/). Therefore,
how to create them is best learned from its website

At the moment, the only detail specific to Appier that is worth noticing, is on how
to resolve URLs. Appier is object-oriented, which amongst other things, allows you 
to have multiple route handlers with the same name, as long as they're in different 
controllers. To render an hyperlink for an handler named ``list_cats`` that is in the
``CatController``, you would do the following:

```html
<a href="{{ url_for('cat.list_cats') }}>List Cats</a>
```

With the syntax explained, all you need to know know is how to render a template
and return it as a response to a request. Here's the handler for the previous example:

```python
import appier

class CatController(appier.Controller):

    @appier.route("/cats", "GET")
    def list_cats(self):
        return self.template(
            "cats/list.html.tpl"
        )
```

The ``list_cats`` handler in this example would render the template in 
``templates/cats/list.html.tpl`` and return it as a response. To make this example more
complete, we would need to retrieve the cats and use them in the template:

```python
cats = models.Cat.find()
return self.template(
    "cats/list.html.tpl",
    cats = cats
)
```

Any keyword arguments passed to the ``template`` method become available in the template:

```html
<table>
    {% for cat in cats %}
    	<tr>
    		<td>{{ cat.name }}</td>
    	</tr>
    {% endfor %}
</table>
```
