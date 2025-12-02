# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Configuration classes for DNUDS."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PrivacyRule:
    """Configuration for privacy masking of a column."""

    column: str
    mask_type: str  # hash, redact, truncate, bucket
    mask_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SamplerConfig:
    """
    Configuration for data sampling.

    Attributes:
        sampling_mode: Sampling strategy (random, stratified, time_aware, outlier_aware)
        target_rows: Target number of rows in output sample
        max_memory_bytes: Approximate maximum memory usage (for future use)
        key_columns: List of column names to use for stratified sampling
        privacy_rules: List of privacy masking rules
        seed: Random seed for reproducibility (None for random)
        log_level: Logging level (for future use)
    """

    sampling_mode: str = "random"
    target_rows: int = 1000
    max_memory_bytes: Optional[int] = None
    key_columns: Optional[List[str]] = None
    privacy_rules: Optional[List[PrivacyRule]] = None
    seed: Optional[int] = None
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.target_rows < 1:
            raise ValueError("target_rows must be at least 1")
        if self.sampling_mode not in [
            "random",
            "stratified",
            "time_aware",
            "outlier_aware",
            "composite",
        ]:
            raise ValueError(
                f"Unknown sampling_mode: {self.sampling_mode}. "
                "Must be one of: random, stratified, time_aware, outlier_aware, composite"
            )


# Profile definitions
PROFILES: Dict[str, Dict[str, Any]] = {
    "debug_sample": {
        "sampling_mode": "random",
        "target_rows": 1000,
        "key_columns": None,
        "seed": None,
    },
    "schema_sample": {
        "sampling_mode": "stratified",
        "target_rows": 100,
        "key_columns": None,  # Will be determined from data
        "seed": None,
    },
    "smoke_test_sample": {
        "sampling_mode": "random",
        "target_rows": 100,
        "key_columns": None,
        "seed": 42,  # Fixed seed for determinism
    },
    "privacy_sample": {
        "sampling_mode": "random",
        "target_rows": 1000,
        "key_columns": None,
        "seed": None,
        "privacy_rules": [],  # Should be configured separately
    },
}


def get_profile_config(profile_name: str) -> Dict[str, Any]:
    """
    Get configuration for a named profile.

    Args:
        profile_name: Name of the profile

    Returns:
        Dictionary of configuration values

    Raises:
        ValueError: If profile name is unknown
    """
    if profile_name not in PROFILES:
        raise ValueError(
            f"Unknown profile: {profile_name}. "
            f"Available profiles: {', '.join(PROFILES.keys())}"
        )
    return PROFILES[profile_name].copy()

