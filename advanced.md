# Advanced Topics

This page presents advanced information in a not so structured manner. It is used as both a reference
for external and internal developers, and therefore rewards flexibility over structure.

## Models

Model attributes can configured by adding keywords to their declaration:

```python
class Message(BaseModel):

    text = appier.field(
        type = unicode,
        index = True,
        immutable = True
    )
```

An attribute can be one of the following types:

* `str` - String (this is the default type);
* `unicode` - Unicode (eg: "Eyjafjallajökull");
* `int` - Integer (eg: 5);
* `bool` - Boolean (eg: True);
* `float` - Float (eg: 1.3);
* `list` - List of values (eg: ["a"]);
* `dict` - Key-value dictionary (eg: {"a": 1});
* `appier.File` - Type to be used for referencing file objects;
* `appier.Files` - Used for a set of file references;
* `appier.ImageFile` - Specialized type file for images (allows resizing, etc.);
* `appier.ImageFiles` - Sequence based data type for the image type;
* `appier.reference` - Non relational equivalent of the foreigh reference/key;
* `appier.references` - Multiple items (to many) version of the reference type;

The following keywords can be added to configure the attribute further:

* `index` - Boolean indicating if an index should be created for this attribute in 
the data source (faster searches);
* `increment` - Flag indicating if the value should be automatically generated on 
persistence by adding 1 to the previously generated value;
* `default` - Indicates that the attribute is the default representation for the model
(useful for search operations to be able to decide which attribute to search by default);
* `safe` - Safe attributes cannot be set automatically with the `apply` operation;
* `private` - Private attributes are not retrieved in `get` or `find` operations (useful
to keep passwords safe for example). This behaviour can be bypassed by passing 
`rules = False` to these methods;
* `immutable` - Immutable attributes cannot be modified, they can only be set at creation time.

##  Events

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

## Configuration

Appier can be configured through environment variables. The following would configure the logger to print only messages whose level is Critical or above:

```bash
LEVEL=CRITICAL python hello_world.py
```

The following are all the configuration variables:

* `LEVEL` `str` - Defines the level of verbodity for the loggers (eg: `DEBUG`)
* `FILE_LOG` `bool` - Enables the rotating file based logging (eg: `/var/log/name.log`, `/var/log/name.err`)
* `LOGGING` `list` - Defines a sequence of logging handlers configuration to be loaded (eg: 'complex' example project)

The configuration can also be provided by creating an "appier.json" file:

```json
{
    "LEVEL" : "CRITICAL"
}
```

### Web server

Appier uses the wsgiref web server that comes with the Python standard library by default. You can easily swap it out with a better server like the one provided in [Netius](http://netius.hive.pt) by doing:

```
pip install netius
SERVER=netius python hello_world.py
```

The same goes for every other server currently supported by Appier:

* [Netius](http://netius.hive.pt)
* [Waitress](http://waitress.readthedocs.org/)
* [Tornado](http://www.tornadoweb.org/)
* [CherryPy](http://www.cherrypy.org/)

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
