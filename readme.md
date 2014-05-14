# Appier Framework

Simple WSGI based framework for easy REST API creation. It aims at creating simple infra-structure for the
consulting work that is being developed by the Hive Solutions team.

This project should be used together with the [Appier Framework Extras](https://github.com/hivesolutions/appier_extras)
project to provide a simple and fas framework for the creation of "admin" based projects.

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

    @appier.exception_handler(appier.NotFoundError)
    def not_found(self, error):
        return "Not found error"

    @appier.error_handler(404)
    def not_found_code(self, error):
        return "404 - Not found"

app = HelloApp()
app.serve()
```

## Configuration

* `LEVEL` `str` - Defines the level of verbodity for the loggers (eg: `DEBUG`)
* `FILE_LOG` `bool` - Enables the rotating file based logging (eg: `/var/log/name.log`, `/var/log/name.err`)

## Data Model

### Attributes

* `type` - The data type to be used for the attribute
* `index` - Boolean indicating if the attribute should be indexed in the data source
* `increment` - Flag that defines if the (integer based) attribute should be incremented on create
* `default` - Sets the current attribute as the default one (representing the class) so that for
instance any search operation uses this field as pivot in the search query
* `safe` - Sets the attribute as safe meaning that it cannot be set automatically with the `apply`
for example in the `new` operation, an attribute with this flag set must be set explicitly in the
controller before the save operation (protected for write)
* `private` - Indicates if the attribute should not be set on the build operation, any attribute
with this flag won't be able to be read without setting the special `rules = False` parameter in
the `get` or `find` operations (protected for read)
* `immutable` - Flag that indicates that the attribute is immutable, meaning that it cannot be changed
after the initial create operation (securty feature)

### Types

* `str` - The string type for text fields (this is the default type)
* `unicode` - Equal to the `str` type but supports unicode characters
* `int` - Number type to be used for integer values
* `bool` - Boolean value used for bool base evaluation
* `float` - Floating point type for real values
* `list` - Type to be used for sequences of values
* `dict` - Map type to be used for mapping keys to values
* `appier.File` - Type to be used for referencing file objects
* `appier.Files` -
* `appier.ImageFile` -
* `appier.ImageFiles` -
* `appier.reference` -
* `appier.references` -

### Filters

* `equals` -
* `not_equals` -
* `in` -
* `not_in` -
* `like` -
* `rlike` -
* `llike` -
* `greater` -
* `greater_equal` -
* `lesser` -
* `lesser_equal` -
* `is_null` -
* `is_not_null` -

## Internationalization i18n

Appier supports both the localization thought template output using the `locale` filter
and the localization using multiple template files `x.LOCALE.xxx`.

The framework also sets the global operative system level locale value and so the operative
system must be ready to handle this changes.

Under Unix it's important to generate the appropriate locales for proper usage, otherwise
this global setting would fail to be set.

```bash
less /usr/share/i18n/SUPPORTED
sudo locale-gen pt_PT
sudo locale-gen pt_PT.utf8
```

### Example

```python
import appier

class Account(appier.Model):

    id = appier.field(
        index = True,
        increment = True
    )

    username = appier.field(
        index = True
    )

    email = appier.field(
        index = True
    )

    password = appier.field(
        private = True
    )

    age = appier.field(
        type = int
    )
```

##  Event Driven / Aspect Oriented

Appier supports a series of event driven techniques that may be used to
decouple the various components of the application.

### Example

```python
class Report(appier.Model):

    @classmethod
    def setup(cls):
        super(Report, cls).setup()
        account.Account.bind_g("pre_save", cls.notify_created)
        account.Account.bind_g("recover_password", cls.notify_recover)

    @classmethod
    def notify_created(cls, ctx):
        print "Created '%s'" % ctx.usermame

    @classmethod
    def notify_recover(cls, ctx):
        print "Recovered password for '%s'" % ctx.usermame

class Account(appier.Model):

    def recover_password():
        self.send_email()
        self.trigger("recover_password")
``` 

## Build Automation

[![Build Status](https://travis-ci.org/hivesolutions/appier.png?branch=master)](https://travis-ci.org/hivesolutions/appier)
