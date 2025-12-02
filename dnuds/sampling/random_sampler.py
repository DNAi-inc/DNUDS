# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Random sampling using reservoir sampling algorithm."""

import random
from typing import Any, Dict, Iterator, List

from dnuds.sampling.base import Sampler


class RandomSampler(Sampler):
    """
    Random sampler using reservoir sampling for single-pass uniform sampling.

    Reservoir sampling ensures each row has equal probability of being selected
    without needing to know the total number of rows in advance.
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize random sampler.

        Args:
            config: Sampling configuration
        """
        super().__init__(config)
        # Initialize random number generator with seed if provided
        if config.seed is not None:
            self.rng = random.Random(config.seed)
        else:
            self.rng = random.Random()

    def sample(
        self, rows: Iterator[Dict[str, Any]], columns: List[str]
    ) -> Iterator[Dict[str, Any]]:
        """
        Sample rows using reservoir sampling algorithm.

        Args:
            rows: Iterator of row dictionaries
            columns: List of column names (unused for random sampling)

        Yields:
            Sampled row dictionaries
        """
        target_size = self.config.target_rows
        reservoir: List[Dict[str, Any]] = []
        count = 0

        # Phase 1: Fill reservoir with first target_size rows
        for row in rows:
            if len(reservoir) < target_size:
                reservoir.append(row)
            else:
                # Phase 2: Replace elements with decreasing probability
                # Random index from 0 to count (inclusive)
                index = self.rng.randint(0, count)
                if index < target_size:
                    reservoir[index] = row
            count += 1

        # Yield all rows in reservoir
        for row in reservoir:
            yield row

