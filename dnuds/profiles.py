# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Profile definitions and factory for DNUDS."""

from typing import Any, Dict

from dnuds.config import SamplerConfig, get_profile_config


def create_config_from_profile(
    profile_name: str, overrides: Dict[str, Any] = None
) -> SamplerConfig:
    """
    Create a SamplerConfig from a profile with optional overrides.

    Args:
        profile_name: Name of the profile
        overrides: Dictionary of configuration values to override

    Returns:
        SamplerConfig instance

    Raises:
        ValueError: If profile name is unknown
    """
    profile_dict = get_profile_config(profile_name)

    # Apply overrides
    if overrides:
        profile_dict.update(overrides)

    return SamplerConfig(**profile_dict)


# Profile descriptions for documentation
PROFILE_DESCRIPTIONS: Dict[str, str] = {
    "debug_sample": (
        "Small samples preserving diversity and rare values. "
        "Uses random sampling with optional stratification. "
        "Good for debugging and manual inspection."
    ),
    "schema_sample": (
        "Minimal rows covering distinct shapes and categories. "
        "Uses stratified sampling to ensure representation across categories. "
        "Good for schema inference and test data generation."
    ),
    "smoke_test_sample": (
        "Deterministic samples for automated testing. "
        "Uses fixed random seed for reproducible outputs. "
        "Good for regression testing and CI/CD pipelines."
    ),
    "privacy_sample": (
        "Samples with privacy masking applied. "
        "Requires privacy_rules configuration. "
        "Good for sharing data samples while protecting sensitive information."
    ),
}

