# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Line-based log format reader with optional parsing."""

import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from dnuds.formats.base import FormatReader


class LogReader(FormatReader):
    """
    Streaming log reader that treats each line as a message.

    Supports optional parsing of structured log formats.
    """

    def __init__(
        self,
        file_path: str,
        encoding: str = "utf-8",
        parse_pattern: Optional[str] = None,
    ):
        """
        Initialize log reader.

        Args:
            file_path: Path to the log file
            encoding: File encoding (default: utf-8)
            parse_pattern: Optional regex pattern to parse log lines
                Example: r'\[(\w+)\]\s+(.*)' for '[LEVEL] message' format
        """
        self.file_path = file_path
        self.encoding = encoding
        self.parse_pattern = parse_pattern
        self.file_handle: Optional[Any] = None
        self.columns: List[str] = ["message"]
        self._compiled_pattern: Optional[Any] = None

        if parse_pattern:
            self._compiled_pattern = re.compile(parse_pattern)
            # Try to infer column names from pattern (simple heuristic)
            # For now, use generic names
            self.columns = ["level", "message"]

    def _parse_line(self, line: str) -> Dict[str, Any]:
        """
        Parse a log line into a dictionary.

        Args:
            line: Log line to parse

        Returns:
            Dictionary with parsed fields
        """
        line = line.rstrip("\n\r")

        if self._compiled_pattern:
            match = self._compiled_pattern.match(line)
            if match:
                groups = match.groups()
                # Create dict from groups
                result: Dict[str, Any] = {}
                for i, col in enumerate(self.columns):
                    if i < len(groups):
                        result[col] = groups[i]
                    else:
                        result[col] = ""
                return result

        # Default: treat entire line as message
        return {"message": line}

    def read_rows(self) -> Iterator[Dict[str, Any]]:
        """
        Read rows from the log file as dictionaries.

        Yields:
            Dictionary representing a log entry
        """
        if self.file_handle is None:
            self.file_handle = open(self.file_path, "r", encoding=self.encoding)

        for line in self.file_handle:
            if line.strip():  # Skip empty lines
                yield self._parse_line(line)

    def get_columns(self) -> List[str]:
        """
        Get the list of column names.

        Returns:
            List of column names
        """
        return self.columns.copy()

    def close(self) -> None:
        """Close the reader and release resources."""
        if self.file_handle is not None:
            self.file_handle.close()
            self.file_handle = None

