# Access Control

Routes can be protected so that they can be accessed only by users with 
certain privileges. To do so, decorate the handlers with the `ensure` decorator:

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
@appier.route("/login", "POST")
def login_post(self):
    try: 
    	# attempts to login with the credentials 
    	# specified in the request (the login here
    	# is using plaintext passwords to simplify
    	# the example, never do this in production)
   		email = self.field("email")
   	 	password = self.field("password")
    	account = models.Account.get(
   	        email = email, 
   	       	password = password
   	    )
    except appier.exceptions.OperationalError, error:
        return self.template(
            "signin.html.tpl",
            email = email,
            error = error.message
        )

    # sets the tokens the user has access to 
    # in the session (in this example, all 
    # authenticated users can access resources 
    # protected with the "base" token)
    self.session["tokens"] = ["base"]
    
    # redirects to the main page
    return self.redirect(
   	    self.url_for("base.index")
    )
 
@appier.route("/logout", ("GET", "POST"))
def logout(self):
	# clears the session
    del self.session["tokens"]
    
    # redirects to the main page
    return self.redirect(
        self.url_for("base.index")
    )
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

When a user is unable to access a route due to not having privileges, 
an exception with the 403 error code (forbidden) is raised. Typically
applications redirect the to the login page when access is denied, to
do so here, we have to define the error handler for the 403 error code:

```python
@appier.error_handler(403)
def forbidden_code(self, error):
	return self.redirect("base.signin")
```

To learn more about error handling, read the [Requests](requests.md)
documentation.
