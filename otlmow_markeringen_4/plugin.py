from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .import_selected import (
    MANAGED_LAYER_NAME,
    ImportCandidate,
    build_managed_attributes,
    validate_import_candidates,
)
from .copy_parallel import CopyParallelCandidate, validate_copy_parallel_selection


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
    """QGIS plugin implementation with phase 1 + phase 2 flows."""

    def __init__(self, iface):
        self.iface = iface
        self._import_action: Optional[object] = None
        self._copy_parallel_action: Optional[object] = None
        self._copy_parallel_map_tool: Optional[object] = None
        self._previous_map_tool: Optional[object] = None

    def initGui(self) -> None:  # QGIS naming
        QAction, QIcon, QCoreApplication, QgsMessageLog, Qgis = _safe_import_qgis()

        text = QCoreApplication.translate("OTLMOWMarkeringen", "OTLMOW: Import selected")
        self._import_action = QAction(QIcon(), text, self.iface.mainWindow())
        self._import_action.setToolTip(text)
        self._import_action.triggered.connect(self._on_import_selected)

        copy_text = QCoreApplication.translate("OTLMOWMarkeringen", "OTLMOW: Copy parallel")
        self._copy_parallel_action = QAction(QIcon(), copy_text, self.iface.mainWindow())
        self._copy_parallel_action.setToolTip(copy_text)
        self._copy_parallel_action.setCheckable(True)
        self._copy_parallel_action.toggled.connect(self._on_copy_parallel_toggled)

        self.iface.addToolBarIcon(self._import_action)
        self.iface.addToolBarIcon(self._copy_parallel_action)
        self.iface.addPluginToMenu("OTLMOW Markeringen", self._import_action)
        self.iface.addPluginToMenu("OTLMOW Markeringen", self._copy_parallel_action)

        QgsMessageLog.logMessage("Plugin GUI initialized", "OTLMOW Markeringen", Qgis.Info)

    def unload(self) -> None:
        if not self._import_action and not self._copy_parallel_action:
            return

        _QAction, _QIcon, _QCoreApplication, QgsMessageLog, Qgis = _safe_import_qgis()

        self._deactivate_copy_parallel_mode()

        if self._import_action:
            self.iface.removeToolBarIcon(self._import_action)
            self.iface.removePluginMenu("OTLMOW Markeringen", self._import_action)

        if self._copy_parallel_action:
            self.iface.removeToolBarIcon(self._copy_parallel_action)
            self.iface.removePluginMenu("OTLMOW Markeringen", self._copy_parallel_action)
        QgsMessageLog.logMessage("Plugin unloaded", "OTLMOW Markeringen", Qgis.Info)

        self._import_action = None
        self._copy_parallel_action = None

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
        geometries_by_fid = {}
        skipped_missing_geometry = 0
        skipped_unconvertible_multipart = 0
        converted_multipart = 0

        for feature in selected_features:
            geometry = feature.geometry()
            if geometry is None or geometry.isEmpty():
                skipped_missing_geometry += 1
                continue

            geometry_to_import = geometry
            is_multipart = geometry_to_import.isMultipart()
            if is_multipart:
                converted_geometry = self._try_convert_multiline_to_singleline(geometry_to_import)
                if converted_geometry is None:
                    skipped_unconvertible_multipart += 1
                    continue
                geometry_to_import = converted_geometry
                is_multipart = False
                converted_multipart += 1

            geometries_by_fid[int(feature.id())] = geometry_to_import

            candidates.append(
                ImportCandidate(
                    source_layer=source_layer.name(),
                    source_fid=int(feature.id()),
                    is_line=geometry_to_import.type() == 1,
                    is_multipart=is_multipart,
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
            import_geometry = geometries_by_fid.get(candidate.source_fid)
            if import_geometry is None or import_geometry.isEmpty():
                continue

            mapped_attributes = build_managed_attributes(
                source_layer=candidate.source_layer,
                source_fid=candidate.source_fid,
                source_attributes=candidate.attributes,
                created_at=now,
            )
            mapped_attributes["geometry_length_m"] = import_geometry.length()

            new_feature = QgsFeature(managed_layer.fields())
            new_feature.setGeometry(import_geometry)
            for name in field_names:
                if name in mapped_attributes:
                    new_feature[name] = mapped_attributes[name]

            if provider.addFeatures([new_feature]):
                imported += 1

        managed_layer.updateExtents()
        managed_layer.triggerRepaint()

        summary = (
            f"Import selected afgerond: {imported} geimporteerd, "
            f"{converted_multipart} multipart geconverteerd, "
            f"{validation.skipped_multipart + skipped_unconvertible_multipart} multipart overgeslagen, "
            f"{validation.skipped_not_line + skipped_missing_geometry} ongeldig."
        )
        self._notify(summary, Qgis.Info)
        QgsMessageLog.logMessage(summary, "OTLMOW Markeringen", Qgis.Info)

    def _try_convert_multiline_to_singleline(self, geometry):
        """Convert a multi-part line geometry into a single-part line where possible."""

        from qgis.core import QgsGeometry

        if geometry is None or geometry.isEmpty() or geometry.type() != 1:
            return None
        if not geometry.isMultipart():
            return geometry

        merged = geometry.mergeLines()
        if merged is not None and not merged.isEmpty() and merged.type() == 1 and not merged.isMultipart():
            return merged

        parts = geometry.asMultiPolyline()
        if len(parts) == 1:
            return QgsGeometry.fromPolylineXY(parts[0])

        return None

    def _on_copy_parallel_toggled(self, checked: bool) -> None:
        """Activate or deactivate copy-parallel map-click mode."""

        from qgis.core import Qgis

        if checked:
            validation = self._validate_copy_parallel_selection()
            if validation.error_message:
                self._notify(validation.error_message, Qgis.Warning)
                if self._copy_parallel_action:
                    self._copy_parallel_action.blockSignals(True)
                    self._copy_parallel_action.setChecked(False)
                    self._copy_parallel_action.blockSignals(False)
                return

            self._activate_copy_parallel_mode()
            self._notify("Copy parallel is actief. Klik op de kaart om een parallelle lijn te maken.", Qgis.Info)
            return

        self._deactivate_copy_parallel_mode()

    def _validate_copy_parallel_selection(self):
        """Validate that exactly one single-part line is selected on the active layer."""

        source_layer = self.iface.activeLayer()
        if source_layer is None:
            return validate_copy_parallel_selection([])

        selected_features = source_layer.selectedFeatures()
        candidates = []
        for feature in selected_features:
            geometry = feature.geometry()
            candidates.append(
                CopyParallelCandidate(
                    source_fid=int(feature.id()),
                    is_line=bool(geometry) and geometry.type() == 1,
                    is_multipart=bool(geometry) and geometry.isMultipart(),
                )
            )

        return validate_copy_parallel_selection(candidates)

    def _activate_copy_parallel_mode(self) -> None:
        """Install a map tool that listens to canvas clicks while mode is enabled."""

        from qgis.gui import QgsMapToolEmitPoint

        canvas = self.iface.mapCanvas()
        self._previous_map_tool = canvas.mapTool()

        self._copy_parallel_map_tool = QgsMapToolEmitPoint(canvas)
        self._copy_parallel_map_tool.canvasClicked.connect(self._on_copy_parallel_canvas_clicked)
        canvas.setMapTool(self._copy_parallel_map_tool)

    def _deactivate_copy_parallel_mode(self) -> None:
        """Remove the copy-parallel map tool and restore the previous one when possible."""

        canvas = self.iface.mapCanvas()
        if self._copy_parallel_map_tool is not None:
            try:
                self._copy_parallel_map_tool.canvasClicked.disconnect(self._on_copy_parallel_canvas_clicked)
            except Exception:
                pass

        if self._previous_map_tool is not None:
            canvas.setMapTool(self._previous_map_tool)

        self._copy_parallel_map_tool = None
        self._previous_map_tool = None

    def _on_copy_parallel_canvas_clicked(self, point, _button) -> None:
        """Create one offset line through the clicked point when copy-parallel mode is active."""

        from qgis.core import Qgis, QgsFeature, QgsGeometry

        validation = self._validate_copy_parallel_selection()
        if validation.error_message:
            self._notify(validation.error_message, Qgis.Warning)
            return

        source_layer = self.iface.activeLayer()
        if source_layer is None:
            self._notify("Geen actieve laag beschikbaar voor Copy parallel.", Qgis.Warning)
            return

        selected_features = source_layer.selectedFeatures()
        source_feature = selected_features[0]
        source_geometry = source_feature.geometry()
        if source_geometry is None or source_geometry.isEmpty():
            self._notify("De geselecteerde lijn heeft geen geldige geometrie.", Qgis.Warning)
            return

        if source_geometry.isMultipart():
            self._notify("Copy parallel ondersteunt enkel single-part lijnen.", Qgis.Warning)
            return

        point_geometry = QgsGeometry.fromPointXY(point)
        distance = source_geometry.distance(point_geometry)
        if distance <= 0.0:
            self._notify("Klik naast de bronlijn om een parallelle lijn te maken.", Qgis.Warning)
            return

        positive = source_geometry.offsetCurve(distance, 8, 1, 2.0)
        negative = source_geometry.offsetCurve(-distance, 8, 1, 2.0)

        candidates = [g for g in (positive, negative) if g is not None and not g.isEmpty()]
        if not candidates:
            self._notify("Kon geen parallelle lijn berekenen voor dit klikpunt.", Qgis.Warning)
            return

        offset_geometry = min(candidates, key=lambda g: g.distance(point_geometry))
        if offset_geometry.isMultipart():
            converted = self._try_convert_multiline_to_singleline(offset_geometry)
            if converted is None:
                self._notify("De berekende offset is multipart en kan niet als enkele lijn worden opgeslagen.", Qgis.Warning)
                return
            offset_geometry = converted

        if offset_geometry.length() < 1.0:
            self._notify("Berekende lijn is korter dan 1.0 m en wordt niet toegevoegd.", Qgis.Warning)
            return

        managed_layer = self._ensure_managed_layer(source_layer)
        provider = managed_layer.dataProvider()
        now = datetime.now(timezone.utc)
        source_field_names = [field.name() for field in source_layer.fields()]
        source_attributes = dict(zip(source_field_names, source_feature.attributes()))
        mapped_attributes = build_managed_attributes(
            source_layer=source_layer.name(),
            source_fid=int(source_feature.id()),
            source_attributes=source_attributes,
            created_at=now,
        )
        mapped_attributes["geometry_length_m"] = offset_geometry.length()

        new_feature = QgsFeature(managed_layer.fields())
        new_feature.setGeometry(offset_geometry)
        for field in managed_layer.fields():
            field_name = field.name()
            if field_name in mapped_attributes:
                new_feature[field_name] = mapped_attributes[field_name]

        if not provider.addFeatures([new_feature]):
            self._notify("Kon parallelle lijn niet toevoegen aan de beheerde laag.", Qgis.Warning)
            return

        managed_layer.updateExtents()
        managed_layer.triggerRepaint()
        self._notify("Parallelle lijn toegevoegd aan de beheerde laag.", Qgis.Info)

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


