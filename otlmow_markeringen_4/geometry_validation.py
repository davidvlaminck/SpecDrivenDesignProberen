from __future__ import annotations

from dataclasses import dataclass


MIN_GEOMETRY_LENGTH_M = 1.0


@dataclass(frozen=True)
class GeometryValidationResult:
    """Validation outcome for a source or generated line geometry."""

    is_valid: bool
    error_code: str | None
    message: str | None


def validate_source_geometry_for_copy_parallel(
    *,
    is_empty: bool,
    is_geos_valid: bool,
    is_simple: bool,
) -> GeometryValidationResult:
    """Validate source geometry constraints before parallel creation."""

    if is_empty:
        return GeometryValidationResult(
            is_valid=False,
            error_code="SOURCE_EMPTY",
            message="De bronlijn heeft geen bruikbare geometrie.",
        )

    if not is_geos_valid:
        return GeometryValidationResult(
            is_valid=False,
            error_code="SOURCE_INVALID",
            message="De bronlijn is geometrisch ongeldig. Corrigeer de brongeometrie en probeer opnieuw.",
        )

    if not is_simple:
        return GeometryValidationResult(
            is_valid=False,
            error_code="SOURCE_NOT_SIMPLE",
            message="De bronlijn heeft self-intersections en kan niet gebruikt worden voor Copy parallel.",
        )

    return GeometryValidationResult(is_valid=True, error_code=None, message=None)


def validate_offset_geometry_for_copy_parallel(
    *,
    is_empty: bool,
    is_geos_valid: bool,
    is_simple: bool,
    length_m: float,
    minimum_length_m: float = MIN_GEOMETRY_LENGTH_M,
) -> GeometryValidationResult:
    """Validate generated offset geometry against phase-3 constraints."""

    if is_empty:
        return GeometryValidationResult(
            is_valid=False,
            error_code="OFFSET_EMPTY",
            message="Kon geen parallelle lijn berekenen voor dit klikpunt.",
        )

    if not is_geos_valid:
        return GeometryValidationResult(
            is_valid=False,
            error_code="OFFSET_INVALID",
            message="De berekende parallelle lijn is ongeldig. Probeer een ander klikpunt.",
        )

    if not is_simple:
        return GeometryValidationResult(
            is_valid=False,
            error_code="OFFSET_NOT_SIMPLE",
            message="De berekende parallelle lijn heeft self-intersections. Probeer een ander klikpunt.",
        )

    if length_m < minimum_length_m:
        return GeometryValidationResult(
            is_valid=False,
            error_code="OFFSET_TOO_SHORT",
            message=f"Berekende lijn is korter dan {minimum_length_m:.1f} m en wordt niet toegevoegd.",
        )

    return GeometryValidationResult(is_valid=True, error_code=None, message=None)

