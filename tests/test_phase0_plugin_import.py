from __future__ import annotations


def test_plugin_package_importable_without_qgis() -> None:
    # Importing the plugin package should not require PyQGIS.
    import otlmow_markeringen  # noqa: F401

