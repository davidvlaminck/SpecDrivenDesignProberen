"""OTLMOW Markeringen QGIS 4 plugin.

Deze package is de QGIS 4.x-variant van de plugin in `otlmow_markeringen`.
Ze bevat momenteel dezelfde code en functionaliteit, maar met metadata gericht op
QGIS 4.x.

QGIS detecteert plugins via een package folder met `metadata.txt` en een
`classFactory(iface)` functie.
"""

from __future__ import annotations


def classFactory(iface):  # noqa: N802 (QGIS requires this exact name)
    """Instantiates the plugin (called by QGIS at load time)."""

    from .plugin import OTLMOWMarkeringenPlugin

    return OTLMOWMarkeringenPlugin(iface)
