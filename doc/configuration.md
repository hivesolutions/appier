# Configuration

Appier configurations are simply a list of settings that are passed from outside the app,
and made accessible to the application logic. They serve both as a single point of
reference to variables that define the app's platform and behavior (eg: database
server, logging level, etc.), and as a means to modify these when running the app in
different environments (eg: having a different configuration for when it's running
in a staging server than from when it's running in a production server).

Configuration can be specified through environment variables, local and/or environment
file, with settings from the former overriding the latter.

Here's a local configuration file (`appier.json` in the application's root folder):

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

The following are reserved configuration variables that modify Appier's behavior:

#### General

| Name             | Type   | Default                 | Description                                                                                                                                                                   |
| ---------------- | ------ | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SERVER**       | `str`  | `legacy`                | The server that will host the app: `legacy`, `netius`, `waitress`, `tornado`, `cherrypi`.                                                                                     |
| **HOST**         | `str`  | `127.0.0.1`             | The address of the server that serves the app (eg: `127.0.0.1` or `0.0.0.0`).                                                                                                 |
| **PORT**         | `int`  | `8080`                  | The port the server will listen at (eg: `8080`).                                                                                                                              |
| **SSL**          | `bool` | `False`                 | Flag indicating if SSL should be enabled.                                                                                                                                     |
| **KEY_FILE**     | `str`  | `None`                  | The path to the SSL key file (mandatory if SSL is enabled).                                                                                                                   |
| **CER_FILE**     | `str`  | `None`                  | The path to the SSL certificate file (mandatory if SSL is enabled).                                                                                                           |
| **BACKLOG**      | `int`  | `socket.SOMAXCONN`      | The number of connections to be hold waiting in server queue while pending accept operation.                                                                                  |
| **FORCE_SSL**    | `bool` | `False`                 | Flag indicating if normal/plain requests (HTTP) should be rewritten to their secure/encrypted counterpart (HTTP).                                                             |
| **FORCE_HOST**   | `str`  | `None`                  | If set and the host value (header) associated with the request does not match its value a rewrite operation in the request will be performed to ensure the host value.        |
| **HTTP_CLIENT**  | `str`  | `netius`                | The client that will be used to perform HTTP requests: `legacy`, `netius`, `requests`.                                                                                        |
| **HTTP_REUSE**   | `bool` | `True`                  | If the HTTP client connections should be re-used under a connection pool approach, or if instead a new connection should be create per request.                               |
| **HTTP_TIMEOUT** | `int`  | `60`                    | The number of seconds the HTTP client is going to wait until the connections is dropped.                                                                                      |
| **BASE_URL**     | `str`  | `http://localhost:8080` | The address to prefix resolved URLs with, in order to turn them from relative to absolute URLs, when so specified (eg: emails links need to point to absolute URLs).          |
| **SECRET**       | `str`  | `None`                  | Secret key/string value to be used for cryptographic operations, should be based on PRNG generated value, if not defined a (properly generated) random value is used instead. |
| **PARTS**        | `list` | `[]`                    | The list of parts definitions (full class path) to be used for the dynamic loading of Appier Parts (eg: `appier_extras.OpbeatPart`).                                          |

#### Database

| Name              | Type   | Default               | Description                                                                                                                                                                                                |
| ----------------- | ------ | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ADAPTER**       | `str`  | `mongo`               | The (database) adapter that is going to be used for data storage (`mongo`, `tiny`, etc).                                                                                                                   |
| **MONGOHQ_URL**   | `str`  | `mongodb://localhost` | URL pointing to a [MongoDB](http://www.mongodb.org/) server, written in the format the [Heroku](https://www.heroku.com/) configuration expects to connect to [MongoHQ](https://bridge.mongohq.com/signup). |
| **MONGOLAB_URI**  | `str`  | `mongodb://localhost` | Same as `MONGOHQ_URL`.                                                                                                                                                                                     |
| **MONGO_URL**     | `str`  | `mongodb://localhost` | Same as `MONGOHQ_URL`.                                                                                                                                                                                     |
| **MONGO_DB**      | `str`  | `None`                | The name of the database to be used as default in case it's not explicitly defined.                                                                                                                        |
| **REDISTOGO_URL** | `str`  | `redis://localhost`   | URL pointing to a [redis](http://redis.io/) server, should conform with the standard/expected URI format.                                                                                                  |
| **REDIS_URL**     | `str`  | `redis://localhost`   | Same as `REDISTOGO_URL`.                                                                                                                                                                                   |
| **REDIS_POOL**    | `bool` | `True`                | If a connection pool should be used for redis communication.                                                                                                                                               |
| **TINY_PATH**     | `str`  | `db.json`             | Path to the file that is going to be used as base for the TinyDB execution (should be JSON based).                                                                                                         |
| **TINY_STORAGE**  | `str`  | `json`                | Storage engine to be used for persistence under TinyDB (`json`, `memory`, etc) (default: `json`).                                                                                                          |
| **SHOW_QUERIES**  | `bool` | `False`               | Displays extra debug information about the queries performed in the database.                                                                                                                              |

#### Email

| Name               | Type   | Description                                                                                                                     |
| ------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------- |
| **SMTP_URL**       | `str`  | Simple URL based value that describes the SMTP configuration (eg: `smtps://username:password@host.com:25`).                     |
| **SMTP_HOST**      | `str`  | The host where an SMTP server is running.                                                                                       |
| **SMTP_PORT**      | `int`  | The port where an SMTP server is listening (default: `25`).                                                                     |
| **SMTP_USER**      | `str`  | The username used to authenticate with the SMTP server.                                                                         |
| **SMTP_PASSWORD**  | `str`  | The password used to authenticate with the SMTP server.                                                                         |
| **SMTP_STARTTLS**  | `bool` | Flag used to tell the server that the client supports Transport Layer Security (default: `True`).                               |
| **SMTP_HELO_HOST** | `str`  | The address of the client connecting to the SMTP server, this will be sent as part of the HELO command send to the SMTP server. |
| **EMAIL_LOCALE**   | `str`  | The default locale to be used while sending emails, this may be overridden explicitly at runtime using the locale attribute.    |

#### Logging

| Name               | Type   | Description                                                                                                                    |
| ------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------ |
| **LEVEL**          | `str`  | Defines the level of verbosity for the loggers: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.                               |
| **FILE_LOG**       | `bool` | Enables rotating file based logging (eg: `/var/log/app_name.log`, `/var/log/app_name.err`).                                    |
| **STREAM_LOG**     | `bool` | Enables the stdout stream based logging (default: `True`) .                                                                    |
| **MEMORY_LOG**     | `bool` | Enables the memory based JSON logging (default: `True`).                                                                       |
| **SYSLOG_HOST**    | `str`  | The hostname of the server running syslog for remote logging, if set also enables the remote syslog handler (default: `None`). |
| **SYSLOG_PORT**    | `int`  | The port of the server running syslog for remote logging (default: `514` or `601`).                                            |
| **SYSLOG_PROTO**   | `str`  | The kind of protocol to be used for the syslog communication (default: `udp`).                                                 |
| **LOGGING**        | `list` | Defines a sequence of logging handlers configuration to be loaded (eg: `complex` example project).                             |
| **LOGGING_EXTRA**  | `bool` | If extra values should be included as part of the logging format so that more debug information is available.                  |
| **LOGGING_FORMAT** | `str`  | If provided overrides the default logging format string for all handlers.                                                      |

#### Cache

| Name           | Type  | Description                                                                                                       |
| -------------- | ----- | ----------------------------------------------------------------------------------------------------------------- |
| **CACHE**      | `str` | Defines the cache manager to be used for general system operations (eg: `file`, `memory`, `redis`).               |
| **CACHE_PATH** | `str` | The path to the directory where the file backed cache engine is going to store the cache files (default: `None`). |

#### Preferences

| Name                 | Type  | Description                                                                                                       |
| -------------------- | ----- | ----------------------------------------------------------------------------------------------------------------- |
| **PREFERENCES**      | `str` | Defines the preferences manager to be used (eg: `file`, `memory`, `redis`).                                       |
| **PREFERENCES_PATH** | `str` | Path to the file that is going to be used by the file preferences engine to store the preferences (using shelve). |

#### Bus

| Name          | Type  | Description                                                                                                                                                                            |
| ------------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **BUS**       | `str` | Defines the bus manager to be used, the bus manager should allow the creation of a federated environment and its orchestration using an event driven approach (eg: `memory`, `redis`). |
| **BUS_NAME**  | `str` | Global name used to create different diffusion scopes for different bus contexts (default: `global`).                                                                                  |
| **BUS_SCOPE** | `str` | Same as `BUS_NAME`.                                                                                                                                                                    |

#### Session

| Name                  | Type  | Description                                                                       |
| --------------------- | ----- | --------------------------------------------------------------------------------- |
| **SESSION**           | `str` | Defines the session manager to be used (eg: `file`, `memory`, `redis`, `client`). |
| **SESSION_FILE_PATH** | `str` | Enables changing of the default directory path for file session storage.          |

#### Scheduler

| Name                  | Type    | Description                                                                      |
| --------------------- | ------- | -------------------------------------------------------------------------------- |
| **SCHEDULER_TIMEOUT** | `float` | Determines the number of seconds between tick operation loops (default: `60.0`). |
| **SCHEDULER_DAEMON**  | `bool`  | Defines if the scheduler thread should be run as a daemon (default: `True`).     |

#### Supervisor

| Name                    | Type    | Description                                                                                                                                                |
| ----------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SUPERVISOR_INTERVAL** | `float` | The number of seconds in between peer checking, this is also going to be used to control the timeout on the peer health check operation (default: `60.0`). |

#### Debug

| Name              | Type   | Description                                                                    |
| ----------------- | ------ | ------------------------------------------------------------------------------ |
| **EXTENDED_PATH** | `bool` | If the file path URL should be set for every traceback line (default: `True`). |
| **EXTENDED_GIT**  | `bool` | If the Git engine should be used for traceback debugging (default: `False`).   |

#### Other/Random

| Name                 | Type   | Description                                                                                                                                                                                                       |
| -------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MANAGER**          | `str`  | The async manager to be used for the scheduling operations (async calls) (default: `queue`).                                                                                                                      |
| **INSTANCE**         | `str`  | The name of the concrete instance to be loaded, this value will affect default database naming, logging and other runtime loaded values (default: `None`).                                                        |
| **PROFILE**          | `str`  | Same as `INSTANCE`.                                                                                                                                                                                               |
| **NAME**             | `str`  | The visual name to be displayed on data associated with the instance, if not provided the default app class name is going to be used instead (default: `None`).                                                   |
| **VERSION**          | `str`  | Version string on a triplet based structure, not recommended to override (default: `None`).                                                                                                                       |
| **DESCRIPTION**      | `str`  | Small sentence with the description for the current application, if not provided the default internal strategy us going to be used to obtain the best possible description for the application (default: `None`). |
| **OBSERVATIONS**     | `str`  | Long sentence to be used as the long description of the application, if not provided the default internal strategy is going to be used to obtain observations for .the application (default: `None`).             |
| **LOGO_URL**         | `str`  | The URL of the main logo for the application (default: `None`).                                                                                                                                                   |
| **LOGO_SQUARE_URL**  | `str`  | The URL of the square version of the logo for the application (default: `None`).                                                                                                                                  |
| **LOGO_RASTER_URL**  | `str`  | If provided ensures an alternative to `LOGO_URL` with a raster image (eg: `PNG`, `JPEG`, etc.) to be used in contexts where a vector image is not suitable .(default: `None`).                                    |
| **FAVICON_URL**      | `str`  | The URL of the preferred `favicon` to be used by the application (default: `None`).                                                                                                                               |
| **COPYRIGHT**        | `str`  | Name of the company to which the copy rights of the application should be attributed (default: `Hive Solutions`).                                                                                                 |
| **COPYRIGHT_YEAR**   | `str`  | The year or range of year to be used in the copyright labels (default: `2008-2021`).                                                                                                                              |
| **COPYRIGHT_URL**    | `str`  | The target URL for the copyright label (default: `http://hive.pt`).                                                                                                                                               |
| **LOCALE**           | `str`  | The default locale value to be used for  language, region and any special variant preferences.                                                                                                                    |
| **APPIER_BASE_PATH** | `str`  | Override the default base path for the app (calculated as a relative directory to the main app file) (default: `None`).                                                                                           |
| **HIGHLIGHTER**      | `str`  | The name of the syntax highlighting library to be used in the main set of Appier pages, including the default HTML error page (eg: `prism`, `highlight.js`) (default: `prism`).                                   |
| **PIP_USER**         | `bool` | If the appier controller `pip_install` operation should be done at an user level.                                                                                                                                 |
