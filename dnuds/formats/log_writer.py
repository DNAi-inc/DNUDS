# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Line-based log format writer."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from dnuds.formats.base import FormatWriter


class LogWriter(FormatWriter):
    """Streaming log writer that writes one line per row."""

    def __init__(
        self,
        file_path: str,
        encoding: str = "utf-8",
        message_column: str = "message",
        format_template: Optional[str] = None,
    ):
        """
        Initialize log writer.

        Args:
            file_path: Path to the output log file
            encoding: File encoding (default: utf-8)
            message_column: Column name to use as message (default: message)
            format_template: Optional format template (e.g., "[{level}] {message}")
        """
        self.file_path = file_path
        self.encoding = encoding
        self.message_column = message_column
        self.format_template = format_template
        self.file_handle: Optional[Any] = None

    def _open(self) -> None:
        """Open the file for writing."""
        if self.file_handle is not None:
            return

        # Create parent directory if needed
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)

        self.file_handle = open(self.file_path, "w", encoding=self.encoding)

    def write_header(self, columns: List[str]) -> None:
        """
        Write header row with column names.

        Note: Logs don't have headers, so this is a no-op.
        We keep it for interface compatibility.

        Args:
            columns: List of column names (ignored for logs)
        """
        self._open()
        # Logs don't have headers, so we do nothing
        pass

    def write_row(self, row: Dict[str, Any]) -> None:
        """
        Write a single row to the log file.

        Args:
            row: Dictionary representing a log entry
        """
        self._open()

        if self.format_template:
            # Use format template
            try:
                line = self.format_template.format(**row)
            except KeyError:
                # Fallback to message column if template fails
                line = str(row.get(self.message_column, ""))
        else:
            # Default: use message column or first column
            line = str(row.get(self.message_column, row.get(list(row.keys())[0] if row else "", "")))

        self.file_handle.write(line)
        self.file_handle.write("\n")

    def close(self) -> None:
        """Close the writer and flush any buffered data."""
        if self.file_handle is not None:
            self.file_handle.flush()
            self.file_handle.close()
            self.file_handle = None

