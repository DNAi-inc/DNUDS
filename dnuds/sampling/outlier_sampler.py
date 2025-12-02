# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Outlier-aware sampling that ensures inclusion of min/max values."""

import random
from typing import Any, Dict, Iterator, List, Optional

from dnuds.profiling.type_inference import TypeGuess, infer_type
from dnuds.sampling.base import Sampler


class OutlierSampler(Sampler):
    """
    Outlier-aware sampler that ensures rows with min/max values are included.

    Detects numeric columns and ensures rows containing extreme values appear in sample.
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize outlier-aware sampler.

        Args:
            config: Sampling configuration
        """
        super().__init__(config)
        # Initialize random number generator
        if config.seed is not None:
            self.rng = random.Random(config.seed)
        else:
            self.rng = random.Random()

        # Columns to check for outliers (if None, auto-detect numeric columns)
        self.outlier_columns: Optional[List[str]] = config.key_columns

    def _is_numeric(self, value: Any) -> bool:
        """
        Check if a value is numeric.

        Args:
            value: Value to check

        Returns:
            True if value is numeric
        """
        type_guess = infer_type(value)
        return type_guess in (TypeGuess.INTEGER, TypeGuess.FLOAT)

    def _get_numeric_value(self, value: Any) -> Optional[float]:
        """
        Convert value to float if numeric.

        Args:
            value: Value to convert

        Returns:
            Float value or None if not numeric
        """
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None

        return None

    def sample(
        self, rows: Iterator[Dict[str, Any]], columns: List[str]
    ) -> Iterator[Dict[str, Any]]:
        """
        Sample rows ensuring outliers (min/max) are included.

        Args:
            rows: Iterator of row dictionaries
            columns: List of column names

        Yields:
            Sampled row dictionaries
        """
        target_size = self.config.target_rows

        # Phase 1: Collect all rows and find outliers
        all_rows: List[Dict[str, Any]] = []
        column_stats: Dict[str, Dict[str, Optional[float]]] = {}

        # Determine columns to check for outliers
        columns_to_check = self.outlier_columns or columns

        for row in rows:
            all_rows.append(row)

            # Update min/max for numeric columns
            for col in columns_to_check:
                if col not in row:
                    continue

                value = self._get_numeric_value(row.get(col))
                if value is not None:
                    if col not in column_stats:
                        column_stats[col] = {"min": None, "max": None, "min_row": None, "max_row": None}

                    stats = column_stats[col]
                    if stats["min"] is None or value < stats["min"]:
                        stats["min"] = value
                        stats["min_row"] = row
                    if stats["max"] is None or value > stats["max"]:
                        stats["max"] = value
                        stats["max_row"] = row

        if not all_rows:
            return

        total_rows = len(all_rows)
        if total_rows <= target_size:
            # If we have fewer rows than target, return all
            for row in all_rows:
                yield row
            return

        # Phase 2: Collect outlier rows
        outlier_rows: List[Dict[str, Any]] = []
        outlier_set = set()

        for col, stats in column_stats.items():
            if stats["min_row"] is not None:
                # Use id() as proxy for row identity (since dicts aren't hashable)
                row_id = id(stats["min_row"])
                if row_id not in outlier_set:
                    outlier_rows.append(stats["min_row"])
                    outlier_set.add(row_id)

            if stats["max_row"] is not None:
                row_id = id(stats["max_row"])
                if row_id not in outlier_set:
                    outlier_rows.append(stats["max_row"])
                    outlier_set.add(row_id)

        # Phase 3: Sample remaining rows randomly
        remaining_target = target_size - len(outlier_rows)
        if remaining_target > 0:
            # Get rows that aren't outliers
            non_outlier_rows = [
                row for row in all_rows if id(row) not in outlier_set
            ]
            if non_outlier_rows:
                sample_count = min(remaining_target, len(non_outlier_rows))
                sampled_rows = self.rng.sample(non_outlier_rows, sample_count)
                outlier_rows.extend(sampled_rows)

        # Shuffle to mix outliers with regular samples
        self.rng.shuffle(outlier_rows)

        # Yield sampled rows (up to target size)
        for row in outlier_rows[:target_size]:
            yield row

