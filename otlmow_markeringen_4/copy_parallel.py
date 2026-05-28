from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CopyParallelCandidate:
    """Minimal selection payload used to validate copy-parallel preconditions."""

    source_fid: int
    is_line: bool
    is_multipart: bool


@dataclass(frozen=True)
class CopyParallelSelectionResult:
    """Result of validating copy-parallel selection rules."""

    selected: CopyParallelCandidate | None
    error_message: str | None


def validate_copy_parallel_selection(
    candidates: list[CopyParallelCandidate],
) -> CopyParallelSelectionResult:
    """Enforce exactly one selected single-part line for copy-parallel mode."""

    if not candidates:
        return CopyParallelSelectionResult(
            selected=None,
            error_message="Selecteer exact 1 lijnfeature voor Copy parallel.",
        )

    if len(candidates) != 1:
        return CopyParallelSelectionResult(
            selected=None,
            error_message="Copy parallel vereist exact 1 geselecteerde feature.",
        )

    candidate = candidates[0]
    if not candidate.is_line:
        return CopyParallelSelectionResult(
            selected=None,
            error_message="De geselecteerde feature is geen lijn.",
        )

    if candidate.is_multipart:
        return CopyParallelSelectionResult(
            selected=None,
            error_message="Copy parallel ondersteunt enkel single-part lijnen.",
        )

    return CopyParallelSelectionResult(selected=candidate, error_message=None)

