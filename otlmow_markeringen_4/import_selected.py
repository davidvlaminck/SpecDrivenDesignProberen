from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

MANAGED_LAYER_NAME = "OTLMOW Markeringen"


@dataclass(frozen=True)
class ImportCandidate:
    """Normalized selection item that can be validated before import."""

    source_layer: str
    source_fid: int
    is_line: bool
    is_multipart: bool
    attributes: dict[str, Any]


@dataclass(frozen=True)
class ImportValidationResult:
    """Validation outcome for a batch of selected source features."""

    accepted: list[ImportCandidate]
    skipped_not_line: int
    skipped_multipart: int


DEFAULT_ATTRIBUTE_VALUES: dict[str, Any] = {
    "position": "onbekend",
    "type": "onbekend",
    "coprocode": "",
    "color": "",
    "status": "draft",
    "created_by": "plugin",
    "comment": "",
}


def validate_import_candidates(candidates: list[ImportCandidate]) -> ImportValidationResult:
    """Filter out non-line and multi-part selections before import."""

    accepted: list[ImportCandidate] = []
    skipped_not_line = 0
    skipped_multipart = 0

    for candidate in candidates:
        if not candidate.is_line:
            skipped_not_line += 1
            continue
        if candidate.is_multipart:
            skipped_multipart += 1
            continue
        accepted.append(candidate)

    return ImportValidationResult(
        accepted=accepted,
        skipped_not_line=skipped_not_line,
        skipped_multipart=skipped_multipart,
    )


def build_managed_attributes(
    *, source_layer: str, source_fid: int, source_attributes: dict[str, Any], created_at: datetime | None = None
) -> dict[str, Any]:
    """Build the managed-layer attribute payload with plugin defaults and metadata."""

    timestamp = created_at or datetime.now(timezone.utc)

    result = {
        "source_layer": source_layer,
        "source_fid": source_fid,
        "created_at": timestamp.isoformat(),
    }

    for field_name, default_value in DEFAULT_ATTRIBUTE_VALUES.items():
        value = source_attributes.get(field_name, default_value)
        result[field_name] = default_value if value is None else value

    # This field is calculated from geometry during import.
    result["geometry_length_m"] = None
    return result


