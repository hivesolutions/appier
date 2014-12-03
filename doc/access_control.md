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
can be handled to forward the user to the login page for example:

```python
@appier.error_handler(403)
def forbidden_code(self, error):
    return self.redirect("base.signin")
```

In order to allow only some authenticated users access, as oposed to
all authenticated users, use the `@ensure` decorator instead:

```python
@appier.route("/", "GET")
@appier.ensure(token = "base")
def hello(self):
    return "hello from /"
```

The `token` keyword specifies the token that must be present in the current
[Session](sessions.md), for this route to be accessible. When a user is logged
in, the tokens he has access to should be set in the reserved `tokens` session
variable, and removed when the user logs out. Here's a basic example of login
and logout handlers doing so:

```python
self.session["tokens"] = ["base"]
```

In this previous example, all authenticated users would be able to access
routes protected with the `base` token, they wouldn't however, be able to
access another route protected with an `admin` token, for example. To be able
to access both, a list with both tokens would have to be set in the session:

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

To learn more about error handling, read the [Requests](requests.md)
documentation.
