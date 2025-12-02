# CLI Quick Start Guide

This guide shows you how to use DNUDS from the command line.

## Installation

```bash
pip install dnuds
```

## Basic Usage

### Simple Sampling

Sample 1000 rows from a CSV file:

```bash
dnuds sample input.csv output.csv
```

### Specify Target Rows

```bash
dnuds sample input.csv output.csv --rows 500
```

### Use a Profile

```bash
dnuds sample input.jsonl output.jsonl --profile schema_sample --rows 100
```

Available profiles:
- `debug_sample`: Small samples preserving diversity (default)
- `schema_sample`: Minimal rows covering distinct categories
- `smoke_test_sample`: Deterministic samples for testing
- `privacy_sample`: Samples with privacy masking

### Stratified Sampling

Ensure representation across key columns:

```bash
dnuds sample data.csv sample.csv --key-col status --key-col country
```

### Reproducible Sampling

Use a fixed seed for identical outputs:

```bash
dnuds sample data.csv sample.csv --seed 42
```

### Format Auto-Detection

DNUDS automatically detects format from file extension:

```bash
dnuds sample data.csv output.csv    # CSV
dnuds sample data.jsonl output.jsonl  # JSONL
dnuds sample access.log output.log    # Log
dnuds sample dump.sql output.sql       # SQL
```

### Explicit Format

Specify format explicitly:

```bash
dnuds sample data.txt output.csv --format csv
```

### SQL Table Filtering

For SQL dumps, filter by table name:

```bash
dnuds sample dump.sql output.csv --format sql --table users
```

## Configuration Files

Create a JSON or YAML configuration file:

**config.json:**
```json
{
  "sampling_mode": "stratified",
  "target_rows": 500,
  "key_columns": ["status", "country"],
  "seed": 42,
  "privacy_rules": [
    {
      "column": "email",
      "mask_type": "hash"
    },
    {
      "column": "age",
      "mask_type": "redact",
      "mask_params": {
        "token": "***"
      }
    }
  ]
}
```

Use the configuration:

```bash
dnuds sample input.csv output.csv --config config.json
```

## Examples

### Example 1: Debug Sample

```bash
dnuds sample large_dataset.csv debug_sample.csv --profile debug_sample --rows 1000
```

### Example 2: Schema Inference

```bash
dnuds sample data.jsonl schema_sample.jsonl --profile schema_sample --rows 50
```

### Example 3: Privacy-Aware Sampling

```bash
dnuds sample sensitive_data.csv safe_sample.csv \
  --profile privacy_sample \
  --config privacy_config.json
```

### Example 4: Time-Aware Sampling

```bash
dnuds sample logs.txt sample.txt \
  --format log \
  --sampling-mode time_aware \
  --key-col timestamp \
  --rows 500
```

## Output

DNUDS creates two files:

1. **Output file**: The sampled data (e.g., `output.csv`)
2. **Manifest file**: Metadata about the sampling run (e.g., `output.dnuds.json`)

The manifest includes:
- DNUDS version
- Timestamp
- Input/output paths
- Sampling configuration
- Column statistics
- Privacy rules applied

## Error Handling

DNUDS provides helpful error messages:

```bash
# File not found
dnuds sample missing.csv output.csv
# Error: Input file not found: missing.csv

# Invalid format
dnuds sample data.txt output.csv --format invalid
# Error: Unknown format: invalid
# Supported formats: csv, jsonl, log, sql
```

## Exit Codes

- `0`: Success
- `1`: Error (file not found, invalid config, etc.)
- `130`: Interrupted by user (Ctrl+C)

