# Sampling Modes

DNUDS supports multiple sampling modes, each designed for different use cases.

## Random Sampling

**Mode**: `random`

Uniform random sampling using reservoir sampling algorithm. Each row has equal probability of being selected.

### Use Cases
- General-purpose sampling
- When you need a representative random sample
- Debugging and exploration

### Example

```python
config = SamplerConfig(
    sampling_mode="random",
    target_rows=1000,
    seed=42  # Optional: for reproducibility
)
```

### Characteristics
- Single-pass algorithm (memory efficient)
- Uniform distribution
- Reproducible with fixed seed

## Stratified Sampling

**Mode**: `stratified`

Ensures representation across key columns/categories. Maintains minimum rows per category while respecting total target size.

### Use Cases
- When you need representation from all categories
- Schema inference
- Testing with diverse data

### Example

```python
config = SamplerConfig(
    sampling_mode="stratified",
    target_rows=500,
    key_columns=["status", "country"]  # Columns to stratify by
)
```

### Characteristics
- Guarantees minimum representation per category
- Balances categories proportionally
- Requires key columns to be specified

## Time-Aware Sampling

**Mode**: `time_aware`

Guarantees coverage from early, middle, and late segments of the data. Uses a timestamp column or line position.

### Use Cases
- Time-series data
- Log files
- Data with temporal patterns

### Example

```python
config = SamplerConfig(
    sampling_mode="time_aware",
    target_rows=500,
    key_columns=["timestamp"]  # Column for temporal ordering
)
```

### Characteristics
- Divides data into three segments (early, middle, late)
- Samples from each segment
- Ensures temporal coverage

## Outlier-Aware Sampling

**Mode**: `outlier_aware`

Ensures rows with min/max values in numeric columns are included in the sample.

### Use Cases
- When edge cases are important
- Data validation
- Anomaly detection

### Example

```python
config = SamplerConfig(
    sampling_mode="outlier_aware",
    target_rows=500,
    key_columns=["price", "score"]  # Numeric columns to check
)
```

### Characteristics
- Automatically detects min/max values
- Guarantees inclusion of extreme values
- Fills remaining slots randomly

## Composite Sampling

**Mode**: `composite`

Combines multiple sampling strategies in sequence.

### Use Cases
- Complex sampling requirements
- Combining outlier detection with time awareness

### Example

```python
config = SamplerConfig(
    sampling_mode="composite",
    target_rows=500
)
```

### Characteristics
- Applies multiple strategies sequentially
- More flexible but potentially slower
- Good for complex requirements

## Choosing a Mode

| Mode | Best For | Key Requirement |
|------|----------|-----------------|
| `random` | General use, debugging | None |
| `stratified` | Category representation | Key columns |
| `time_aware` | Temporal data, logs | Time column |
| `outlier_aware` | Edge cases, validation | Numeric columns |
| `composite` | Complex requirements | None |

## Performance Considerations

- **Random**: Fastest, single pass
- **Stratified**: Requires collecting all rows first (two passes)
- **Time-aware**: Requires sorting (two passes)
- **Outlier-aware**: Requires finding min/max (two passes)
- **Composite**: Depends on component strategies

For very large files, consider using `random` mode for best performance.

