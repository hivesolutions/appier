# Access Control

Routes can be protected so that only authenticated users can access them.
To do so, decorate the handlers with the `@private` decorator:

```python
@appier.route("/", "GET")
@private
def hello(self):
    return "hello from /"
```

When a user is unable to access a route due to not having privileges, 
an exception with the 403 error code (forbidden) is raised. This error
can be handled to send the user to the login page for example:

```python
@appier.error_handler(403)
def forbidden_code(self, error):
    return self.redirect("base.signin")
```

In order to allow access to only some of the authenticated users, 
use the `@ensure` decorator instead:

```python
@appier.route("/", "GET")
@appier.ensure(token = "base")
def hello(self):
    return "hello from /"
```

The `token` keyword specifies the token that must be present in the current
[Session](sessions.md), for this route to be accessible. When a user is logged
in, the tokens he has access to should be set in the reserved `tokens` session
variable like so:

```python
self.session["tokens"] = ["base"]
```

And deleted when the user logs out:

```python
del self.session["tokens"]
```

In this example, all authenticated users would be able to access routes protected 
with the `base` token, they wouldn't however, be able to access another route 
protected with an `admin` token. To be able to access both, a list with both tokens 
would have to be set in the session:

```python
self.session["tokens"] = ["base", "admin"]
```

There is however, a special token that allows users to access any protected
resource, regardless of what token it is protected with:

```python
self.session["tokens"] = ["*"]
```

This special token should rarely be used though. It can be used to easily
define the access rights of an administrator user that can do anything
another user can, but such usage is discouraged for security reasons.

## Templates

The access rights of an user can be checked in templates in order to output
only the content that should be visible to each access level. Here's how to 
show different content depending on whether the user is logged in or not:

```html
{% if session.email %}
    <p>Logged in</p>
{% else %}
    <p>Not logged in</p>
{% endif %}
```

This example is checking for the existence of the `email` attribute in the 
session object to determine if the user is logged in or not, however any
session variable will do, as long as it's one that is only set if the user
is logged in.

To change the output depending on the authenticated user's access level,
one can check through the template if the user has a certain token:

```html
{% if session.email %}
    {% if acl('admin') %}
        <p>Logged in as admin</p>
    {% else %}
        <p>Logged in as a normal user</p>
    {% endif %}
{% else %}
    <p>Not logged in</p>
{% endif %}
```
