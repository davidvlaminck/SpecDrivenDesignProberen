from __future__ import annotations


def test_validate_copy_parallel_selection_requires_exactly_one_feature() -> None:
    from otlmow_markeringen.copy_parallel import validate_copy_parallel_selection

    no_selection = validate_copy_parallel_selection([])
    assert no_selection.selected is None
    assert no_selection.error_message is not None

    from otlmow_markeringen.copy_parallel import CopyParallelCandidate

    multi_selection = validate_copy_parallel_selection(
        [
            CopyParallelCandidate(source_fid=1, is_line=True, is_multipart=False),
            CopyParallelCandidate(source_fid=2, is_line=True, is_multipart=False),
        ]
    )
    assert multi_selection.selected is None
    assert "exact 1" in str(multi_selection.error_message)


def test_validate_copy_parallel_selection_rejects_non_line_and_multipart() -> None:
    from otlmow_markeringen.copy_parallel import (
        CopyParallelCandidate,
        validate_copy_parallel_selection,
    )

    not_line = validate_copy_parallel_selection(
        [CopyParallelCandidate(source_fid=1, is_line=False, is_multipart=False)]
    )
    assert not_line.selected is None
    assert "geen lijn" in str(not_line.error_message)

    multipart = validate_copy_parallel_selection(
        [CopyParallelCandidate(source_fid=1, is_line=True, is_multipart=True)]
    )
    assert multipart.selected is None
    assert "single-part" in str(multipart.error_message)


def test_validate_copy_parallel_selection_accepts_single_part_line() -> None:
    from otlmow_markeringen.copy_parallel import (
        CopyParallelCandidate,
        validate_copy_parallel_selection,
    )

    result = validate_copy_parallel_selection(
        [CopyParallelCandidate(source_fid=99, is_line=True, is_multipart=False)]
    )

    assert result.error_message is None
    assert result.selected is not None
    assert result.selected.source_fid == 99


def test_qgis4_copy_parallel_module_is_importable() -> None:
    from otlmow_markeringen_4.copy_parallel import CopyParallelCandidate, validate_copy_parallel_selection

    result = validate_copy_parallel_selection(
        [CopyParallelCandidate(source_fid=5, is_line=True, is_multipart=False)]
    )
    assert result.error_message is None

