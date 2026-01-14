from __future__ import annotations

from pathlib import Path


def test_validate_script_find_metadata_in_repo_plugin_dir(tmp_path) -> None:
    # We validate against the repo plugin folder itself.
    plugin_dir = Path(__file__).resolve().parents[1] / "otlmow_markeringen"
    assert (plugin_dir / "metadata.txt").exists()

