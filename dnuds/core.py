# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Core API for DNUDS."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from dnuds.config import PrivacyRule, SamplerConfig, get_profile_config
from dnuds.manifest import generate_manifest
from dnuds.privacy.rules import apply_privacy_rules
from dnuds.formats import (
    FormatReader,
    FormatWriter,
    detect_format,
    FormatType,
    CSVReader,
    CSVWriter,
    JSONLReader,
    JSONLWriter,
    LogReader,
    LogWriter,
    SQLReader,
    SQLWriter,
)
from dnuds.sampling import (
    CompositeSampler,
    OutlierSampler,
    RandomSampler,
    Sampler,
    StratifiedSampler,
    TimeSampler,
)


@dataclass
class SampleResult:
    """
    Result of a sampling operation.

    Attributes:
        output_path: Path to the output sample file
        row_count: Number of rows in the output sample
        manifest_path: Path to the manifest file (if generated)
    """

    output_path: str
    row_count: int
    manifest_path: Optional[str] = None


def _get_reader(
    file_path: str, format_type: Optional[FormatType] = None
) -> FormatReader:
    """
    Create an appropriate reader for the input file.

    Args:
        file_path: Path to input file
        format_type: Format type (auto-detected if None)

    Returns:
        FormatReader instance

    Raises:
        ValueError: If format cannot be determined or is unsupported
    """
    if format_type is None:
        format_type = detect_format(file_path)

    if format_type == FormatType.CSV:
        return CSVReader(file_path)
    elif format_type == FormatType.JSONL:
        return JSONLReader(file_path)
    elif format_type == FormatType.LOG:
        return LogReader(file_path)
    elif format_type == FormatType.SQL:
        return SQLReader(file_path)
    else:
        raise ValueError(
            f"Unsupported format: {format_type}. "
            "Supported formats: CSV, JSONL, LOG, SQL"
        )


def _get_writer(
    file_path: str,
    format_type: Optional[FormatType] = None,
    columns: Optional[List[str]] = None,
) -> FormatWriter:
    """
    Create an appropriate writer for the output file.

    Args:
        file_path: Path to output file
        format_type: Format type (auto-detected if None)
        columns: List of column names (for CSV header)

    Returns:
        FormatWriter instance

    Raises:
        ValueError: If format cannot be determined or is unsupported
    """
    if format_type is None:
        format_type = detect_format(file_path)

    if format_type == FormatType.CSV:
        return CSVWriter(file_path, columns=columns)
    elif format_type == FormatType.JSONL:
        return JSONLWriter(file_path)
    elif format_type == FormatType.LOG:
        return LogWriter(file_path)
    elif format_type == FormatType.SQL:
        return SQLWriter(file_path)
    else:
        raise ValueError(
            f"Unsupported format: {format_type}. "
            "Supported formats: CSV, JSONL, LOG, SQL"
        )


def _get_sampler(config: SamplerConfig) -> Sampler:
    """
    Create an appropriate sampler based on configuration.

    Args:
        config: Sampling configuration

    Returns:
        Sampler instance

    Raises:
        ValueError: If sampling mode is unsupported
    """
    if config.sampling_mode == "random":
        return RandomSampler(config)
    elif config.sampling_mode == "stratified":
        return StratifiedSampler(config)
    elif config.sampling_mode == "time_aware":
        return TimeSampler(config)
    elif config.sampling_mode == "outlier_aware":
        return OutlierSampler(config)
    elif config.sampling_mode == "composite":
        # For composite, we'd need additional config to specify which samplers
        # For now, default to outlier + time + random
        samplers = [
            OutlierSampler(config),
            TimeSampler(config),
            RandomSampler(config),
        ]
        return CompositeSampler(config, samplers)
    else:
        raise ValueError(
            f"Unsupported sampling mode: {config.sampling_mode}. "
            "Supported modes: random, stratified, time_aware, outlier_aware, composite"
        )


def sample_file(
    input_path: str,
    output_path: str,
    format: Optional[str] = None,
    profile: str = "debug_sample",
    target_rows: int = 1000,
    key_columns: Optional[List[str]] = None,
    config: Optional[SamplerConfig] = None,
) -> SampleResult:
    """
    Sample rows from an input file and write to an output file.

    Args:
        input_path: Path to input file
        output_path: Path to output file
        format: Input/output format (auto-detected if None)
        profile: Sampling profile name (default: debug_sample)
        target_rows: Target number of rows in sample (overrides profile default)
        key_columns: List of key columns for stratified sampling
        config: Optional SamplerConfig (overrides profile and other args)

    Returns:
        SampleResult with output path, row count, and manifest path

    Raises:
        FileNotFoundError: If input file does not exist
        ValueError: If configuration is invalid
    """
    # Validate input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Determine format
    format_type: Optional[FormatType] = None
    if format:
        try:
            format_type = FormatType(format.lower())
        except ValueError:
            raise ValueError(f"Unknown format: {format}")

    # Build configuration
    if config is None:
        # Start with profile defaults
        profile_config = get_profile_config(profile)
        config_dict: Dict[str, Any] = profile_config.copy()

        # Override with explicit arguments
        if target_rows != 1000:  # Only override if different from default
            config_dict["target_rows"] = target_rows
        if key_columns is not None:
            config_dict["key_columns"] = key_columns

        config = SamplerConfig(**config_dict)

    # Create reader and writer
    reader = _get_reader(input_path, format_type)
    columns = reader.get_columns()

    writer = _get_writer(output_path, format_type, columns)
    writer.write_header(columns)

    # Create sampler
    sampler = _get_sampler(config)

    # Perform sampling
    row_count = 0
    sampled_rows_list: List[Dict[str, Any]] = []
    try:
        sampled_rows = sampler.sample(reader.read_rows(), columns)
        for row in sampled_rows:
            # Apply privacy rules if configured
            if config.privacy_rules:
                row = apply_privacy_rules(row, config.privacy_rules)
            writer.write_row(row)
            sampled_rows_list.append(row)
            row_count += 1
    finally:
        reader.close()
        writer.close()

    # Generate manifest
    input_format_str = (
        format_type.value if format_type else detect_format(input_path).value
    )
    output_format_str = (
        format_type.value if format_type else detect_format(output_path).value
    )

    # Collect basic stats for manifest (lightweight)
    stats = None
    try:
        from dnuds.profiling.stats import collect_stats

        # Re-read sampled rows for stats (or use collected list)
        stats = collect_stats(iter(sampled_rows_list), columns, max_top_values=10)
    except Exception:
        # If stats collection fails, continue without stats
        pass

    manifest_path = generate_manifest(
        input_path=input_path,
        output_path=output_path,
        config=config,
        input_format=input_format_str,
        output_format=output_format_str,
        columns=columns,
        row_count=row_count,
        stats=stats,
    )

    return SampleResult(
        output_path=output_path,
        row_count=row_count,
        manifest_path=manifest_path,
    )

