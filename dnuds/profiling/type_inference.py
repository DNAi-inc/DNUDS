# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Type inference for column values."""

import re
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class TypeGuess(str, Enum):
    """Possible type guesses for column values."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    UNKNOWN = "unknown"


# Common datetime patterns
DATETIME_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}",  # ISO format
    r"\d{4}-\d{2}-\d{2}",  # Date only
    r"\d{2}/\d{2}/\d{4}",  # US date format
    r"\d{2}-\d{2}-\d{4}",  # Alternative date format
]


def infer_type(value: Any) -> TypeGuess:
    """
    Infer the type of a single value.

    Args:
        value: Value to infer type for

    Returns:
        TypeGuess enum value
    """
    if value is None:
        return TypeGuess.UNKNOWN

    # Check boolean first (before int, since bool is subclass of int in Python)
    if isinstance(value, bool):
        return TypeGuess.BOOLEAN

    # Check integer
    if isinstance(value, int):
        return TypeGuess.INTEGER

    # Check float
    if isinstance(value, float):
        return TypeGuess.FLOAT

    # Check datetime
    if isinstance(value, datetime):
        return TypeGuess.DATETIME

    # For string values, try to infer type
    if isinstance(value, str):
        value_stripped = value.strip()

        # Empty string
        if not value_stripped:
            return TypeGuess.STRING

        # Try boolean strings
        if value_stripped.lower() in ("true", "false", "yes", "no", "1", "0"):
            return TypeGuess.BOOLEAN

        # Try integer
        try:
            int(value_stripped)
            return TypeGuess.INTEGER
        except ValueError:
            pass

        # Try float
        try:
            float(value_stripped)
            return TypeGuess.FLOAT
        except ValueError:
            pass

        # Try datetime patterns
        for pattern in DATETIME_PATTERNS:
            if re.match(pattern, value_stripped):
                return TypeGuess.DATETIME

        # Default to string
        return TypeGuess.STRING

    # Unknown type
    return TypeGuess.UNKNOWN


def infer_column_type(values: list[Any], sample_size: int = 100) -> TypeGuess:
    """
    Infer the type of a column from a sample of values.

    Args:
        values: List of values from the column
        sample_size: Maximum number of values to sample for inference

    Returns:
        TypeGuess enum value representing the most likely type
    """
    if not values:
        return TypeGuess.UNKNOWN

    # Sample values if list is too long
    sample = values[:sample_size] if len(values) > sample_size else values

    # Count type guesses
    type_counts: dict[TypeGuess, int] = {}
    for value in sample:
        if value is not None:
            type_guess = infer_type(value)
            type_counts[type_guess] = type_counts.get(type_guess, 0) + 1

    if not type_counts:
        return TypeGuess.UNKNOWN

    # Return most common type
    most_common = max(type_counts.items(), key=lambda x: x[1])
    return most_common[0]

