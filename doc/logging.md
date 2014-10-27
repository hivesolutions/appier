# Logging

To log info messages from within an app, model or controller object:

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
(to learn how to change app configurations read [Configuration](configuration.md)). If the
app is run with a logging level of ``ERROR`` and the following lines are executed:

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

The file path to where the log is written can be specified using ``FILE_LOG`` configuration variable:

```python
FILE_LOG=/var/log/hello_world.log python hello_world.py
```
