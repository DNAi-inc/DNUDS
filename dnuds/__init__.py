# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""
DNUDS - DNAi Universal Data Sampler

A Python library and CLI for creating representative samples from large data files.
"""

from dnuds.__version__ import __version__
from dnuds.core import SampleResult, sample_file
from dnuds.config import SamplerConfig

__all__ = [
    "__version__",
    "sample_file",
    "SamplerConfig",
    "SampleResult",
]

