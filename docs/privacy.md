# Privacy Configuration Guide

DNUDS provides built-in privacy masking to protect sensitive data in samples.

## Mask Types

### Hash Masking

Replaces values with cryptographic hashes (SHA256 by default).

```python
PrivacyRule(column="email", mask_type="hash")
PrivacyRule(column="ssn", mask_type="hash", mask_params={"algorithm": "sha256"})
```

**Use Cases**: When you need consistent pseudonymization (same input → same hash)

### Redaction

Replaces values with a constant token.

```python
PrivacyRule(column="name", mask_type="redact")
PrivacyRule(column="phone", mask_type="redact", mask_params={"token": "***"})
```

**Use Cases**: When you just need to hide values completely

### Truncation

Keeps only the first N characters.

```python
PrivacyRule(column="credit_card", mask_type="truncate", mask_params={"max_length": 4})
```

**Use Cases**: When you need partial information (e.g., last 4 digits)

### Bucketing

Replaces numeric values with range labels.

```python
PrivacyRule(column="age", mask_type="bucket", mask_params={"bucket_size": 10})
# 25 → "20-29", 35 → "30-39"
```

**Use Cases**: When you need approximate values for analysis

## Configuration

### Python API

```python
from dnuds import SamplerConfig, PrivacyRule

config = SamplerConfig(
    target_rows=1000,
    privacy_rules=[
        PrivacyRule(column="email", mask_type="hash"),
        PrivacyRule(column="phone", mask_type="redact"),
        PrivacyRule(column="age", mask_type="bucket", mask_params={"bucket_size": 10}),
        PrivacyRule(column="credit_card", mask_type="truncate", mask_params={"max_length": 4}),
    ]
)
```

### JSON Configuration

```json
{
  "target_rows": 1000,
  "privacy_rules": [
    {
      "column": "email",
      "mask_type": "hash",
      "mask_params": {
        "algorithm": "sha256"
      }
    },
    {
      "column": "phone",
      "mask_type": "redact",
      "mask_params": {
        "token": "***"
      }
    },
    {
      "column": "age",
      "mask_type": "bucket",
      "mask_params": {
        "bucket_size": 10
      }
    }
  ]
}
```

### YAML Configuration

```yaml
target_rows: 1000
privacy_rules:
  - column: email
    mask_type: hash
    mask_params:
      algorithm: sha256
  - column: phone
    mask_type: redact
    mask_params:
      token: "***"
  - column: age
    mask_type: bucket
    mask_params:
      bucket_size: 10
```

## Column Tagging

You can tag columns for automatic privacy rules:

```python
# Future feature: column tagging
# tags = {
#     "id": "id",
#     "email": "quasi_id",
#     "name": "quasi_id",
#     "age": "safe"
# }
```

## Best Practices

1. **Hash for Pseudonymization**: Use hash masking when you need consistent pseudonymization across multiple samples
2. **Redact for Complete Hiding**: Use redaction when values should be completely hidden
3. **Truncate for Partial Info**: Use truncation when you need partial information (e.g., last 4 digits)
4. **Bucket for Aggregation**: Use bucketing for numeric values when exact values aren't needed

## Example: Complete Privacy Setup

```python
from dnuds import sample_file, SamplerConfig, PrivacyRule

# Define privacy rules
privacy_rules = [
    # PII: Hash for pseudonymization
    PrivacyRule(column="email", mask_type="hash"),
    PrivacyRule(column="ssn", mask_type="hash"),
    
    # Sensitive: Redact completely
    PrivacyRule(column="credit_card", mask_type="redact"),
    
    # Quasi-identifiers: Bucket
    PrivacyRule(column="age", mask_type="bucket", mask_params={"bucket_size": 10}),
    PrivacyRule(column="zipcode", mask_type="bucket", mask_params={"bucket_size": 1000}),
    
    # Partial info: Truncate
    PrivacyRule(column="phone", mask_type="truncate", mask_params={"max_length": 4}),
]

# Configure sampling
config = SamplerConfig(
    sampling_mode="random",
    target_rows=1000,
    privacy_rules=privacy_rules,
    seed=42
)

# Sample with privacy
result = sample_file(
    input_path="sensitive_data.csv",
    output_path="safe_sample.csv",
    config=config
)

print(f"Sampled {result.row_count} rows with privacy masking")
```

## Verification

After sampling, verify that masked columns don't contain raw values:

```python
import csv

with open("safe_sample.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Email should be hashed (64 char hex string)
        assert len(row["email"]) == 64
        assert row["email"].isalnum()
        
        # Credit card should be redacted
        assert row["credit_card"] == "[REDACTED]"
        
        # Age should be bucketed
        assert "-" in row["age"]  # Format: "20-29"
```

## Limitations

- DNUDS does not implement full k-anonymity
- Hash masking is one-way (cannot recover original values)
- Bucketing may reduce data utility for analysis
- Consider additional privacy measures for highly sensitive data

