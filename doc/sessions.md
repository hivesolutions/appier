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
* `RedisSession` - stores values in a [Redis](http://redis.io/) server should be used together with the `REDISTOGO_URL` configuration variable
* `ClientSession` - stores values using cookies on the client, this is considered safe (message signed) avoid tampering from the client side

## Transient

To hold the session variables only for the duration of the request's lifecycle (eg: for authenticating the request with an oauth token), transient session variables can be set instead. These act just like regular session variables, therefore leveraging every other session-dependent feature for the duration of that request.

To set a transient session value:

```python
self.session.set_t("email", "email")
```

To retrieve it later on you can just to a regular session value retrieval:

```python
email = self.session["email"]
```

Or you may want to explicitly state that you are looking for a transient value (will not retrieve regular values):

```python
self.session.get_t("email")
```

In case you want to delete it (not necessary in most cases, as it will be discarded at the end of the request):

```python
self.session.delete_t("email")
```
