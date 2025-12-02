# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""CSV format writer."""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from dnuds.formats.base import FormatWriter


class CSVWriter(FormatWriter):
    """Streaming CSV writer."""

    def __init__(
        self,
        file_path: str,
        columns: Optional[List[str]] = None,
        delimiter: str = ",",
        quotechar: str = '"',
        write_header: bool = True,
        encoding: str = "utf-8",
    ):
        """
        Initialize CSV writer.

        Args:
            file_path: Path to the output CSV file
            columns: List of column names (required if write_header is True)
            delimiter: CSV delimiter (default: comma)
            quotechar: Quote character (default: double quote)
            write_header: Whether to write header row (default: True)
            encoding: File encoding (default: utf-8)
        """
        self.file_path = file_path
        self.columns = columns or []
        self.delimiter = delimiter
        self.quotechar = quotechar
        # Flag controlling whether a header row should be written.
        # Use a different attribute name to avoid clashing with the write_header method.
        self._write_header_flag = write_header
        self.encoding = encoding
        self.file_handle: Optional[Any] = None
        self.writer: Optional[Any] = None
        self._header_written = False

    def _open(self) -> None:
        """Open the file and initialize the CSV writer."""
        if self.file_handle is not None:
            return

        # Create parent directory if needed
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)

        self.file_handle = open(
            self.file_path, "w", encoding=self.encoding, newline=""
        )
        self.writer = csv.DictWriter(
            self.file_handle,
            fieldnames=self.columns,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            extrasaction="ignore",  # Ignore extra keys not in columns
        )

    def write_header(self, columns: List[str]) -> None:
        """
        Write header row with column names.

        Args:
            columns: List of column names
        """
        self._open()

        # Update columns if not set
        if not self.columns:
            self.columns = columns
            self.writer = csv.DictWriter(
                self.file_handle,
                fieldnames=self.columns,
                delimiter=self.delimiter,
                quotechar=self.quotechar,
                extrasaction="ignore",
            )

        if self._write_header_flag and not self._header_written:
            self.writer.writeheader()
            self._header_written = True

    def write_row(self, row: Dict[str, Any]) -> None:
        """
        Write a single row to the CSV file.

        Args:
            row: Dictionary representing a row, with column names as keys
        """
        self._open()

        # Write header if needed and columns are available
        if self._write_header_flag and not self._header_written:
            if self.columns:
                self.writer.writeheader()
                self._header_written = True
            elif row:
                # Infer columns from first row
                self.columns = list(row.keys())
                self.writer = csv.DictWriter(
                    self.file_handle,
                    fieldnames=self.columns,
                    delimiter=self.delimiter,
                    quotechar=self.quotechar,
                    extrasaction="ignore",
                )
                self.writer.writeheader()
                self._header_written = True

        self.writer.writerow(row)

    def close(self) -> None:
        """Close the writer and flush any buffered data."""
        if self.file_handle is not None:
            self.file_handle.flush()
            self.file_handle.close()
            self.file_handle = None
            self.writer = None

