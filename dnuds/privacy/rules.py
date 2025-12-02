# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Privacy rule application."""

from typing import Any, Dict, List

from dnuds.config import PrivacyRule
from dnuds.privacy.masks import apply_mask


def apply_privacy_rules(
    row: Dict[str, Any], privacy_rules: List[PrivacyRule]
) -> Dict[str, Any]:
    """
    Apply privacy rules to a row, masking specified columns.

    Args:
        row: Row dictionary to mask
        privacy_rules: List of privacy rules to apply

    Returns:
        New row dictionary with masked values
    """
    if not privacy_rules:
        return row.copy()

    masked_row = row.copy()

    for rule in privacy_rules:
        column = rule.column
        if column in masked_row:
            masked_value = apply_mask(
                masked_row[column], rule.mask_type, rule.mask_params
            )
            masked_row[column] = masked_value

    return masked_row

