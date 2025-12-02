# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""SQL dump format reader for INSERT statements."""

import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from dnuds.formats.base import FormatReader


class SQLReader(FormatReader):
    """
    Streaming SQL dump reader that parses INSERT statements.

    Supports MySQL/PostgreSQL-like INSERT syntax.
    """

    # Pattern to match INSERT INTO statements
    INSERT_PATTERN = re.compile(
        r"INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)",
        re.IGNORECASE,
    )

    def __init__(
        self,
        file_path: str,
        table_name: Optional[str] = None,
        encoding: str = "utf-8",
    ):
        """
        Initialize SQL reader.

        Args:
            file_path: Path to the SQL dump file
            table_name: Optional table name to filter (if None, uses first table found)
            encoding: File encoding (default: utf-8)
        """
        self.file_path = file_path
        self.table_name = table_name
        self.encoding = encoding
        self.file_handle: Optional[Any] = None
        self.columns: List[str] = []
        self._columns_determined = False

    def _parse_value(self, value_str: str) -> Any:
        """
        Parse a SQL value string into Python value.

        Args:
            value_str: SQL value string (may be quoted, NULL, number, etc.)

        Returns:
            Parsed Python value
        """
        value_str = value_str.strip()

        # NULL
        if value_str.upper() == "NULL":
            return None

        # String (quoted)
        if (value_str.startswith("'") and value_str.endswith("'")) or (
            value_str.startswith('"') and value_str.endswith('"')
        ):
            # Remove quotes and unescape
            unquoted = value_str[1:-1]
            # Simple unescape (handle common cases)
            unquoted = unquoted.replace("\\'", "'").replace('\\"', '"')
            return unquoted

        # Number
        try:
            if "." in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass

        # Boolean
        if value_str.upper() in ("TRUE", "FALSE"):
            return value_str.upper() == "TRUE"

        # Return as string if nothing else matches
        return value_str

    def _parse_insert_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse an INSERT statement line.

        Args:
            line: SQL line to parse

        Returns:
            Dictionary with column values or None if not an INSERT statement
        """
        match = self.INSERT_PATTERN.search(line)
        if not match:
            return None

        table = match.group(1)
        columns_str = match.group(2)
        values_str = match.group(3)

        # Filter by table name if specified
        if self.table_name and table.lower() != self.table_name.lower():
            return None

        # Parse column names
        column_names = [col.strip() for col in columns_str.split(",")]

        # Parse values
        # Simple parsing: split by comma, but handle quoted strings
        values: List[str] = []
        current_value = ""
        in_quotes = False
        quote_char = None

        for char in values_str:
            if char in ("'", '"') and (not in_quotes or char == quote_char):
                if in_quotes and char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    in_quotes = True
                    quote_char = char
                current_value += char
            elif char == "," and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
            else:
                current_value += char

        # Add last value
        if current_value:
            values.append(current_value.strip())

        # Parse values and create row dict
        row: Dict[str, Any] = {}
        for i, col in enumerate(column_names):
            if i < len(values):
                row[col] = self._parse_value(values[i])
            else:
                row[col] = None

        return row

    def read_rows(self) -> Iterator[Dict[str, Any]]:
        """
        Read rows from the SQL dump file as dictionaries.

        Yields:
            Dictionary representing a row from INSERT statements
        """
        if self.file_handle is None:
            self.file_handle = open(self.file_path, "r", encoding=self.encoding)

        for line in self.file_handle:
            row = self._parse_insert_line(line)
            if row:
                # Determine columns from first row
                if not self._columns_determined:
                    self.columns = list(row.keys())
                    self._columns_determined = True
                yield row

    def get_columns(self) -> List[str]:
        """
        Get the list of column names.

        Returns:
            List of column names (determined from first INSERT statement)
        """
        if not self._columns_determined:
            # Read first INSERT to determine columns
            if self.file_handle is None:
                self.file_handle = open(self.file_path, "r", encoding=self.encoding)

            pos = self.file_handle.tell()
            try:
                for line in self.file_handle:
                    row = self._parse_insert_line(line)
                    if row:
                        self.columns = list(row.keys())
                        break
            except Exception:
                self.columns = []
            finally:
                self.file_handle.seek(pos)

        return self.columns.copy()

    def close(self) -> None:
        """Close the reader and release resources."""
        if self.file_handle is not None:
            self.file_handle.close()
            self.file_handle = None

