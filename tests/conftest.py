"""Test configuration.

We keep tests as QGIS-independent as possible.

However, when running tests with a system interpreter that has PyQGIS installed
(e.g. /usr/bin/python3 on many Linux distros), we expose a small helper fixture.
"""

from __future__ import annotations

import importlib.util

import pytest


def has_pyqgis() -> bool:
    return importlib.util.find_spec("qgis") is not None


@pytest.fixture(scope="session")
def pyqgis_available() -> bool:
    """True if qgis python bindings can be imported in this interpreter."""

    return has_pyqgis()

