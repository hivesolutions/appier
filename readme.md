# Appier

Simple WSGI based framework for easy REST API creation.

## Example

```python
import appier

class HelloApp(appier.App):

    def __init__(self):
        appier.App.__init__(self, name = "hello")

    @appier.route("/hello", "GET")
    def hello(self):
        return dict(
            message = "hello world"
        )

    @appier.route("/hello/<int:count>", "GET")    
    def hello_count(self, count):
        return dict(
            message = "hello world %d" % count
        )

    @appier.route("/hello.tpl", "GET")
    def hello_template(self):
        return self.template("hello.txt", message = "hello world")

app = HelloApp()
app.serve()
```

## Data Model

### 

### Example

```python
import appier

class Account(appier.Model):

    id = dict(
        index = True,
        increment = True
    )

    username = dict(
        index = True
    )

    email = dict(
        index = True
    )

    password = dict(
        private = True
    )
    
    age = dict(
        type = int
    )
```
