#  Events

Here's an example of Appier triggering and handling events across different models:

```python
class Report(appier.Model):

    @classmethod
    def setup(cls):
        super(Report, cls).setup()
        account.Account.bind_g("pre_save", cls.handle_pre_save)
        account.Account.bind_g("password_recovered", cls.handle_password_recovered)

    @classmethod
    def handle_pre_save(cls, ctx):
        print "Created '%s'" % ctx.usermame

    @classmethod
    def handle_password_recovered(cls, ctx):
        print "Recovered password for '%s'" % ctx.usermame

class Account(appier.Model):

    def recover_password():
        self.send_email()
        self.trigger("recover_password")
``` 
