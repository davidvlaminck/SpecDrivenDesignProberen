from __future__ import annotations

from datetime import datetime, timezone


def test_validate_import_candidates_filters_not_line_and_multipart() -> None:
    from otlmow_markeringen.import_selected import ImportCandidate, validate_import_candidates

    candidates = [
        ImportCandidate(
            source_layer="bron",
            source_fid=1,
            is_line=True,
            is_multipart=False,
            attributes={},
        ),
        ImportCandidate(
            source_layer="bron",
            source_fid=2,
            is_line=False,
            is_multipart=False,
            attributes={},
        ),
        ImportCandidate(
            source_layer="bron",
            source_fid=3,
            is_line=True,
            is_multipart=True,
            attributes={},
        ),
    ]

    result = validate_import_candidates(candidates)

    assert [candidate.source_fid for candidate in result.accepted] == [1]
    assert result.skipped_not_line == 1
    assert result.skipped_multipart == 1


def test_build_managed_attributes_applies_defaults_and_keeps_source_values() -> None:
    from otlmow_markeringen.import_selected import build_managed_attributes

    created_at = datetime(2026, 5, 18, 8, 0, tzinfo=timezone.utc)

    result = build_managed_attributes(
        source_layer="bronlaag",
        source_fid=42,
        source_attributes={"status": "validated", "color": "#ff0000", "comment": None},
        created_at=created_at,
    )

    assert result["source_layer"] == "bronlaag"
    assert result["source_fid"] == 42
    assert result["created_at"] == "2026-05-18T08:00:00+00:00"

    assert result["status"] == "validated"
    assert result["color"] == "#ff0000"

    assert result["position"] == "onbekend"
    assert result["type"] == "onbekend"
    assert result["coprocode"] == ""
    assert result["created_by"] == "plugin"
    assert result["comment"] == ""
    assert result["geometry_length_m"] is None


