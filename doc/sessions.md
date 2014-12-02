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

