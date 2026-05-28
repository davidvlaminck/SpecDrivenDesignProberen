from __future__ import annotations


def test_validate_source_geometry_rejects_invalid_and_self_intersection() -> None:
    from otlmow_markeringen.geometry_validation import validate_source_geometry_for_copy_parallel

    invalid = validate_source_geometry_for_copy_parallel(
        is_empty=False,
        is_geos_valid=False,
        is_simple=True,
    )
    assert invalid.is_valid is False
    assert invalid.error_code == "SOURCE_INVALID"

    not_simple = validate_source_geometry_for_copy_parallel(
        is_empty=False,
        is_geos_valid=True,
        is_simple=False,
    )
    assert not_simple.is_valid is False
    assert not_simple.error_code == "SOURCE_NOT_SIMPLE"


def test_validate_offset_geometry_rejects_invalid_short_and_self_intersections() -> None:
    from otlmow_markeringen.geometry_validation import validate_offset_geometry_for_copy_parallel

    invalid = validate_offset_geometry_for_copy_parallel(
        is_empty=False,
        is_geos_valid=False,
        is_simple=True,
        length_m=10.0,
    )
    assert invalid.is_valid is False
    assert invalid.error_code == "OFFSET_INVALID"

    not_simple = validate_offset_geometry_for_copy_parallel(
        is_empty=False,
        is_geos_valid=True,
        is_simple=False,
        length_m=10.0,
    )
    assert not_simple.is_valid is False
    assert not_simple.error_code == "OFFSET_NOT_SIMPLE"

    too_short = validate_offset_geometry_for_copy_parallel(
        is_empty=False,
        is_geos_valid=True,
        is_simple=True,
        length_m=0.9,
    )
    assert too_short.is_valid is False
    assert too_short.error_code == "OFFSET_TOO_SHORT"


def test_validate_offset_geometry_accepts_valid_line() -> None:
    from otlmow_markeringen.geometry_validation import validate_offset_geometry_for_copy_parallel

    ok = validate_offset_geometry_for_copy_parallel(
        is_empty=False,
        is_geos_valid=True,
        is_simple=True,
        length_m=1.0,
    )

    assert ok.is_valid is True
    assert ok.error_code is None


def test_qgis4_geometry_validation_module_is_importable() -> None:
    from otlmow_markeringen_4.geometry_validation import validate_offset_geometry_for_copy_parallel

    result = validate_offset_geometry_for_copy_parallel(
        is_empty=False,
        is_geos_valid=True,
        is_simple=True,
        length_m=2.5,
    )
    assert result.is_valid is True

