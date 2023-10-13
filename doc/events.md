# Events

With Appier, you can send events across application models. This allows models to
communicate with each other without creating a strict dependency between them.

Here's an example of the event of a `Cat` having "mehowed" being broadcast to the
whole app:

```python
class Cat(appier.Model):

    name = appier.field()

    def meow(self):
        print("Meoooow!")
        self.trigger("cat_meowed")
```

This event can be listened to and acted upon in a different model:

```python
import cat

class MeowTracker(appier.Model):

    @classmethod
    def setup(cls):
        super(MeowTracker, cls).setup()
        cat.Cat.bind_g("cat_meowed", cls.handle_cat_mehowed)

    @classmethod
    def handle_cat_mehowed(cls, ctx):
        print("Cat '%s' mehowed" % ctx.name)
```

The previous example defines a global listener, which means that
all `cat_meowed` events will be handled by the `MeowTracker` model.
However, if you wanted the event to be listened to only by a particular
instance of the model, then you should use the `bind` method instead:

```python
class MeowTracker(appier.Model):

    def listen(self):
        self.bind("cat_meowed", self.handle_cat_mehowed)

    def handle_cat_mehowed(self, ctx):
        print("Cat '%s' mehowed" % ctx.name)
```

It's true that `Cat` could just import `MeowTracker` and invoke it
directly in its `meow` method, however, that would be a conceptual violation
that would intertwine the logic in such a way that would cause problems down
the road (it makes more sense than a meow tracker, whatever that is, to be aware
that cats exist, then for cats to be aware of meow trackers).

Events are dispatched and handled synchronously, therefore after the `trigger`
method returns, you can rest assured that all listeners have already processed
the event and their associated behaviors.

## Persistence events

When model instances are being saved, Appier issues events for each phase
of their persistence workflow (see [Models](models.md) for more details
about model persistence). These can be listened to in the same way:

```python
@classmethod
def setup(cls):
    super(MeowTracker, cls).setup()
    cat.Cat.bind_g("post_create", cls.handle_post_create)

@classmethod
def handle_cat_post_create(cls, ctx):
    print("Cat '%s' was born" % ctx.name)
```

These are the built-in persistence workflow events:

* `pre_validate` - the entity is going to be validated
* `pre_save` - it's going to be saved (invoked both on create and update)
* `pre_create` - it's going to be created
* `pre_update` - it's going to be updated
* `pre_delete` - it's going to be deleted
* `post_validate` - it was validated
* `post_save` - it was saved (invoked both on create and update)
* `post_create` - it was created
* `post_update` - it was updated
* `post_delete` - it was deleted
* `pre_apply` - request data is about to be applied
* `post_apply` - request data was applied
