# Models

Appier has a data layer used to abstract the user from the underlying data source.
Currently, the data layer only supports [MongoDB](http://www.mongodb.org/), so be
sure to install it before trying to add models to your app.

A database will be created automatically in MongoDB with name of the app,
and collections will be created with the name of the models. Therefore, if a `Cat`
model is defined in a app called `HelloApp`, a database named `HelloApp` will be
created in MongoDB with a collection named `cat` inside it.

Model attributes can configured by adding keywords to their declaration:

```python
class Cat(appier.Model):

    id = appier.field(
        type = int,
        index = True,
        increment = True
    )

    name = appier.field(
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

## Persistence

To create a cat just do:

```python
cat = Cat()
cat.name = "garfield"
cat.save()
```

Once the cat is saved, a value will be set in its `id` attribute, due to the
`increment` flag being set in the model definition (eg: `1`, `2`). To update the
cat, just make the changes and call `save` again.

To create the cat and have form data be automatically set do this:

```python
cat = Cat.new()
cat.save()
```

Creating a cat this way, will make a form data attribute named `name`,
be applied to the `name` model attribute. The same form mapping behaviour can
also be performed on a cat that already exists:

```python
cat.apply()
```

Deleting the cat is completely straightforward:

```python
cat.delete()
```

### Validation

When the `save` method is called on an entity, it will validate the model first.
The entity will only be saved in case all validations defined for that model pass.
The `validate` method must be implemented to define which validations should
be executed before the entity is saved:

```python
class Cat(appier.Model):

    name = appier.field(
        type = unicode
    )

    @classmethod
    def validate(cls):
        return super(Cat, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name")
        ]
```

In the previous example, if a `Cat` entity was saved with the `name` attribute
unset or set as an empty string, then the entity would not be saved and the
`appier.exceptions.ValidationError` exception would be raised.

The following validation methods are available in Appier:

* `eq` - attribute equal to specified value
* `gt` - attribute greater than specified value
* `gte` - attribute greater than or equal to specified value
* `lt` - attribute less than specified value
* `lte` - attribute less than or equal to specified value
* `not_null` - attribute is not null
* `not_empty` - attribute is not empty (eg: empty array or string)
* `not_false` - ?
* `is_in` - attribute is not in the specified list of values
* `is_simple` - ?
* `is_email` - attribute obeys email regular expression
* `is_url` - attribute obeys url regular expression
* `is_regex` - attribute obeys regular expression
* `field_eq` - attribute is equal to the value of another attribute
* `field_gte` - attribute is greater than or equal to the value of another attribute
* `field_lt` - attribute is less than the value of another attribute
* `field_lte` - attribute is less than or equal to the value of another attribute
* `string_gt` - X
* `string_lt` - X
* `equals` - attribute is equal to specified value
* `not_past` - attribute is a date that is not in the past (comparison is done in UTC)
* `not_duplicate` - attribute is unique in the data source (there isn't another entity
of the same model with the same attribute value)
* `all_different` -
* `no_self` - attribute is not the entity itself

In case there is a situation where we want to execute an extra validation method
for a specific entity, but not to all entities, we can add that validation method
in runtime. For example, if we wanted to run a password strength validator at the
time of an account creation, we would first have to add that validator definition
method to the hypothetical `Account` model:

```python
@classmethod
def validate_password_strength(cls):
    return [
        appier.string_gt("_password", 5)
    ]
```

Afterwards, in the place where the signup logic was being executed (eg: a signup
handler in a controller), we would need to tell the account instance to execute
that validation was well, before calling the `save` method:

```python
account.validate_extra("password_strength")
account.save()
```

## Retrieval

You can retrieve cats whose name is `garfield` by doing the following:

```python
cats = Cat.find(name = "garfield")
```

Or cats whose text is not `garfield`:

```python
cats = Cat.find(name = {"$ne" : "garfield"})
```

You can retrieve cats whose text is `garfield` or `felix`:

```python
cats = Cat.find(name = {"$in" : ("garfield", "felix")})
```

Or cats whose text is not `garfield` nor `felix`:

```python
cats = Cat.find(name = {"$nin" : ("garfield", "felix")})
```

## Referencing the App

In order to invoke methods that belong to the App object, one can access it through
the `owner` attribute. For example, to resolve the URL for a route within a model:

```python
class Cat(appier.Model):

    id = appier.field(
        type = int,
        index = True,
        increment = True
    )

    def get_show_url(self):
        url = self.owner.url_for("cats.show", id = self.id)
        return url
```
