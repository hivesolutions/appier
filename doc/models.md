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
* `initial` - Value indicating the initial value that should be placed in the model
for that attribute when creating a new instance, if not specified the default value
of the data type of the attribute is used instead
* `increment` - Flag indicating if the value should be automatically generated on
persistence by adding 1 to the previously generated value
* `eager` - Boolean indicating if the reference (or lazy loaded) value should be loaded
by default for `get` operations or `find` operations if the `eager_l` flag set
* `default` - Indicates that the attribute is the `default` representation for the model
(useful for search operations to be able to decide which attribute to search by default).
In case there are multiple defaults in the hierarchy (eg: `Cat` has a default attribute
and it inherits from `Animal`, which also has its own default attribute), then the most
concrete level of the hierarchy has priority (`Cat` in the previous example).
* `safe` - Safe attributes cannot be set automatically with the `apply` operation. This
behaviour can be bypassed by passing `safe_a = False` to the `apply` method.
* `private` - Private attributes are not retrieved in `get` or `find` operations (useful
to keep passwords safe for example). This behaviour can be bypassed by passing
`rules = False` to these methods
* `immutable` - Immutable attributes cannot be modified, they can only be set at creation time

## Persistence

To create a cat just do:

```python
cat = Cat()
cat.name = "Garfield"
cat.save()
```

Once the cat is saved, a value will be set in its `id` attribute, due to the
`increment` flag being set in the model definition (eg: `1`, `2`). To update the
cat, just make the changes and call `save` again.

To create the cat and have form data be automatically set in it do this:

```python
cat = Cat.new()
cat.save()
```

Creating a cat this way, will make a form data attribute named `name`
be applied to the `name` model attribute. The same form mapping behaviour can
also be performed on a cat that already exists:

```python
cat.apply()
```

If you want to delete the cat then do:

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

    age = appier.field(
        type = int
    )

    @classmethod
    def validate(cls):
        return super(Cat, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name"),
            appier.gte("age", 5)
        ]
```

In the previous example, if a `Cat` entity was saved with the `name` attribute
unset or set as an empty string, then the entity would not be saved and the
`appier.exceptions.ValidationError` exception would be raised. This exception
has an `errors` attribute which includes the failed validations. Upon a validation
having failed, an `errors` map could look like the following:

```python
{
    'name': ['value is null', 'value is empty'],
    'age': ['is not greater than 5']
}
```

The messages after each failed validation are created using the defaults associated
with the validation methods. These messages can be customized by specifying the `message`
keyword when defining the model validators:

```python
appier.not_empty("name", message = "Please specify the name (mandatory)")
```

The following validation methods are available in Appier:

* `eq` - equal to specified value (eg: `appier.eq("age", 5)`)
* `gt` - greater than specified value
* `gte` - greater than or equal to specified value
* `lt` - less than specified value
* `lte` - less than or equal to specified value
* `not_null` - not equal to null (eg: `appier.not_null("name")`)
* `not_empty` - not an empty collection like a string or an array
* `not_false` - not equal to `False`
* `is_in` - in the specified list of values (eg: `appier.is_in("name", ("Garfield", "Catbert")`)
* `is_simple` - simple enough to be safely used as part of an URL
* `is_email` - is a valid email
* `is_url` - is a valid URL
* `is_regex` - matches regular expression (eg: `appier.is_regex("name", "cat*")`)
* `field_lt` - less than the value of another attribute (eg: `appier.field_eq("age", "birth_year"`)
* `field_lte` - less than or equal to the value of another attribute
* `field_eq` - equal to the value of another attribute
* `field_gte` - greater than or equal to the value of another attribute
* `string_gt` - string length is greater than the specified number of characters
* `string_lt` - string length is less than the specified number of characters
* `not_past` - attribute is a date that is not in the past (comparison is done in UTC)
* `not_duplicate` - attribute is unique in the data source (there isn't another entity
of the same model with the same attribute value)
* `all_different` - all objects in the list are different (they don't have the same `id`)
* `no_self` - validated entity is not in the list

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

You can retrieve a cat named `Garfield` doing the following:


```python
number_cats = Cat.count()
number_garfields = Cat.count(name = "Garfield")
```

Or retrieve all cats, and find all cats named `Garfield`:

```python
cats = Cat.find()
garfields = Cat.find(name = "Garfield")
```

Or count all cats, as well as all named `Garfield`:

```python
number_cats = Cat.count()
number_garfields = Cat.count(name = "Garfield")
```

The `get`, `find` and `count` operations can all use the same kinds of filters.
These filters can be simple equality filters, or more advanced:

```python
not_garfield = Cat.get(name = {"$ne" : "Garfield"})
number_not_garfields = Cat.count(name = {"$ne" : "Garfield"})
number_garfields = Cat.find(name = {"$ne" : "Garfield"})
```

Advanced query operators like `$ne` are the same as the ones available in
[MongoDB](http://www.mongodb.org/). For documentation on those please read
the [MongoDB documentation](http://docs.mongodb.org/manual/reference/operator/query/).

The following is a list of extra named arguments that can be passed to the `find` and
`get` methods to configure the query and its results:

* `skip` (`int`) - the number of the first record to retrieve from the results (eg: in case there
were 10 results and this argument was set to 5, then only the last 5 results would be retrieved)
* `limit` (`int`) - the number of results to retrieve (eg: in case there were 10 results and this
argument was 3, then only the first 3 results would be returned; however if `skip` was also specified
and it was 2, then only the 2nd, 3rd and 4th results would be retrieved)
* `sort` (`list`) - list of arguments to sort the results by, and which direction to sort them in
(eg: `[("age", 1)]` would sort by the `age` attribute in ascending order, while `[("age", -1)]` would
do it in descending order; the results can be sorted by multiple fields as well, like `[("age", -1), ("name", 1)]`)
* `fields` (`list`) - the attributes that should be returned in the results (defaults to all attributes)
* `eager` (`list`) - sequence containing the fields that should be eager loaded, relevant for relation
based attributes (impacts performance)
* `eager_l` (`bool`) - if the model defined eager fields definition should be applied to the operation, note
that this value is set by default on `get` operations and unset on `find` operations
* `map` (`bool`) - indicates if the results should be returned as lists and dictionaries instead of model
instances, for easier serialization (defaults to `False`)
* `raise_e` (`bool`) - indicates if an exception should be raised when no results are found for a retrieval
using the `get` method (defaults to `True`)
* `rules` (`bool`) - indicates if model definition rules are to be enforced; for example, in case this flag is
`True`, attributes that have the `private` flag set in the model definition will not be retrieved (defaults to `True`)
* `build` (`bool`) - in case this flag is set then before the retrieved results are converted to model
instances, the _build class method for those models will be called before with the basic data structures,
allowing the injection of extra attributes (defaults to `True`)
* `fill` (`bool`) - indicates if the models that are constructed from retrieved model data should be "filled"
with default values associated with each of the model's fields (defaults to `True`)
* `meta` (`bool`) - processes `meta` keywords in the model definition in order to create alternate versions of the
attributes where the values have been mapped to other values; for example, an attribute named `activated` which stored
the boolean values, could be mapped in a such a way that its respective `activated_meta` attribute would show an
"On" or "Off" string, depending on the value set in `activated`) (defaults to `False`)

## Referencing the App

In order to invoke methods that belong to the [App](app.md) object, one can access it through
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
