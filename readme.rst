`Appier <http://appier.hive.pt>`__
==================================

Joyful Python Web App development

Appier is an object-oriented Python web framework built for super fast app development.
It's as lightweight as possible, but not too lightweight.
It gives you the power of bigger frameworks, without their complexity.

Installation
------------

    pip install appier

Usage
-----

.. code:: python

    import appier

    class HelloApp(appier.App):

        @appier.route("/", "GET")
        def hello(self):
            return "Hello World"

    HelloApp().serve()

More
----

For more information consult the `website <http://appier.hive.pt>`__.
