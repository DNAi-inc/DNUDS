# Copyright 2025 DNAi inc.

# Dual-licensed under the DNAi Free License v1.1 and the
# DNAi Commercial License v1.1.
# See the LICENSE files in the project root for details.

"""Base classes for format readers and writers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional


class FormatReader(ABC):
    """Abstract base class for format readers."""

    @abstractmethod
    def read_rows(self) -> Iterator[Dict[str, Any]]:
        """
        Read rows from the input file as dictionaries.

        Yields:
            Dictionary representing a row, with column names as keys
        """
        pass

    @abstractmethod
    def get_columns(self) -> List[str]:
        """
        Get the list of column names.

        Returns:
            List of column names
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the reader and release resources."""
        pass

    def __enter__(self) -> "FormatReader":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


class FormatWriter(ABC):
    """Abstract base class for format writers."""

    @abstractmethod
    def write_row(self, row: Dict[str, Any]) -> None:
        """
        Write a single row to the output file.

        Args:
            row: Dictionary representing a row, with column names as keys
        """
        pass

    @abstractmethod
    def write_header(self, columns: List[str]) -> None:
        """
        Write header row with column names.

        Args:
            columns: List of column names
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the writer and flush any buffered data."""
        pass

    def __enter__(self) -> "FormatWriter":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

