# Advanced Topics

This page presents advanced information in a not so structured manner. It is used as both a reference
for external and internal developers, and therefore rewards flexibility over structure.

## Configuration

Appier can be configured through environment variables. The following would configure the logger to print only messages whose level is Critical or above:

```bash
LEVEL=CRITICAL python hello_world.py
```

The following are all the configuration variables:

* `LEVEL` `str` - Defines the level of verbodity for the loggers (eg: `DEBUG`)
* `FILE_LOG` `bool` - Enables the rotating file based logging (eg: `/var/log/name.log`, `/var/log/name.err`)
* `LOGGING` `list` - Defines a sequence of logging handlers configuration to be loaded (eg: 'complex' example project)

The configuration can also be provided by creating an "appier.json" file:

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

## Internationalization i18n

Appier supports both the localization thought template output using the `locale` filter
and the localization using multiple template files `x.LOCALE.xxx`.

The framework also sets the global operative system level locale value and so the operative
system must be ready to handle this changes.

Under Unix it's important to generate the appropriate locales for proper usage, otherwise
this global setting would fail to be set.

```bash
less /usr/share/i18n/SUPPORTED
sudo locale-gen pt_PT
sudo locale-gen pt_PT.utf8
```
