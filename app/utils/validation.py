"""User input validation before agent execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.utils.config import get_config


SUPPORTED_EXTENSION = ".py"


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating uploaded or pasted source code."""

    is_valid: bool
    file_name: str
    source_code: str
    errors: list[str]


def validate_review_input(
    source_code: Optional[str],
    file_name: Optional[str] = None,
    file_size_bytes: Optional[int] = None,
) -> ValidationResult:
    """Validate code, file name, type, and size limits."""

    config = get_config()
    cleaned_code = source_code or ""
    cleaned_file_name = (file_name or "pasted_code.py").strip()
    normalized_file_name = cleaned_file_name.lower()
    errors: list[str] = []

    if not cleaned_file_name:
        errors.append("Missing file name.")

    if not normalized_file_name.endswith(SUPPORTED_EXTENSION):
        errors.append("Only Python .py files are supported.")

    if not cleaned_code.strip():
        errors.append("Source code cannot be empty.")

    if "\x00" in cleaned_code:
        errors.append("Source code appears to contain binary data and cannot be reviewed.")

    if "\ufffd" in cleaned_code:
        errors.append("Source code contains characters that could not be decoded as UTF-8.")

    encoded_size = len(cleaned_code.encode("utf-8"))
    measured_size = file_size_bytes if file_size_bytes is not None else encoded_size
    if measured_size > config.max_file_size_bytes:
        errors.append(
            f"File is too large. Limit is {config.max_file_size_bytes // 1000} KB."
        )

    return ValidationResult(
        is_valid=not errors,
        file_name=cleaned_file_name,
        source_code=cleaned_code,
        errors=errors,
    )
