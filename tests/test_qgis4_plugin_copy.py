from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path


def test_qgis4_plugin_package_importable_without_qgis() -> None:
    import otlmow_markeringen_4  # noqa: F401


def test_qgis4_plugin_metadata_targets_qgis4() -> None:
    metadata_path = Path(__file__).resolve().parents[1] / "otlmow_markeringen_4" / "metadata.txt"

    parser = ConfigParser()
    parser.read(metadata_path, encoding="utf-8")

    assert parser.get("general", "name") == "OTLMOW Markeringen 4"
    assert parser.get("general", "qgisMinimumVersion") == "4.0"
    assert parser.get("general", "qgisMaximumVersion") == "4.99"

