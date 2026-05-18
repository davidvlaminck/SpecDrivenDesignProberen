from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .import_selected import (
    MANAGED_LAYER_NAME,
    ImportCandidate,
    build_managed_attributes,
    validate_import_candidates,
)


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
    """QGIS plugin implementation with phase 1 import flow."""

    def __init__(self, iface):
        self.iface = iface
        self._import_action: Optional[object] = None

    def initGui(self) -> None:  # QGIS naming
        QAction, QIcon, QCoreApplication, QgsMessageLog, Qgis = _safe_import_qgis()

        text = QCoreApplication.translate("OTLMOWMarkeringen", "OTLMOW: Import selected")
        self._import_action = QAction(QIcon(), text, self.iface.mainWindow())
        self._import_action.setToolTip(text)
        self._import_action.triggered.connect(self._on_import_selected)

        self.iface.addToolBarIcon(self._import_action)
        self.iface.addPluginToMenu("OTLMOW Markeringen", self._import_action)

        QgsMessageLog.logMessage("Plugin GUI initialized", "OTLMOW Markeringen", Qgis.Info)

    def unload(self) -> None:
        if not self._import_action:
            return

        _QAction, _QIcon, _QCoreApplication, QgsMessageLog, Qgis = _safe_import_qgis()

        self.iface.removeToolBarIcon(self._import_action)
        self.iface.removePluginMenu("OTLMOW Markeringen", self._import_action)
        QgsMessageLog.logMessage("Plugin unloaded", "OTLMOW Markeringen", Qgis.Info)

        self._import_action = None

    def _on_import_selected(self) -> None:
        """Import the current selection into the managed plugin layer."""

        from qgis.core import Qgis, QgsMessageLog

        source_layer = self.iface.activeLayer()
        if source_layer is None:
            self._notify(
                "Geen actieve laag. Selecteer eerst een lijnlaag.",
                Qgis.Warning,
            )
            return

        selected_features = source_layer.selectedFeatures()
        if not selected_features:
            self._notify("Geen geselecteerde features om te importeren.", Qgis.Warning)
            return

        source_field_names = [field.name() for field in source_layer.fields()]

        candidates: list[ImportCandidate] = []
        skipped_missing_geometry = 0

        for feature in selected_features:
            geometry = feature.geometry()
            if geometry is None or geometry.isEmpty():
                skipped_missing_geometry += 1
                continue

            candidates.append(
                ImportCandidate(
                    source_layer=source_layer.name(),
                    source_fid=int(feature.id()),
                    is_line=geometry.type() == 1,
                    is_multipart=geometry.isMultipart(),
                    attributes=dict(zip(source_field_names, feature.attributes())),
                )
            )

        validation = validate_import_candidates(candidates)
        if not validation.accepted:
            self._notify(
                "Geen geldige single-part lijnen geselecteerd voor import.",
                Qgis.Warning,
            )
            return

        managed_layer = self._ensure_managed_layer(source_layer)
        provider = managed_layer.dataProvider()
        field_names = [field.name() for field in managed_layer.fields()]

        from qgis.core import QgsFeature

        imported = 0
        now = datetime.now(timezone.utc)
        for candidate in validation.accepted:
            source_feature = source_layer.getFeature(candidate.source_fid)
            if not source_feature.isValid():
                continue

            mapped_attributes = build_managed_attributes(
                source_layer=candidate.source_layer,
                source_fid=candidate.source_fid,
                source_attributes=candidate.attributes,
                created_at=now,
            )
            mapped_attributes["geometry_length_m"] = source_feature.geometry().length()

            new_feature = QgsFeature(managed_layer.fields())
            new_feature.setGeometry(source_feature.geometry())
            for name in field_names:
                if name in mapped_attributes:
                    new_feature[name] = mapped_attributes[name]

            if provider.addFeatures([new_feature]):
                imported += 1

        managed_layer.updateExtents()
        managed_layer.triggerRepaint()

        summary = (
            f"Import selected afgerond: {imported} geimporteerd, "
            f"{validation.skipped_multipart} multipart overgeslagen, "
            f"{validation.skipped_not_line + skipped_missing_geometry} ongeldig."
        )
        self._notify(summary, Qgis.Info)
        QgsMessageLog.logMessage(summary, "OTLMOW Markeringen", Qgis.Info)

    def _ensure_managed_layer(self, source_layer):
        """Return the existing managed layer or create it with the Phase 1 schema."""

        from qgis.core import (
            QgsField,
            QgsProject,
            QgsVectorLayer,
        )
        from qgis.PyQt.QtCore import QVariant

        project = QgsProject.instance()
        existing_layers = project.mapLayersByName(MANAGED_LAYER_NAME)
        if existing_layers:
            return existing_layers[0]

        crs_authid = source_layer.crs().authid() or "EPSG:31370"
        managed_layer = QgsVectorLayer(
            f"LineString?crs={crs_authid}",
            MANAGED_LAYER_NAME,
            "memory",
        )

        provider = managed_layer.dataProvider()
        provider.addAttributes(
            [
                QgsField("source_layer", QVariant.String),
                QgsField("source_fid", QVariant.LongLong),
                QgsField("geometry_length_m", QVariant.Double),
                QgsField("position", QVariant.String),
                QgsField("type", QVariant.String),
                QgsField("coprocode", QVariant.String),
                QgsField("color", QVariant.String),
                QgsField("status", QVariant.String),
                QgsField("created_by", QVariant.String),
                QgsField("created_at", QVariant.String),
                QgsField("comment", QVariant.String),
            ]
        )
        managed_layer.updateFields()
        project.addMapLayer(managed_layer)
        return managed_layer

    def _notify(self, message: str, level) -> None:
        """Send a best-effort user-facing message through the QGIS message bar."""

        try:
            self.iface.messageBar().pushMessage("OTLMOW Markeringen", message, level=level)
        except Exception:
            pass


