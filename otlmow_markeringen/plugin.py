from __future__ import annotations

from typing import Optional


def _safe_import_qgis():
    """Import QGIS/PyQt modules lazily.

    This keeps the module importable in non-QGIS contexts (unit tests, linters)
    while still working normally inside QGIS.
    """

    from qgis.core import Qgis, QgsMessageLog
    from qgis.PyQt.QtCore import QCoreApplication
    from qgis.PyQt.QtGui import QIcon
    from qgis.PyQt.QtWidgets import QAction

    return QAction, QIcon, QCoreApplication, QgsMessageLog, Qgis


class OTLMOWMarkeringenPlugin:
    """Minimal QGIS plugin implementation (phase 0)."""

    def __init__(self, iface):
        self.iface = iface
        self._action: Optional[object] = None

    def initGui(self) -> None:  # QGIS naming
        QAction, QIcon, QCoreApplication, QgsMessageLog, Qgis = _safe_import_qgis()

        text = QCoreApplication.translate("OTLMOWMarkeringen", "OTLMOW: Plugin loaded")
        self._action = QAction(QIcon(), text, self.iface.mainWindow())
        self._action.setToolTip(text)
        self._action.triggered.connect(self._on_action_triggered)

        self.iface.addToolBarIcon(self._action)
        self.iface.addPluginToMenu("OTLMOW Markeringen", self._action)

        QgsMessageLog.logMessage("Plugin GUI initialized", "OTLMOW Markeringen", Qgis.Info)

    def unload(self) -> None:
        if not self._action:
            return

        QAction, _QIcon, _QCoreApplication, QgsMessageLog, Qgis = _safe_import_qgis()

        self.iface.removeToolBarIcon(self._action)
        self.iface.removePluginMenu("OTLMOW Markeringen", self._action)
        QgsMessageLog.logMessage("Plugin unloaded", "OTLMOW Markeringen", Qgis.Info)

        self._action = None

    def _on_action_triggered(self) -> None:
        QAction, _QIcon, QCoreApplication, QgsMessageLog, Qgis = _safe_import_qgis()

        msg = QCoreApplication.translate(
            "OTLMOWMarkeringen",
            "OTLMOW Markeringen: plugin loaded and action works.",
        )

        # Show a message in QGIS UI (message bar)
        try:
            self.iface.messageBar().pushInfo("OTLMOW Markeringen", msg)
        except Exception:
            # Some interfaces in tests/mocks might not have a messageBar.
            pass

        QgsMessageLog.logMessage(msg, "OTLMOW Markeringen", Qgis.Info)

