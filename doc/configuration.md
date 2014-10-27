# Configuration

Appier can be configured through environment variables. The following would configure the logger to print only messages whose level is "critical" or above:

```bash
LEVEL=INFO python hello_world.py
```

The following are all the available configuration variables:

* `LEVEL` (`str`) - Defines the level of verbodity for the loggers (eg: `DEBUG`)
* `FILE_LOG` (`bool`) - Enables the rotating file based logging (eg: `/var/log/name.log`, `/var/log/name.err`)
* `LOGGING` (`list`) - Defines a sequence of logging handlers configuration to be loaded (eg: 'complex' example project)
* `SERVER` (`str`) - The server that will host the app (eg: `netius`)

The configuration can also be provided by creating an `appier.json` in the root of your project directory:

```json
{
    "LEVEL" : "WARNING"
}
```

You can also create a configuration file in your home directory, also named `appier.json`:

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
