# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""JSONL (JSON Lines) format writer."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from dnuds.formats.base import FormatWriter


class JSONLWriter(FormatWriter):
    """Streaming JSONL writer that writes one JSON object per line."""

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        """
        Initialize JSONL writer.

        Args:
            file_path: Path to the output JSONL file
            encoding: File encoding (default: utf-8)
        """
        self.file_path = file_path
        self.encoding = encoding
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

        Note: JSONL doesn't have headers, so this is a no-op.
        We keep it for interface compatibility.

        Args:
            columns: List of column names (ignored for JSONL)
        """
        self._open()
        # JSONL doesn't have headers, so we do nothing
        pass

    def write_row(self, row: Dict[str, Any]) -> None:
        """
        Write a single row to the JSONL file.

        Args:
            row: Dictionary representing a row
        """
        self._open()

        # Write row as JSON on a single line
        json_line = json.dumps(row, ensure_ascii=False)
        self.file_handle.write(json_line)
        self.file_handle.write("\n")

    def close(self) -> None:
        """Close the writer and flush any buffered data."""
        if self.file_handle is not None:
            self.file_handle.flush()
            self.file_handle.close()
            self.file_handle = None

