# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Privacy masking functions."""

import hashlib
from typing import Any, Dict


def hash_mask(value: Any, algorithm: str = "sha256") -> str:
    """
    Hash a value using the specified algorithm.

    Args:
        value: Value to hash
        algorithm: Hash algorithm (sha256, sha1, md5)

    Returns:
        Hexadecimal hash string
    """
    if value is None:
        return ""

    value_str = str(value)
    if algorithm == "sha256":
        hash_obj = hashlib.sha256(value_str.encode("utf-8"))
    elif algorithm == "sha1":
        hash_obj = hashlib.sha1(value_str.encode("utf-8"))
    elif algorithm == "md5":
        hash_obj = hashlib.md5(value_str.encode("utf-8"))
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    return hash_obj.hexdigest()


def redact_mask(value: Any, token: str = "[REDACTED]") -> str:
    """
    Replace a value with a redaction token.

    Args:
        value: Value to redact
        token: Token to use for redaction

    Returns:
        Redaction token
    """
    if value is None:
        return token
    return token


def truncate_mask(value: Any, max_length: int = 4) -> str:
    """
    Truncate a value to maximum length.

    Args:
        value: Value to truncate
        max_length: Maximum length to keep

    Returns:
        Truncated string
    """
    if value is None:
        return ""

    value_str = str(value)
    if len(value_str) <= max_length:
        return value_str
    return value_str[:max_length] + "..."


def bucket_mask(value: Any, bucket_size: int = 10) -> str:
    """
    Replace a numeric value with a bucket label.

    Args:
        value: Numeric value to bucket
        bucket_size: Size of each bucket

    Returns:
        Bucket label string (e.g., "0-9", "10-19")
    """
    if value is None:
        return ""

    try:
        num_value = float(value)
        bucket_start = int((num_value // bucket_size) * bucket_size)
        bucket_end = bucket_start + bucket_size - 1
        return f"{bucket_start}-{bucket_end}"
    except (ValueError, TypeError):
        # If not numeric, return original or empty
        return ""


def apply_mask(
    value: Any, mask_type: str, mask_params: Dict[str, Any] = None
) -> Any:
    """
    Apply a mask to a value based on mask type and parameters.

    Args:
        value: Value to mask
        mask_type: Type of mask (hash, redact, truncate, bucket)
        mask_params: Optional parameters for the mask

    Returns:
        Masked value

    Raises:
        ValueError: If mask_type is unknown
    """
    if mask_params is None:
        mask_params = {}

    if mask_type == "hash":
        algorithm = mask_params.get("algorithm", "sha256")
        return hash_mask(value, algorithm)
    elif mask_type == "redact":
        token = mask_params.get("token", "[REDACTED]")
        return redact_mask(value, token)
    elif mask_type == "truncate":
        max_length = mask_params.get("max_length", 4)
        return truncate_mask(value, max_length)
    elif mask_type == "bucket":
        bucket_size = mask_params.get("bucket_size", 10)
        return bucket_mask(value, bucket_size)
    else:
        raise ValueError(f"Unknown mask type: {mask_type}")

