# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

* Support for the `LOGIN_CONTEXT` configuration value that forces the context used in login redirection

### Changed

*

### Fixed

*

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
