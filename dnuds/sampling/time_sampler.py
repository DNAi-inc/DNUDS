# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Time-aware sampling that ensures coverage from early, middle, and late segments."""

import random
from typing import Any, Dict, Iterator, List, Optional

from dnuds.profiling.type_inference import TypeGuess, infer_type
from dnuds.sampling.base import Sampler


class TimeSampler(Sampler):
    """
    Time-aware sampler that guarantees coverage from start, middle, and end segments.

    Can use a timestamp column or line position to determine temporal ordering.
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize time-aware sampler.

        Args:
            config: Sampling configuration
        """
        super().__init__(config)
        # Initialize random number generator
        if config.seed is not None:
            self.rng = random.Random(config.seed)
        else:
            self.rng = random.Random()

        # Time column (if None, uses line position)
        self.time_column: Optional[str] = config.key_columns[0] if config.key_columns else None

    def _get_timestamp_value(self, row: Dict[str, Any], row_index: int) -> float:
        """
        Get timestamp value from row (or use row index as fallback).

        Args:
            row: Row dictionary
            row_index: Index of row in sequence

        Returns:
            Timestamp as float (seconds since epoch or row index)
        """
        if self.time_column and self.time_column in row:
            value = row[self.time_column]
            # Try to convert to numeric timestamp
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Try to parse as number
                try:
                    return float(value)
                except ValueError:
                    pass
                # Try to parse as datetime string (simple heuristic)
                # For now, use hash of string as proxy
                return float(hash(value))

        # Fallback to row index
        return float(row_index)

    def sample(
        self, rows: Iterator[Dict[str, Any]], columns: List[str]
    ) -> Iterator[Dict[str, Any]]:
        """
        Sample rows ensuring coverage from early, middle, and late segments.

        Args:
            rows: Iterator of row dictionaries
            columns: List of column names

        Yields:
            Sampled row dictionaries
        """
        target_size = self.config.target_rows

        # Phase 1: Collect all rows with timestamps
        all_rows: List[tuple[float, Dict[str, Any]]] = []
        row_index = 0

        for row in rows:
            timestamp = self._get_timestamp_value(row, row_index)
            all_rows.append((timestamp, row))
            row_index += 1

        if not all_rows:
            return

        # Sort by timestamp
        all_rows.sort(key=lambda x: x[0])

        total_rows = len(all_rows)
        if total_rows <= target_size:
            # If we have fewer rows than target, return all
            for _, row in all_rows:
                yield row
            return

        # Phase 2: Divide into three segments (early, middle, late)
        segment_size = total_rows // 3
        early_end = segment_size
        middle_start = segment_size
        middle_end = segment_size * 2
        late_start = segment_size * 2

        early_rows = all_rows[:early_end]
        middle_rows = all_rows[middle_start:middle_end]
        late_rows = all_rows[late_start:]

        # Phase 3: Sample from each segment
        samples_per_segment = target_size // 3
        remaining = target_size - (samples_per_segment * 3)

        sampled: List[Dict[str, Any]] = []

        # Sample from early segment
        if early_rows:
            count = samples_per_segment + (1 if remaining > 0 else 0)
            count = min(count, len(early_rows))
            sampled_rows = self.rng.sample(early_rows, count)
            sampled.extend([row for _, row in sampled_rows])
            remaining -= 1 if remaining > 0 else 0

        # Sample from middle segment
        if middle_rows:
            count = samples_per_segment + (1 if remaining > 0 else 0)
            count = min(count, len(middle_rows))
            sampled_rows = self.rng.sample(middle_rows, count)
            sampled.extend([row for _, row in sampled_rows])
            remaining -= 1 if remaining > 0 else 0

        # Sample from late segment
        if late_rows:
            count = samples_per_segment + remaining
            count = min(count, len(late_rows))
            sampled_rows = self.rng.sample(late_rows, count)
            sampled.extend([row for _, row in sampled_rows])

        # Shuffle to mix segments
        self.rng.shuffle(sampled)

        # Yield sampled rows
        for row in sampled[:target_size]:
            yield row

