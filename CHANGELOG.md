# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## Unreleased
### Added
### Changed
### Fixed
### Removed

## [0.3.0] - 2016-11-08
### Fixed
- hashin 0.7.0 broke backwards compatibility; dephash 0.3.0 fixes that and requires `hashin>=0.7.1`
## [0.2.0] - 2016-07-04
### Changed
- Rename to `dephash` since there is already a `reqhash` in pypi
- Moved `dephash` functionality to `dephash gen`

### Added
- Added `dephash outdated` to check for outdated files

## [0.1.0] - 2016-07-04
### Changed
- Use `click` for commandline options
- Use `hashin` for package hashing
- Use `logging` for log output
