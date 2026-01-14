"""Small smoke test for PyQGIS imports.

Run with the system interpreter that ships with/targets your QGIS installation, e.g.:
    /usr/bin/python3 scripts/check_pyqgis.py

This is intentionally not a full QGIS init (QgsApplication) yet; it's just for IDE/interpreter validation.
"""

from __future__ import annotations

import importlib.util


def main() -> int:
    mods = ["qgis", "qgis.core", "qgis.gui", "osgeo", "PyQt5"]
    for m in mods:
        spec = importlib.util.find_spec(m)
        print(f"{m}: {'OK' if spec else 'MISSING'}")

    # Hard fail if base qgis module isn't importable.
    if importlib.util.find_spec("qgis") is None:
        return 1

    print("\nPyQGIS import path looks OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
