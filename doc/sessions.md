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

Once you want to remove that variable from the session just do:

```python
del self.session["email"]
```

## Persistence

The way a session is persisted is configurable, it can be stored in memory, a file, or a database, for example. To configure the type of session persistence to use, pass the `session_c` keyword in the app initialization:

```python
import appier

class HelloApp(appier.App):
    pass

HelloApp(session_c = session.FileSession).serve()
```

The following session types are currently available:

* MemorySession - 
* FileSession - 
