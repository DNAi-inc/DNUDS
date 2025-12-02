# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""CSV format reader with auto-detection."""

import csv
import io
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from dnuds.formats.base import FormatReader


class CSVReader(FormatReader):
    """
    Streaming CSV reader with automatic delimiter and quote detection.

    Supports header detection and various CSV dialects.
    """

    def __init__(
        self,
        file_path: str,
        delimiter: Optional[str] = None,
        quotechar: Optional[str] = None,
        has_header: Optional[bool] = None,
        encoding: str = "utf-8",
    ):
        """
        Initialize CSV reader.

        Args:
            file_path: Path to the CSV file
            delimiter: CSV delimiter (auto-detected if None)
            quotechar: Quote character (auto-detected if None)
            has_header: Whether file has header row (auto-detected if None)
            encoding: File encoding (default: utf-8)
        """
        self.file_path = file_path
        self.file_handle: Optional[Any] = None
        self.reader: Optional[Any] = None
        self.columns: List[str] = []
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.has_header = has_header
        self.encoding = encoding
        self._opened = False

    def _detect_dialect(self) -> csv.Dialect:
        """
        Detect CSV dialect from file content.

        Returns:
            Detected CSV dialect
        """
        # Read first few lines to detect dialect
        with open(self.file_path, "r", encoding=self.encoding, newline="") as f:
            sample = f.read(8192)  # Read first 8KB
            sniffer = csv.Sniffer()
            try:
                dialect = sniffer.sniff(sample, delimiters=",\t;|")
                return dialect
            except csv.Error:
                # Fallback to default
                return csv.excel

    def _detect_header(self) -> bool:
        """
        Detect if file has a header row.

        Returns:
            True if header detected, False otherwise
        """
        with open(self.file_path, "r", encoding=self.encoding, newline="") as f:
            sample = f.read(8192)
            sniffer = csv.Sniffer()
            try:
                return sniffer.has_header(sample)
            except csv.Error:
                # Default to True if detection fails
                return True

    def _open(self) -> None:
        """Open the file and initialize the CSV reader."""
        if self._opened:
            return

        self.file_handle = open(
            self.file_path, "r", encoding=self.encoding, newline=""
        )

        # Detect dialect if not provided
        if self.delimiter is None or self.quotechar is None:
            dialect = self._detect_dialect()
            if self.delimiter is None:
                self.delimiter = dialect.delimiter
            if self.quotechar is None:
                self.quotechar = dialect.quotechar

        # Detect header if not provided
        if self.has_header is None:
            self.has_header = self._detect_header()

        # Create CSV reader
        self.reader = csv.DictReader(
            self.file_handle,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
        )

        # Get column names
        if self.has_header and self.reader.fieldnames:
            self.columns = list(self.reader.fieldnames)
        else:
            # If no header, we need to read first row to determine columns
            # This is a limitation - we'll use generic column names
            if not self.has_header:
                # Try to read first row to get column count
                pos = self.file_handle.tell()
                first_line = self.file_handle.readline()
                self.file_handle.seek(pos)
                reader = csv.reader(
                    io.StringIO(first_line),
                    delimiter=self.delimiter,
                    quotechar=self.quotechar,
                )
                first_row = next(reader)
                self.columns = [f"column_{i}" for i in range(len(first_row))]
                # Recreate reader without header
                self.file_handle.seek(0)
                self.reader = csv.reader(
                    self.file_handle,
                    delimiter=self.delimiter,
                    quotechar=self.quotechar,
                )

        self._opened = True

    def read_rows(self) -> Iterator[Dict[str, Any]]:
        """
        Read rows from the CSV file as dictionaries.

        Yields:
            Dictionary representing a row, with column names as keys
        """
        self._open()

        if self.has_header:
            # Use DictReader which handles headers
            for row in self.reader:
                yield dict(row)
        else:
            # Manual reading without header
            for row in self.reader:
                yield {col: val for col, val in zip(self.columns, row)}

    def get_columns(self) -> List[str]:
        """
        Get the list of column names.

        Returns:
            List of column names
        """
        self._open()
        return self.columns.copy()

    def close(self) -> None:
        """Close the reader and release resources."""
        if self.file_handle is not None:
            self.file_handle.close()
            self.file_handle = None
            self.reader = None
            self._opened = False

