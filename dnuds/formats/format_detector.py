# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Format detection utilities."""

import re
from enum import Enum
from pathlib import Path
from typing import Optional


class FormatType(str, Enum):
    """Supported format types."""

    CSV = "csv"
    JSONL = "jsonl"
    LOG = "log"
    SQL = "sql"
    UNKNOWN = "unknown"


def detect_format(
    file_path: str, content_hint: Optional[str] = None
) -> FormatType:
    """
    Detect the format of a file based on extension and optionally content.

    Args:
        file_path: Path to the file
        content_hint: Optional first few lines of content for content-based detection

    Returns:
        Detected format type
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    # Extension-based detection
    if extension == ".csv":
        return FormatType.CSV
    elif extension in (".jsonl", ".ndjson"):
        return FormatType.JSONL
    elif extension == ".log":
        return FormatType.LOG
    elif extension == ".sql":
        return FormatType.SQL

    # Content-based detection if extension is ambiguous
    if content_hint:
        content_lower = content_hint.lower()
        # Check for JSONL (first line is valid JSON)
        if content_hint.strip().startswith("{") and content_hint.strip().endswith("}"):
            try:
                import json

                json.loads(content_hint.strip())
                return FormatType.JSONL
            except (json.JSONDecodeError, ValueError):
                pass

        # Check for CSV (comma-separated values)
        if "," in content_hint and "\n" in content_hint:
            return FormatType.CSV

        # Check for SQL (INSERT statements)
        if re.search(r"INSERT\s+INTO", content_lower):
            return FormatType.SQL

    return FormatType.UNKNOWN

