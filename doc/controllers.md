# Controllers

Controllers are the bridge from the outside world to the app. They define handlers that listen to requested
URLs, perform logic, and return a response. Typically an handler upon receiving a request will do the following:

1. Retrieve entities (instances of a model stored in the data source)
2. Invoke their logic (application logic should be encapsulated in the model files)
3. Process a template using the retrieved entities
4. Return the result of that template having been processed as the response

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

Controller responses can be a redirect, instead of an output:

```python
@appier.route("/cats/<int:id>", "GET")
def show(self, id):
	return self.redirect(
	    self.url_for("animal.show", id = id)
	)
```

There's not much else to say about controllers, other than stating the best practice
of avoiding to write application logic in controllers. Controllers are only meant for 
invoking methods and returning results. They are meant to knit together existing logic 
in a meaningful way and making it available to the outside world; logic belongs to 
[Models](models.md).

For further details on how to create routes to make controller methods acessible to
the outside world read the [Requests](requests.md) documentation.
