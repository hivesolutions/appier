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
