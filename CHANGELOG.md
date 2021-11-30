# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

*

### Changed

*

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
