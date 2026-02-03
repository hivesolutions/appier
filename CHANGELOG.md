# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

*

### Changed

* Ensures result in ASGI response is a sequence

### Fixed

* String conversion in ASGI response

## [1.35.0] - 2026-01-06

### Added

* Support for `conf_override` context manager in config module for temporarily overriding configuration values

### Changed

* Documented `GeoResolver` class

## [1.34.12] - 2025-09-16

### Added

* Support for the `custom` validation

## [1.34.11] - 2025-09-15

### Added

* Support for the callable filter

## [1.34.10] - 2025-09-13

### Added

* ValidationRules as a new type for the sequence of validation rules

## [1.34.9] - 2025-09-12

### Added

* Support for continuous paging for non "pageable" models

## [1.34.8] - 2025-08-27

### Added

* Support for PyMongo DEBUG mode disable

## [1.34.7] - 2025-08-18

### Changed

* Made `error_handler` and `exception_handler` behave according to the `json` flag so that by default they handle both Web and JSON requests

## [1.34.6] - 2025-02-18

### Added

* Support for the `X-Error-Id` header for tracing purposes
* Support for relative param in redirect, forcing relative redirects

## [1.34.5] - 2024-09-25

### Added

* Support for the `ident()` method in `Model`
* New types for the `model.py` file

## [1.34.4] - 2024-08-29

### Added

* The `version` field to the `info_dict`

## [1.34.3] - 2024-06-03

### Added

* Support for identification and description of Cron Tasks

## [1.34.2] - 2024-06-02

### Fixed

* Double start execution for ASGI applications

## [1.34.1] - 2024-06-02

### Changed

* Improved string representation of `SchedulerTask`

## [1.34.0] - 2024-05-31

### Added

* Support for `save()` and `open()` methods in `File` class

## [1.33.5] - 2024-05-28

### Added

* Support for `LimitedSizeDict` data structure

## [1.33.4] - 2024-05-04

### Fixed

* Comparison support for `SchedulerTask`

## [1.33.3] - 2024-05-01

### Added

* Support for loading of `.env` files in for config

## [1.33.2] - 2024-04-21

### Changed

* Support for direct `html` and `plain` contents sending in `email()`

## [1.33.1] - 2024-01-17

### Fixed

* Small type related fixes

## [1.33.0] - 2024-01-17

### Added

* Support for Cron based scheduling using `SchedulerCron` class - [#65](https://github.com/hivesolutions/appier/issues/65)

### Fixed

* Problems with raw strings and regular expressions, invalid escape sequences - [#63](https://github.com/hivesolutions/appier/issues/63)

## [1.32.0] - 2024-01-17

### Added

* Support for the `reply_to` argument to control the "Reply-To" MIME header
* Support for `return_path` and `priority` email values

## [1.31.5] - 2024-01-04

### Changed

* Changed codebase to be compliant with Black code formatter

### Fixed

* Issue with Pillow and the ANTIALIAS resampling constant

## [1.31.4] - 2023-10-15

### Fixed

* Long term issue with sessions with static value

## [1.31.3] - 2023-10-15

### Fixed

* Python 3.12 support

## [1.31.2] - 2023-06-29

### Fixed

* Issue related to wrong regex option in MongoDB

## [1.31.1] - 2023-05-31

### Fixed

* Issue related to immutable tuple and the `append()` method

## [1.31.0] - 2023-05-30

### Added

* Support for fallback sorting order
* Support for multiple sort elements

## [1.30.1] - 2023-02-08

### Fixed

* Issue with forward headers for the `uvicorn` server, forced wildcard IP validation
* Remove custom event handler method issue with the priority field, which caused an item not found error in `list.remove`

## [1.30.0] - 2022-08-17

### Added

* Improved the `holder.html.tpl` page with more content

### Changed

* Improved the `merge_dict()` operation with the support for callback

## [1.29.1] - 2022-06-25

### Added

* Support for setting prefix in `url_for` avoiding the usage of the request

## [1.29.0] - 2022-06-10

### Added

* Support for `basic_auth()` method that generates a basic authorization string

## [1.28.0] - 2022-05-17

### Added

* Support for the `LOGIN_CONTEXT` configuration value that forces the context used in login redirection

## [1.27.3] - 2022-05-02

### Added

* Support for callable sending of data, allows lazy data retrieval, relevant for ETag validation

## [1.27.2] - 2022-05-01

### Fixed

* Issue related to invalid cache-control policy set for 304 Not Modified requests

## [1.27.1] - 2022-03-09

### Fixed

* Support for Jinja2 > 3.1.x

## [1.27.0] - 2022-03-09

### Added

* Support for find operations in count

### Fixed

* Graph's Dijkstra in case of no available path
* Converts the filters passed before executing the `count` operation

## [1.26.0] - 2022-02-23

### Added

* `Graph` module and dijkstra priority queue implementation

## [1.25.2] - 2021-12-18

### Fixed

* Support for `count_documents` in `PyMongo>=4`

## [1.25.1] - 2021-12-01

### Fixed

* Fix pymongo version parsing for versions without the patch number

## [1.25.0] - 2021-11-08

### Added

* Support for `ValueError` handling in casting `field()` values

## [1.24.0] - 2021-07-07

### Added

* Support for multiple character escaping in `appier.escape`

## [1.23.0] - 2021-07-07

### Added

* Support for `dict` as casting strategy

## [1.22.2] - 2021-06-28

### Fixed

* Error related with unpacking of error handler parameters

## [1.22.1] - 2021-06-28

### Fixed

* `OPTIONS` route issue with non existing priority field

## [1.22.0] - 2021-06-28

### Added

* Support for `priority` field in routes, errors and custom handlers, allows explicit control of handler resolution
