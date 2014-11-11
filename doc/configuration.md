# Configuration

Appier configurations are simply a list of settings that are passed from outside the app,
and then made accessible to the application logic. They serve both as a single point of 
reference to variables that define the app's platform and behavior (eg: database
server, logging level, etc.), and as a means to modify these when running the app in
different environments (eg: having a different configuration for when it's running
in a staging server than from when it's running in a production server).

Configuration can be specified through environment variables, local file and/or environment 
file, with settings from the former overriding the latter.

Here's an example of the app's logger being configured through the local configuration file,
named ``appier.json`` and set in the application's root folder:

```json
{
    "LEVEL" : "INFO"
}
```

That setting could also be configured through environment variables, which would override
the very same setting defined in the local configuration file:

```bash
LEVEL=WARNING python hello.py
```

To retrieve configuration values from anywhere in the app do:

```json
level = appier.conf("LEVEL")
```

You can also provide a default, so the app still works when that setting is missing:

```json
level = appier.conf("LEVEL", "INFO")
```

## Reference

Appier has many reserved configuration variables that modify its internal behavior
as well: 

* `SERVER` (`str`) - The server that will host the app (eg: `netius`, ``Waitress``, ``Tornado``, ``CherryPi``).
* `PORT` (`int`) - The port the server will listen at (eg: 8080).
* `LEVEL` (`str`) - Defines the level of verbodity for the loggers (eg: `DEBUG`).
* `FILE_LOG` (`bool`) - Enables the rotating file based logging (eg: `/var/log/name.log`, 
`/var/log/name.err`).
* `LOGGING` (`list`) - Defines a sequence of logging handlers configuration to be loaded 
(eg: 'complex' example project).
* `SMTP_HOST` (`str`) - The host where an SMTP server is running.
* `SMTP_PORT` (`int`) - The port where an SMTP server is listening (default: 25).
* `SMTP_USER` (`str`) - The username used to authenticate with the SMTP server.
* `SMTP_PASSWORD` (`str`) - The password used to authenticate with the SMTP server.
* `SMTP_STARTTLS` (`bool`) - Flag used to tell the server that the client supports Transport 
Layer Security (default: True).
