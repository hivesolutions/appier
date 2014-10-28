# Models

Appier has a data layer used to abstract the user from the underlying data source. 
Currently, the data layer only supports [MongoDB](http://www.mongodb.org/), so be
sure to install it before trying to add models to your app.

Model attributes can configured by adding keywords to their declaration:

```python
class Message(appier.Model):
    
    id = appier.field(
        type = int,
        index = True,
        increment = True
    )
    
    text = appier.field(
        type = unicode,
        index = True
    )
```

An attribute can be one of the following types:

* `str` - String (this is the default type)
* `unicode` - Unicode (eg: `Eyjafjallajökull`)
* `int` - Integer (eg: `5`)
* `bool` - Boolean (eg: `True`)
* `float` - Float (eg: `1.3`)
* `list` - List of values (eg: `["a"]`)
* `dict` - Key-value dictionary (eg: `{"a": 1}`)
* `appier.File` - Python file object
* `appier.Files` - List of Python file objects
* `appier.ImageFile` - Specialized type file for images (allows resizing, etc.)
* `appier.ImageFiles` - Sequence based data type for the image type
* `appier.reference` - Non relational equivalent of the foreigh reference/key
* `appier.references` - Multiple items (to many) version of the reference type

The following keywords can be added to configure the attribute further:

* `index` - Boolean indicating if an index should be created for this attribute in 
the data source (faster searches)
* `increment` - Flag indicating if the value should be automatically generated on 
persistence by adding 1 to the previously generated value
* `default` - Indicates that the attribute is the default representation for the model
(useful for search operations to be able to decide which attribute to search by default)
* `safe` - Safe attributes cannot be set automatically with the `apply` operation
* `private` - Private attributes are not retrieved in `get` or `find` operations (useful
to keep passwords safe for example). This behaviour can be bypassed by passing 
`rules = False` to these methods
* `immutable` - Immutable attributes cannot be modified, they can only be set at creation time

### Persistence

To create a message just do:

```python
message = Message()
message.text = "testing"
message.save()
```

Once the message is saved, a value will be set in its ``id`` attribute, due to the
``increment`` flag being set in the model definition (eg: ``1``, ``2``). To update the 
message, just make the changes and call ``save`` again. 

To create the message and have form data be automatically set do this:

```python
message = Message.new()
message.save()
```

Creating a message this way, will make a form data attribute named ``text``,
be applied to the ``text`` model attribute. The same form mapping behaviour can 
also be performed on a message that already exists:

```python
message.apply()
```

Deleting the message is completely straightforward:

```python
message.delete()
```

### Retrieval

You can retrieve messages whose text is ``hello`` by doing the following:

```python
messages = Message.find(text = "hello")
```

Or messages whose text is not ``hello``:

```python
messages = Message.find(text = {"$ne" : "hello"})
```

You can retrieve messages whose text is ``hello`` or ``world``:

```python
messages = Message.find({"in" : ("hello", "world")})
```

Or messages whose text is not ``hello`` nor ``world``:

```python
messages = Message.find({"not_in" : ("hello", "world")})
```

* `equals` - 
* `not_equals` -
* `like` -
* `llike` -
* `rlike` -
* `greater` -
* `greater_equal` -
* `lesser` -
* `lesser_equal` -
* `is_null` -
* `is_not_null` -
* `contains` -
