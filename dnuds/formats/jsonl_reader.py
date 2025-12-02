# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""JSONL (JSON Lines) format reader."""

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from dnuds.formats.base import FormatReader


class JSONLReader(FormatReader):
    """Streaming JSONL reader that handles one JSON object per line."""

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        """
        Initialize JSONL reader.

        Args:
            file_path: Path to the JSONL file
            encoding: File encoding (default: utf-8)
        """
        self.file_path = file_path
        self.encoding = encoding
        self.file_handle: Optional[Any] = None
        self.columns: List[str] = []
        self._columns_determined = False

    def _determine_columns(self, first_row: Dict[str, Any]) -> None:
        """
        Determine column names from first row.

        Args:
            first_row: First row as a dictionary
        """
        if self._columns_determined:
            return

        # For flat objects, use keys directly
        # For nested objects, we'll flatten simple structures
        self.columns = self._flatten_keys(first_row)
        self._columns_determined = True

    def _flatten_keys(self, obj: Dict[str, Any], prefix: str = "") -> List[str]:
        """
        Flatten nested dictionary keys for schema inference.

        Args:
            obj: Dictionary to flatten
            prefix: Prefix for nested keys

        Returns:
            List of flattened key names
        """
        keys: List[str] = []
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                # Recursively flatten nested dicts
                keys.extend(self._flatten_keys(value, full_key))
            else:
                keys.append(full_key)
        return keys

    def _flatten_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten a nested row dictionary.

        Args:
            row: Nested dictionary

        Returns:
            Flattened dictionary
        """
        result: Dict[str, Any] = {}

        def _flatten(obj: Any, prefix: str = "") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    _flatten(value, full_key)
            elif isinstance(obj, list):
                # For lists, convert to JSON string for now
                result[prefix] = json.dumps(obj)
            else:
                result[prefix] = obj

        _flatten(row)
        return result

    def read_rows(self) -> Iterator[Dict[str, Any]]:
        """
        Read rows from the JSONL file as dictionaries.

        Yields:
            Dictionary representing a row
        """
        if self.file_handle is None:
            self.file_handle = open(self.file_path, "r", encoding=self.encoding)

        for line_num, line in enumerate(self.file_handle, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                row = json.loads(line)
                if not isinstance(row, dict):
                    # Convert non-dict JSON to dict
                    row = {"value": row}

                # Determine columns from first row
                if not self._columns_determined:
                    self._determine_columns(row)

                # Flatten nested structures
                flattened = self._flatten_row(row)
                yield flattened

            except json.JSONDecodeError as e:
                # Skip invalid JSON lines with a warning
                # In production, might want to log this
                continue

    def get_columns(self) -> List[str]:
        """
        Get the list of column names.

        Returns:
            List of column names (determined from first row)
        """
        if not self._columns_determined:
            # Read first row to determine columns
            if self.file_handle is None:
                self.file_handle = open(self.file_path, "r", encoding=self.encoding)

            pos = self.file_handle.tell()
            try:
                first_line = self.file_handle.readline()
                if first_line.strip():
                    row = json.loads(first_line.strip())
                    if isinstance(row, dict):
                        self._determine_columns(row)
                    else:
                        self.columns = ["value"]
                else:
                    self.columns = []
            except (json.JSONDecodeError, StopIteration):
                self.columns = []
            finally:
                self.file_handle.seek(pos)

        return self.columns.copy()

    def close(self) -> None:
        """Close the reader and release resources."""
        if self.file_handle is not None:
            self.file_handle.close()
            self.file_handle = None

