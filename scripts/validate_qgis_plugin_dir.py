"""Validate a QGIS plugin directory layout.

Purpose
-------
QGIS marks a plugin as "broken (no metadata file)" when it can't find a
`metadata.txt` file at the *plugin root folder level*.

This script mimics that check so you can debug Windows junction/symlink
issues without guessing.

Usage
-----
Linux/macOS:
    python scripts/validate_qgis_plugin_dir.py \
      ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/otlmow_markeringen

Windows (PowerShell):
    python scripts/validate_qgis_plugin_dir.py \
      "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\otlmow_markeringen"

Exit codes
----------
0 = OK
1 = broken layout / missing metadata.txt
2 = unexpected error
"""

from __future__ import annotations

import sys
from configparser import ConfigParser
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_qgis_plugin_dir.py <path-to-plugin-folder>")
        return 2

    plugin_dir = Path(sys.argv[1])
    print(f"Plugin dir: {plugin_dir}")
    print(f"Exists: {plugin_dir.exists()}")
    try:
        print(f"Resolved: {plugin_dir.resolve()}")
    except Exception as e:
        print(f"Resolved: <failed> ({e})")

    if not plugin_dir.exists() or not plugin_dir.is_dir():
        print("ERROR: plugin dir does not exist or is not a directory")
        return 1

    metadata = plugin_dir / "metadata.txt"
    print(f"metadata.txt exists: {metadata.exists()}")
    print(f"metadata.txt is file: {metadata.is_file()}")
    if metadata.exists():
        try:
            data = metadata.read_text(encoding="utf-8", errors="replace")
            print("metadata.txt first lines:")
            for i, line in enumerate(data.splitlines()[:10], start=1):
                print(f"{i:02d}: {line}")
        except Exception as e:
            print(f"ERROR: couldn't read metadata.txt ({e})")
            return 1

    if not metadata.exists():
        # Common mistake: nested folder
        nested = plugin_dir / plugin_dir.name / "metadata.txt"
        if nested.exists():
            print("HINT: Found nested metadata at:")
            print(f"  {nested}")
            print("QGIS expects metadata.txt directly inside the plugin folder.")
        return 1

    # Parse minimum sections/keys
    parser = ConfigParser()
    try:
        parser.read(metadata, encoding="utf-8")
    except Exception:
        # Some python versions don't have encoding param; fallback.
        parser.read(metadata)

    if "general" not in parser:
        print("ERROR: [general] section missing")
        return 1

    required_keys = ["name", "qgisMinimumVersion", "version", "description"]
    missing = [k for k in required_keys if k not in parser["general"]]
    if missing:
        print(f"ERROR: missing keys in [general]: {', '.join(missing)}")
        return 1

    if "title" not in parser["general"]:
        print("NOTE: optional key [general].title is missing (usually not fatal).")

    print("OK: plugin folder contains a readable metadata.txt at root.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise SystemExit(2)
