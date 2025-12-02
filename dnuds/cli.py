# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Command-line interface for DNUDS."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dnuds import __version__
from dnuds.config import PrivacyRule, SamplerConfig
from dnuds.core import sample_file
from dnuds.formats import FormatType, detect_format
from dnuds.profiles import create_config_from_profile


def load_config_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON or YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Dictionary with configuration values

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file format is unsupported
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        if path.suffix.lower() in (".json",):
            return json.load(f)
        elif path.suffix.lower() in (".yaml", ".yml"):
            try:
                import yaml

                return yaml.safe_load(f)
            except ImportError:
                raise ValueError(
                    "YAML support requires pyyaml. Install with: pip install pyyaml"
                )
        else:
            # Try JSON first, then YAML
            try:
                content = f.read()
                f.seek(0)
                return json.loads(content)
            except json.JSONDecodeError:
                try:
                    import yaml

                    return yaml.safe_load(f)
                except ImportError:
                    raise ValueError("Could not parse config file. Supported: JSON, YAML")


def parse_privacy_rules(config_dict: Dict[str, Any]) -> Optional[List[PrivacyRule]]:
    """
    Parse privacy rules from configuration dictionary.

    Args:
        config_dict: Configuration dictionary

    Returns:
        List of PrivacyRule objects or None
    """
    privacy_config = config_dict.get("privacy_rules")
    if not privacy_config:
        return None

    rules = []
    if isinstance(privacy_config, list):
        for rule_dict in privacy_config:
            if isinstance(rule_dict, dict):
                rules.append(
                    PrivacyRule(
                        column=rule_dict.get("column", ""),
                        mask_type=rule_dict.get("mask_type", "redact"),
                        mask_params=rule_dict.get("mask_params", {}),
                    )
                )
    elif isinstance(privacy_config, dict):
        # Format: {"column_name": "mask_type"} or {"column_name": {"type": "...", "params": {...}}}
        for column, mask_spec in privacy_config.items():
            if isinstance(mask_spec, str):
                rules.append(PrivacyRule(column=column, mask_type=mask_spec))
            elif isinstance(mask_spec, dict):
                rules.append(
                    PrivacyRule(
                        column=column,
                        mask_type=mask_spec.get("type", "redact"),
                        mask_params=mask_spec.get("params", {}),
                    )
                )

    return rules if rules else None


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="dnuds",
        description="DNUDS - DNAi Universal Data Sampler. Create representative samples from large data files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dnuds sample input.csv output.csv
  dnuds sample input.jsonl output.jsonl --format jsonl --profile debug_sample --rows 2000
  dnuds sample access.log sample.log --format log --profile debug_sample --rows 500 --key-col status --key-col service
  dnuds sample dump.sql sample.csv --format sql --profile schema_sample --table users --rows 1000 --seed 42
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"dnuds {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True

    # Sample command
    sample_parser = subparsers.add_parser(
        "sample", help="Sample rows from an input file"
    )

    sample_parser.add_argument(
        "input",
        type=str,
        help="Path to input file",
    )

    sample_parser.add_argument(
        "output",
        type=str,
        help="Path to output file",
    )

    sample_parser.add_argument(
        "--format",
        type=str,
        choices=["csv", "jsonl", "log", "sql"],
        default=None,
        help="Input/output format (auto-detected from extension if not specified)",
    )

    sample_parser.add_argument(
        "--profile",
        type=str,
        default="debug_sample",
        choices=["debug_sample", "schema_sample", "smoke_test_sample", "privacy_sample"],
        help="Sampling profile (default: debug_sample)",
    )

    sample_parser.add_argument(
        "--rows",
        type=int,
        default=None,
        help="Target number of rows in sample (overrides profile default)",
    )

    sample_parser.add_argument(
        "--key-col",
        type=str,
        action="append",
        dest="key_columns",
        help="Key column for stratified sampling (can be specified multiple times)",
    )

    sample_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )

    sample_parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file (JSON or YAML)",
    )

    sample_parser.add_argument(
        "--table",
        type=str,
        default=None,
        help="Table name for SQL dumps (filters INSERT statements)",
    )

    sample_parser.add_argument(
        "--sampling-mode",
        type=str,
        choices=["random", "stratified", "time_aware", "outlier_aware", "composite"],
        default=None,
        help="Sampling mode (overrides profile default)",
    )

    return parser


def main() -> int:
    """
    Main entry point for the DNUDS CLI.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()

    # If no arguments are provided, show a concise banner and quick help.
    if len(sys.argv) == 1:
        print(f"dnuds {__version__} - DNAi Universal Data Sampler")
        print("Copyright (c) 2025 DNAi Inc.")
        print()
        print("Usage: dnuds sample <input> <output> [options]")
        print("Try 'dnuds --help' for full usage and examples.\n")
        parser.print_help()
        return 0

    args = parser.parse_args()

    if args.command != "sample":
        parser.print_help()
        return 1

    try:
        # Validate input file exists
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            return 1

        # Determine format
        format_type: Optional[FormatType] = None
        if args.format:
            try:
                format_type = FormatType(args.format.lower())
            except ValueError:
                print(
                    f"Error: Unknown format: {args.format}",
                    file=sys.stderr,
                )
                print("Supported formats: csv, jsonl, log, sql", file=sys.stderr)
                return 1
        else:
            # Auto-detect
            format_type = detect_format(str(input_path))

        if format_type == FormatType.UNKNOWN:
            print(
                f"Error: Could not determine format for: {args.input}",
                file=sys.stderr,
            )
            print("Please specify --format explicitly", file=sys.stderr)
            return 1

        # Load configuration
        config_overrides: Dict[str, Any] = {}

        # Load from config file if provided
        if args.config:
            try:
                file_config = load_config_file(args.config)
                config_overrides.update(file_config)
            except Exception as e:
                print(f"Error loading config file: {e}", file=sys.stderr)
                return 1

        # Apply CLI arguments (these override config file)
        if args.rows is not None:
            config_overrides["target_rows"] = args.rows

        if args.key_columns:
            config_overrides["key_columns"] = args.key_columns

        if args.seed is not None:
            config_overrides["seed"] = args.seed

        if args.sampling_mode:
            config_overrides["sampling_mode"] = args.sampling_mode

        # Parse privacy rules from config
        privacy_rules = None
        if "privacy_rules" in config_overrides:
            privacy_rules = parse_privacy_rules(config_overrides)
            config_overrides["privacy_rules"] = privacy_rules

        # Create config from profile with overrides
        try:
            config = create_config_from_profile(args.profile, config_overrides)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        # Perform sampling
        print(f"Sampling {args.input} -> {args.output}...", file=sys.stderr)
        result = sample_file(
            input_path=str(input_path),
            output_path=args.output,
            format=format_type.value if format_type else None,
            profile=args.profile,
            target_rows=config.target_rows,
            key_columns=config.key_columns,
            config=config,
        )

        print(
            f"Successfully sampled {result.row_count} rows to {result.output_path}",
            file=sys.stderr,
        )
        if result.manifest_path:
            print(f"Manifest: {result.manifest_path}", file=sys.stderr)

        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
