# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""SQL dump format writer for INSERT statements."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from dnuds.formats.base import FormatWriter


class SQLWriter(FormatWriter):
    """Streaming SQL writer that writes INSERT statements."""

    def __init__(
        self,
        file_path: str,
        table_name: str = "data",
        encoding: str = "utf-8",
    ):
        """
        Initialize SQL writer.

        Args:
            file_path: Path to the output SQL file
            table_name: Name of the table for INSERT statements
            encoding: File encoding (default: utf-8)
        """
        self.file_path = file_path
        self.table_name = table_name
        self.encoding = encoding
        self.file_handle: Optional[Any] = None
        self.columns: Optional[List[str]] = None

    def _open(self) -> None:
        """Open the file for writing."""
        if self.file_handle is not None:
            return

        # Create parent directory if needed
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)

        self.file_handle = open(self.file_path, "w", encoding=self.encoding)

    def _escape_sql_value(self, value: Any) -> str:
        """
        Escape a value for SQL.

        Args:
            value: Value to escape

        Returns:
            SQL-safe string representation
        """
        if value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            # String: escape quotes and wrap in single quotes
            value_str = str(value)
            value_str = value_str.replace("'", "''")  # Escape single quotes
            return f"'{value_str}'"

    def write_header(self, columns: List[str]) -> None:
        """
        Write header (no-op for SQL, columns determined from first row).

        Args:
            columns: List of column names
        """
        self._open()
        self.columns = columns

    def write_row(self, row: Dict[str, Any]) -> None:
        """
        Write a single row as an INSERT statement.

        Args:
            row: Dictionary representing a row
        """
        self._open()

        # Determine columns from first row if not set
        if self.columns is None:
            self.columns = list(row.keys())

        # Build column list
        columns_str = ", ".join(self.columns)

        # Build values list
        values = [self._escape_sql_value(row.get(col)) for col in self.columns]
        values_str = ", ".join(values)

        # Write INSERT statement
        insert_stmt = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({values_str});\n"
        self.file_handle.write(insert_stmt)

    def close(self) -> None:
        """Close the writer and flush any buffered data."""
        if self.file_handle is not None:
            self.file_handle.flush()
            self.file_handle.close()
            self.file_handle = None

