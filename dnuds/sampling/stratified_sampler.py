# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Stratified sampling by key columns."""

import random
from collections import defaultdict
from typing import Any, Dict, Iterator, List, Optional

from dnuds.sampling.base import Sampler


class StratifiedSampler(Sampler):
    """
    Stratified sampler that ensures representation across key columns.

    Maintains a minimum number of rows per category while respecting
    the total target sample size.
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize stratified sampler.

        Args:
            config: Sampling configuration with key_columns specified
        """
        super().__init__(config)
        if config.key_columns is None or len(config.key_columns) == 0:
            raise ValueError(
                "Stratified sampling requires at least one key column. "
                "Set key_columns in config."
            )

        # Initialize random number generator
        if config.seed is not None:
            self.rng = random.Random(config.seed)
        else:
            self.rng = random.Random()

        self.key_columns = config.key_columns

    def _get_category_key(self, row: Dict[str, Any]) -> str:
        """
        Generate a category key from row values.

        Args:
            row: Row dictionary

        Returns:
            String representation of category (comma-separated values)
        """
        key_parts = []
        for col in self.key_columns:
            value = row.get(col)
            # Convert None to string representation
            key_parts.append(str(value) if value is not None else "None")
        return "|".join(key_parts)

    def sample(
        self, rows: Iterator[Dict[str, Any]], columns: List[str]
    ) -> Iterator[Dict[str, Any]]:
        """
        Sample rows using stratified sampling.

        Args:
            rows: Iterator of row dictionaries
            columns: List of column names

        Yields:
            Sampled row dictionaries
        """
        target_size = self.config.target_rows

        # Phase 1: Collect all rows grouped by category
        category_rows: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        total_rows = 0

        for row in rows:
            category_key = self._get_category_key(row)
            category_rows[category_key].append(row)
            total_rows += 1

        # Phase 2: Calculate sampling strategy
        num_categories = len(category_rows)
        if num_categories == 0:
            return

        # Minimum rows per category (at least 1, but adjust based on target)
        min_per_category = max(1, target_size // (num_categories * 2))
        # Maximum rows per category (to prevent one category from dominating)
        max_per_category = max(min_per_category, target_size // max(1, num_categories // 2))

        # Phase 3: Sample from each category
        sampled: List[Dict[str, Any]] = []

        # First pass: ensure minimum representation
        remaining_target = target_size
        for category_key, category_list in category_rows.items():
            category_size = len(category_list)
            # Sample at least min_per_category, but not more than available
            sample_count = min(min_per_category, category_size, remaining_target)
            if sample_count > 0:
                sampled_rows = self.rng.sample(category_list, sample_count)
                sampled.extend(sampled_rows)
                remaining_target -= sample_count

        # Second pass: fill remaining slots proportionally
        if remaining_target > 0 and len(sampled) < target_size:
            # Calculate remaining capacity per category
            category_capacities: Dict[str, int] = {}
            for category_key, category_list in category_rows.items():
                already_sampled = sum(
                    1 for row in sampled if self._get_category_key(row) == category_key
                )
                available = len(category_list) - already_sampled
                capacity = min(available, max_per_category - already_sampled)
                if capacity > 0:
                    category_capacities[category_key] = capacity

            # Distribute remaining slots
            while remaining_target > 0 and category_capacities:
                # Select category with highest capacity
                if not category_capacities:
                    break

                # Weight selection by capacity
                total_capacity = sum(category_capacities.values())
                if total_capacity == 0:
                    break

                # Random selection weighted by capacity
                rand_val = self.rng.random() * total_capacity
                cumulative = 0
                selected_category = None

                for cat_key, capacity in category_capacities.items():
                    cumulative += capacity
                    if rand_val <= cumulative:
                        selected_category = cat_key
                        break

                if selected_category is None:
                    selected_category = list(category_capacities.keys())[0]

                # Sample one row from selected category
                category_list = category_rows[selected_category]
                already_sampled_keys = {
                    self._get_category_key(row) for row in sampled
                }
                available_rows = [
                    row
                    for row in category_list
                    if self._get_category_key(row) not in already_sampled_keys
                    or row not in sampled
                ]

                if available_rows:
                    sampled_row = self.rng.choice(available_rows)
                    sampled.append(sampled_row)
                    remaining_target -= 1
                    category_capacities[selected_category] -= 1
                    if category_capacities[selected_category] <= 0:
                        del category_capacities[selected_category]
                else:
                    # No more rows available in this category
                    del category_capacities[selected_category]

        # Shuffle final sample for randomness
        self.rng.shuffle(sampled)

        # Yield sampled rows
        for row in sampled[:target_size]:
            yield row

