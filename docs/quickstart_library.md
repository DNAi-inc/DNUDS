# Library API Quick Start Guide

This guide shows you how to use DNUDS as a Python library.

## Installation

```bash
pip install dnuds
```

## Basic Usage

### Simple Sampling

```python
from dnuds import sample_file

result = sample_file(
    input_path="data.csv",
    output_path="sample.csv",
    profile="debug_sample",
    target_rows=1000
)

print(f"Sampled {result.row_count} rows")
print(f"Manifest: {result.manifest_path}")
```

### Advanced Configuration

```python
from dnuds import sample_file, SamplerConfig, PrivacyRule

config = SamplerConfig(
    sampling_mode="stratified",
    target_rows=500,
    key_columns=["status", "country"],
    seed=42,
    privacy_rules=[
        PrivacyRule(column="email", mask_type="hash"),
        PrivacyRule(column="age", mask_type="redact"),
    ]
)

result = sample_file(
    input_path="data.jsonl",
    output_path="sample.jsonl",
    config=config
)
```

## Sampling Modes

### Random Sampling

```python
from dnuds import sample_file, SamplerConfig

config = SamplerConfig(
    sampling_mode="random",
    target_rows=1000,
    seed=42
)

result = sample_file("data.csv", "sample.csv", config=config)
```

### Stratified Sampling

```python
config = SamplerConfig(
    sampling_mode="stratified",
    target_rows=500,
    key_columns=["status", "country"]
)

result = sample_file("data.csv", "sample.csv", config=config)
```

### Time-Aware Sampling

```python
config = SamplerConfig(
    sampling_mode="time_aware",
    target_rows=500,
    key_columns=["timestamp"]  # Column to use for temporal ordering
)

result = sample_file("logs.jsonl", "sample.jsonl", config=config)
```

### Outlier-Aware Sampling

```python
config = SamplerConfig(
    sampling_mode="outlier_aware",
    target_rows=500,
    key_columns=["price", "score"]  # Numeric columns to check
)

result = sample_file("data.csv", "sample.csv", config=config)
```

## Privacy Masking

### Hash Masking

```python
from dnuds import SamplerConfig, PrivacyRule

config = SamplerConfig(
    target_rows=1000,
    privacy_rules=[
        PrivacyRule(column="email", mask_type="hash"),
        PrivacyRule(column="ssn", mask_type="hash", mask_params={"algorithm": "sha256"})
    ]
)
```

### Redaction

```python
config = SamplerConfig(
    target_rows=1000,
    privacy_rules=[
        PrivacyRule(column="name", mask_type="redact"),
        PrivacyRule(column="phone", mask_type="redact", mask_params={"token": "***"})
    ]
)
```

### Truncation

```python
config = SamplerConfig(
    target_rows=1000,
    privacy_rules=[
        PrivacyRule(column="credit_card", mask_type="truncate", mask_params={"max_length": 4})
    ]
)
```

### Bucketing

```python
config = SamplerConfig(
    target_rows=1000,
    privacy_rules=[
        PrivacyRule(column="age", mask_type="bucket", mask_params={"bucket_size": 10})
    ]
)
```

## Format Support

### CSV

```python
result = sample_file("data.csv", "sample.csv", format="csv")
```

### JSONL

```python
result = sample_file("data.jsonl", "sample.jsonl", format="jsonl")
```

### Logs

```python
result = sample_file("access.log", "sample.log", format="log")
```

### SQL

```python
result = sample_file("dump.sql", "sample.sql", format="sql")
```

## Reading Manifests

```python
from dnuds.manifest import read_manifest

manifest = read_manifest("sample.dnuds.json")
print(f"Sampling mode: {manifest['sampling_mode']}")
print(f"Rows sampled: {manifest['actual_rows']}")
print(f"Columns: {manifest['columns']}")
```

## Profiles

### Using Profiles

```python
from dnuds.profiles import create_config_from_profile

# Get profile config
config = create_config_from_profile("debug_sample")

# Override specific settings
config.target_rows = 2000
config.seed = 42

result = sample_file("data.csv", "sample.csv", config=config)
```

### Available Profiles

- `debug_sample`: Random sampling, preserve diversity
- `schema_sample`: Stratified sampling, minimal rows
- `smoke_test_sample`: Deterministic with fixed seed
- `privacy_sample`: Random sampling with privacy rules

## Complete Example

```python
from dnuds import sample_file, SamplerConfig, PrivacyRule

# Configure sampling
config = SamplerConfig(
    sampling_mode="stratified",
    target_rows=1000,
    key_columns=["status", "country"],
    seed=42,
    privacy_rules=[
        PrivacyRule(column="email", mask_type="hash"),
        PrivacyRule(column="phone", mask_type="redact"),
        PrivacyRule(column="age", mask_type="bucket", mask_params={"bucket_size": 10})
    ]
)

# Sample the data
result = sample_file(
    input_path="sensitive_data.csv",
    output_path="safe_sample.csv",
    config=config
)

# Check results
print(f"Sampled {result.row_count} rows")
print(f"Output: {result.output_path}")
print(f"Manifest: {result.manifest_path}")

# Read manifest for details
from dnuds.manifest import read_manifest
manifest = read_manifest(result.manifest_path)
print(f"Sampling mode: {manifest['sampling_mode']}")
print(f"Privacy rules applied: {len(manifest.get('privacy_rules', []))}")
```

