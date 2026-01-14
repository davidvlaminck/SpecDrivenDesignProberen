"""OTLMOW Markeringen QGIS plugin.

Fase 0: minimaal plugin-skelet dat in QGIS kan laden, een toolbar-knop toont,
en een melding/logging doet.

QGIS detecteert plugins via een package folder met `metadata.txt` en een
`classFactory(iface)` functie.
"""

from __future__ import annotations


def classFactory(iface):  # noqa: N802 (QGIS requires this exact name)
    """Instantiates the plugin (called by QGIS at load time)."""

    from .plugin import OTLMOWMarkeringenPlugin

    return OTLMOWMarkeringenPlugin(iface)
