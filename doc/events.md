# Events

With Appier, you can send events across application models. This is a way to allow
models to communicate with each other without creating a strict dependency between
them.

Here's an example of the event of a `Cat` having "mehowed" being broadcast to the
whole app:

```python
class Cat(appier.Model):

    name = appier.field()

    def meow(self):
        print("Meoooow!")
        self.trigger("cat_meowed")
```

This event can be listened to, and acted upon, in a different model:

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

It's true that `Cat` could just import `MeowTracker` and invoke it
on its `meow` method, however, that would be a conceptual violation
that would intertwine the logic in a such a way that would most probably
cause problems down the road (it's natural for a cat tracker to be aware
that cats exist, but not so natural for cats to be aware of trackers).

## Persistence events

When entities are being saved, Appier issues events for each phase
of their persistence workflow (see [Models](models.md) for more
details about model persistence). These can be listened to in the
same way:

```python
@classmethod
def setup(cls):
    super(MeowTracker, cls).setup()
    cat.Cat.bind_g("post_create", cls.handle_post_create)

@classmethod
def handle_cat_post_create(cls, ctx):
    print("Cat '%s' was born" % ctx.name)
```

The following is a list of the persistence workflow events that
can be listened to:

* `pre_validate` - the entity is going to be validated
* `pre_save` - it's going to be saved
* `pre_create` - it's going to be created
* `pre_update` - it's going to be updated
* `pre_delete` - it's going to be deleted
* `post_validate` - it was validated
* `post_save` - it was saved
* `post_create` - it was created
* `post_update` - it was updated
* `post_delete` - it was deleted
* `pre_apply` - request data is about to be applied
* `post_apply` - request data was applied
