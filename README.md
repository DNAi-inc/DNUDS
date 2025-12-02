# DNUDS - DNAi Universal Data Sampler

DNUDS is a Python library and CLI tool for creating representative samples from large data files. It supports multiple input formats (CSV, JSONL, logs, SQL dumps) and provides various sampling strategies to ensure diversity and coverage in your samples.

## Features

- **Multiple Format Support**: CSV, JSONL, line-based logs, and SQL dumps
- **Streaming Architecture**: Processes files without loading them entirely into memory
- **Multiple Sampling Modes**: Random, stratified, time-aware, and outlier-aware sampling
- **Profiles**: Pre-configured sampling strategies (debug_sample, schema_sample, smoke_test_sample, privacy_sample)
- **Privacy Features**: Built-in masking for sensitive data (hash, redact, truncate, bucket)
- **Reproducibility**: Fixed random seeds ensure identical outputs across runs
- **Manifests**: Automatic generation of metadata files documenting sampling runs

## Installation

```bash
pip install dnuds
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

### CLI Usage

```bash
# Basic sampling
dnuds sample input.csv output.csv

# With options
dnuds sample input.jsonl output.jsonl --format jsonl --profile debug_sample --rows 2000

# Stratified sampling
dnuds sample access.log sample.log --format log --profile debug_sample --rows 500 --key-col status --key-col service

# With seed for reproducibility
dnuds sample dump.sql sample.csv --format sql --profile schema_sample --table users --rows 1000 --seed 42
```

### Library Usage

```python
from dnuds import sample_file, SamplerConfig

# Simple sampling
result = sample_file(
    input_path="data.csv",
    output_path="sample.csv",
    profile="debug_sample",
    target_rows=1000
)

print(f"Sampled {result.row_count} rows")
print(f"Manifest: {result.manifest_path}")

# Advanced configuration
config = SamplerConfig(
    sampling_mode="stratified",
    target_rows=500,
    key_columns=["status", "country"],
    seed=42
)

result = sample_file(
    input_path="data.jsonl",
    output_path="sample.jsonl",
    config=config
)
```

## Sampling Modes

- **Random**: Uniform random sampling using reservoir sampling
- **Stratified**: Ensures representation across key columns/categories
- **Time-aware**: Guarantees coverage from early, middle, and late segments
- **Outlier-aware**: Includes rows with min/max values in numeric columns

## Profiles

- **debug_sample**: Small samples preserving diversity and rare values
- **schema_sample**: Minimal rows covering distinct shapes and categories
- **smoke_test_sample**: Deterministic samples for automated testing
- **privacy_sample**: Applies masking rules to sensitive columns

## Documentation

See the `docs/` directory for detailed documentation:
- [CLI Quick Start](docs/quickstart_cli.md)
- [Library API Guide](docs/quickstart_library.md)
- [Sampling Modes](docs/sampling_modes.md)
- [Privacy Configuration](docs/privacy.md)

## License

This project is dual-licensed.

• Free for personal, academic, and educational use under the
  DNAi Free License v1.1. See LICENSE.

• Commercial, business, or production use requires purchasing a
  DNAi Commercial License v1.1. See LICENSE-COMMERCIAL.

Commercial customers must follow the DNAi Commercial License v1.1,
which overrides the DNAi Free License v1.1 for all commercial usage.

## Contributing

Contributions are welcome! Please ensure all code includes type hints and follows the existing code style. See CONTRIBUTING.md for more details.


