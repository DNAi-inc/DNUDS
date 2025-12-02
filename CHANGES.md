# Changelog

All notable changes to DNUDS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Development Builds

#### Build 0.1.0-dev.17 - 2025-01-01
- Added Apache 2.0 license headers to all Python source files
- Headers include copyright notice, Apache 2.0 license text, and commercial license reference
- All code files now compliant with Apache 2.0 license requirements

#### Build 0.1.0-dev.16 - 2025-01-01
- Updated .gitignore with comprehensive patterns
- Added Ruff cache, test outputs, external test data, and project-specific ignores
- Better organization and coverage of common Python development artifacts

#### Build 0.1.0-dev.13 - 2025-11-30
- Final polish: documentation, examples, linting fixes
- Added comprehensive documentation (CLI guide, library guide, sampling modes, privacy)
- Added example datasets and scripts
- Fixed type hints and linting issues

#### Build 0.1.0-dev.12 - 2025-11-30
- Added comprehensive test suite
- Unit tests for formats, sampling, privacy, profiling, manifest, core API, CLI
- Test data files for CSV, JSONL, logs, SQL

#### Build 0.1.0-dev.11 - 2025-11-30
- Complete CLI implementation
- Support for all command-line options
- Auto-detection of formats
- Configuration file support (JSON/YAML)
- Helpful error messages

#### Build 0.1.0-dev.10 - 2025-11-30
- Manifest generation system
- Automatic .dnuds.json manifest files with metadata
- Column statistics in manifests
- Manifest reading API

#### Build 0.1.0-dev.9 - 2025-11-30
- Log format support (line-based logs with optional parsing)
- SQL dump format support (INSERT statement parsing)
- Streaming parsers for both formats

#### Build 0.1.0-dev.8 - 2025-11-30
- Privacy masking system
- Hash, redact, truncate, and bucket masking types
- Privacy rule configuration
- Privacy-aware sampling profile

#### Build 0.1.0-dev.7 - 2025-11-30
- Profile system implementation
- debug_sample, schema_sample, smoke_test_sample, privacy_sample profiles
- Profile factory and configuration

#### Build 0.1.0-dev.6 - 2025-11-30
- Time-aware sampling (early/middle/late segments)
- Outlier-aware sampling (min/max detection)
- Composite sampler for combining strategies

#### Build 0.1.0-dev.5 - 2025-11-30
- Profiling and statistics collection
- Type inference (string, int, float, bool, datetime)
- Column statistics (min/max, frequencies, null counts)
- Stratified sampling by key columns

#### Build 0.1.0-dev.4 - 2025-11-30
- Core sampling engine
- Random sampling with reservoir algorithm
- SamplerConfig and SampleResult dataclasses
- sample_file() API

#### Build 0.1.0-dev.3 - 2025-11-30
- CSV format reader/writer with auto-detection
- JSONL format reader/writer
- Format detection utilities
- Streaming I/O architecture

#### Build 0.1.0-dev.2 - 2025-11-30
- Project structure and package layout
- pyproject.toml configuration
- Basic CLI stub
- Testing setup (pytest)
- Linting configuration (ruff, mypy)

#### Build 0.1.0-dev.1 - 2025-11-30
- Initial project skeleton
- Project structure and configuration files
- Basic package layout
