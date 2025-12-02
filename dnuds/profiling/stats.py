# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Statistics collection for columns."""

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from dnuds.profiling.type_inference import TypeGuess, infer_column_type


@dataclass
class ColumnStats:
    """Statistics for a single column."""

    column_name: str
    type_guess: TypeGuess = TypeGuess.UNKNOWN
    null_count: int = 0
    total_count: int = 0
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    top_values: Dict[Any, int] = field(default_factory=dict)
    unique_count: int = 0

    def update(self, value: Any) -> None:
        """
        Update statistics with a new value.

        Args:
            value: Value to incorporate into statistics
        """
        self.total_count += 1

        if value is None:
            self.null_count += 1
            return

        # Update min/max for numeric values based on the value itself.
        # We do not rely on the current type_guess here because it is inferred
        # after collecting samples.
        if isinstance(value, (int, float)):
            if self.min_value is None or value < self.min_value:
                self.min_value = value
            if self.max_value is None or value > self.max_value:
                self.max_value = value

        # Track unique values (for frequency counting)
        if value not in self.top_values:
            self.unique_count += 1
        self.top_values[value] = self.top_values.get(value, 0) + 1


def collect_stats(
    rows: Iterator[Dict[str, Any]],
    columns: List[str],
    max_top_values: int = 50,
    sample_size: Optional[int] = None,
) -> Dict[str, ColumnStats]:
    """
    Collect statistics for columns from a stream of rows.

    Args:
        rows: Iterator of row dictionaries
        columns: List of column names to collect stats for
        max_top_values: Maximum number of top values to track per column
        sample_size: Maximum number of rows to process (None for all)

    Returns:
        Dictionary mapping column names to ColumnStats objects
    """
    # Initialize stats objects
    stats: Dict[str, ColumnStats] = {
        col: ColumnStats(column_name=col) for col in columns
    }

    # Collect values for type inference (first pass)
    value_samples: Dict[str, List[Any]] = {col: [] for col in columns}
    row_count = 0

    for row in rows:
        if sample_size and row_count >= sample_size:
            break

        for col in columns:
            value = row.get(col)
            value_samples[col].append(value)
            stats[col].update(value)

        row_count += 1

    # Infer types from samples
    for col in columns:
        if value_samples[col]:
            stats[col].type_guess = infer_column_type(value_samples[col])

    # Trim top values to max_top_values
    for col_stats in stats.values():
        if len(col_stats.top_values) > max_top_values:
            # Keep only top N most frequent values
            counter = Counter(col_stats.top_values)
            col_stats.top_values = dict(counter.most_common(max_top_values))

    return stats

