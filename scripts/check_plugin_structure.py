"""Minimal repo-side check for the QGIS plugin skeleton.

This script does *not* start QGIS. It just validates that the expected plugin
files exist and that the package can be imported without PyQGIS.

Run with any Python:
    python scripts/check_plugin_structure.py

Why this exists:
- Helps keep phase 0 reproducible.
- Gives a fast failure mode in CI or pre-commit.

Note: The plugin code itself imports qgis.* lazily, so importing the package
should work even outside QGIS.
"""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "otlmow_markeringen"


def main() -> int:
    # Ensure repo root is importable when running as a script.
    sys.path.insert(0, str(ROOT))

    expected = [
        PLUGIN_DIR / "__init__.py",
        PLUGIN_DIR / "metadata.txt",
        PLUGIN_DIR / "plugin.py",
    ]

    missing = [p for p in expected if not p.exists()]
    if missing:
        print("Missing expected plugin files:")
        for p in missing:
            print(f"- {p}")
        return 1

    # Import should work without qgis.* being available.
    import otlmow_markeringen  # noqa: F401

    print("Plugin skeleton looks OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
