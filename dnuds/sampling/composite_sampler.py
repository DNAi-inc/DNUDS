# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Composite sampler that combines multiple sampling strategies."""

from typing import Any, Dict, Iterator, List

from dnuds.sampling.base import Sampler


class CompositeSampler(Sampler):
    """
    Composite sampler that applies multiple sampling strategies in sequence.

    This allows combining strategies like: outlier detection + time-aware + random.
    """

    def __init__(self, config: Any, samplers: List[Sampler]) -> None:
        """
        Initialize composite sampler.

        Args:
            config: Sampling configuration
            samplers: List of samplers to apply in sequence
        """
        super().__init__(config)
        self.samplers = samplers

    def sample(
        self, rows: Iterator[Dict[str, Any]], columns: List[str]
    ) -> Iterator[Dict[str, Any]]:
        """
        Apply multiple samplers in sequence.

        Args:
            rows: Iterator of row dictionaries
            columns: List of column names

        Yields:
            Sampled row dictionaries
        """
        current_rows = rows

        # Apply each sampler in sequence
        for sampler in self.samplers:
            current_rows = sampler.sample(current_rows, columns)

        # Yield final results
        for row in current_rows:
            yield row

