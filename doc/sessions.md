# Sessions

The session object can be acessed through [Models](models.md) or [Controllers](controllers.md)
in the same way. Here's how you'd set the email of a logged in user in the session:

```python
self.session["email"] = email
```

Once set in the session, this value will be accessible by the same client across requests:

```python
email = self.session["email"]
```

You can access the session object in directly in any template as well:

```html
<p>Logged in as {{ session.email }}</p>
```

If you want to remove the variable from the session just do:

```python
del self.session["email"]
```

## Persistence

The way a session is persisted is configurable, it can be stored in memory, a file, or a database, for example. To configure the type of session persistence to use, pass the `session_c` keyword in the app initialization:

```python
import appier

class HelloApp(appier.App):

    def __init__(self):
        appier.App.__init__(
            self,
            session_c = appier.session.FileSession
        )

HelloApp().serve()
```

The following session types are currently available:

* `MemorySession` - stores session values in memory (session is lost when app is stopped and relaunched) 
* `FileSession` - stores values in a [Shelve](https://docs.python.org/library/shelve.html) named `session.shelve.db` in the app root directory (session is kept even if the app is stopped and relaunched)
