# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Manifest generation for DNUDS sampling runs."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dnuds.__version__ import __version__
from dnuds.config import SamplerConfig
from dnuds.profiling.stats import ColumnStats, collect_stats


def generate_manifest(
    input_path: str,
    output_path: str,
    config: SamplerConfig,
    input_format: str,
    output_format: str,
    columns: List[str],
    row_count: int,
    stats: Optional[Dict[str, ColumnStats]] = None,
) -> str:
    """
    Generate a manifest file for a sampling run.

    Args:
        input_path: Path to input file
        output_path: Path to output file
        config: Sampling configuration used
        input_format: Input format (csv, jsonl, log, sql)
        output_format: Output format (csv, jsonl, log, sql)
        columns: List of column names
        row_count: Number of rows in output sample
        stats: Optional column statistics

    Returns:
        Path to the generated manifest file
    """
    # Determine manifest path (same base name as output + .dnuds.json)
    output_file = Path(output_path)
    manifest_path = output_file.parent / f"{output_file.stem}.dnuds.json"

    # Ensure manifest directory exists
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # Build manifest data
    manifest: Dict[str, Any] = {
        "dnuds_version": __version__,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "input_path": str(Path(input_path).absolute()),
        "output_path": str(Path(output_path).absolute()),
        "input_format": input_format,
        "output_format": output_format,
        "sampling_mode": config.sampling_mode,
        "target_rows": config.target_rows,
        "actual_rows": row_count,
        "key_columns": config.key_columns or [],
        "seed": config.seed,
        "columns": columns,
        "column_count": len(columns),
    }

    # Add statistics if provided
    if stats:
        column_stats: Dict[str, Any] = {}
        for col_name, col_stats in stats.items():
            column_stats[col_name] = {
                "type_guess": col_stats.type_guess.value,
                "null_count": col_stats.null_count,
                "total_count": col_stats.total_count,
                "unique_count": col_stats.unique_count,
            }
            if col_stats.min_value is not None:
                column_stats[col_name]["min_value"] = col_stats.min_value
            if col_stats.max_value is not None:
                column_stats[col_name]["max_value"] = col_stats.max_value
            if col_stats.top_values:
                # Convert to list of [value, count] pairs for JSON serialization
                column_stats[col_name]["top_values"] = [
                    [str(k), v] for k, v in list(col_stats.top_values.items())[:10]
                ]

        manifest["column_stats"] = column_stats

    # Add privacy rules if present
    if config.privacy_rules:
        manifest["privacy_rules"] = [
            {
                "column": rule.column,
                "mask_type": rule.mask_type,
                "mask_params": rule.mask_params,
            }
            for rule in config.privacy_rules
        ]

    # Write manifest file
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return str(manifest_path)


def read_manifest(manifest_path: str) -> Dict[str, Any]:
    """
    Read a manifest file.

    Args:
        manifest_path: Path to manifest file

    Returns:
        Dictionary with manifest data

    Raises:
        FileNotFoundError: If manifest file doesn't exist
        json.JSONDecodeError: If manifest file is invalid JSON
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)

