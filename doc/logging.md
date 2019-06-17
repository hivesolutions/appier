# Logging

To log info messages from within an [App](app.md), [Model](model.md) or [Controller](controller.md) object:

```python
self.logger.info("information message")
```

To log warning messages:

```python
self.logger.warn("warning message")
```

To log error messages:

```python
self.logger.error("error message")
```

To log critical messages:

```python
self.logger.critical("critical message")
```

You can configure the logging level so that only messages at and above that level are logged
(to learn more read the [Configuration](configuration.md) guide):

```python
LEVEL=ERROR python hello.py
```

If the app is run with a logging level of `ERROR` and the following lines are executed:

```python
self.logger.info("info message")
self.logger.warn("warning message")
self.logger.error("error message")
self.logger.critical("critical message")
```

The output would be the following:

```bash
error message
critical message
```

It's possible to write the log to file using the `FILE_LOG` configuration variable:

```python
FILE_LOG=1 python hello.py
```
