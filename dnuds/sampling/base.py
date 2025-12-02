# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Base classes for sampling algorithms."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional

from dnuds.config import SamplerConfig


class Sampler(ABC):
    """Abstract base class for sampling algorithms."""

    def __init__(self, config: SamplerConfig):
        """
        Initialize sampler with configuration.

        Args:
            config: Sampling configuration
        """
        self.config = config

    @abstractmethod
    def sample(
        self, rows: Iterator[Dict[str, Any]], columns: List[str]
    ) -> Iterator[Dict[str, Any]]:
        """
        Sample rows from an input iterator.

        Args:
            rows: Iterator of row dictionaries
            columns: List of column names

        Yields:
            Sampled row dictionaries
        """
        pass

    def get_sample_size(self, total_rows: Optional[int] = None) -> int:
        """
        Get the target sample size.

        Args:
            total_rows: Total number of rows (if known)

        Returns:
            Target sample size
        """
        if total_rows is None:
            return self.config.target_rows
        return min(self.config.target_rows, total_rows)

