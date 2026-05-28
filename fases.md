# Plan van aanpak in fases

Doel: de plugin iteratief opbouwen volgens de vernieuwde `spec.md`, met focus op de twee kernflows **Import selected** en **Copy parallel**, en met expliciete aandacht voor testbaarheid en QGIS-compatibiliteit.

## Huidige status (wat al in de repo zit)

### Fase 0 is afgerond
- Basis plugin-structuur aanwezig in `otlmow_markeringen/`.
- Plugin is importeerbaar zonder PyQGIS door lazy imports in `otlmow_markeringen/plugin.py`.
- Minimale action/GUI lifecycle aanwezig (`initGui`, `unload`, click-handler).
- Repo-check script aanwezig: `scripts/check_plugin_structure.py`.
- Basistests aanwezig:
  - `tests/test_phase0_plugin_import.py`
  - `tests/test_validate_qgis_plugin_dir.py`

### Nog niet geïmplementeerd (volgens spec)
- Geen beheerde laag met schema/mapping (FR-01/02/03).
- Geen `Import selected` flow.
- Geen `Copy parallel` modus en offset-creatie (FR-04/05).
- Geen lengte/CRS-validatie volgens Lambert2008/fallback (FR-06/07).
- Geen OTL-export met OTLMOW-model/converter (FR-08/09).
- Geen `vendor/`-beleid, lockfile en update-script (NFR-06 t.e.m. NFR-08).

---

## Uitgangspunten voor alle volgende fases
- Elke fase levert een werkende tussenstap op die in QGIS getest kan worden.
- PyQGIS-afhankelijke code blijft zo dun mogelijk; kernlogica komt in testbare modules.
- Elke fase koppelt expliciet naar FR/AC in `spec.md`.
- Geen fase is "done" zonder geautomatiseerde tests (minstens unit; integratie waar haalbaar).

## Definition of Done (algemeen)
- Relevante FR/AC voor de fase zijn aantoonbaar geïmplementeerd.
- `pytest` draait groen voor toegevoegde tests.
- Korte "Try in QGIS" stappen staan in docs of PR-notes.
- `spec.md` en docs zijn gesynchroniseerd bij scopewijzigingen.

---

## Fase 1 - Import selected + beheerde laag (FR-01/02/03)
**Doel:** geselecteerde single-part lijnen kunnen importeren naar een enkele door de plugin beheerde laag.

**Status:** geimplementeerd in deze iteratie (basisversie, klaar voor QGIS smoke test).

**Scope**
- Knop/actie `Import selected`.
- Beheerde laag auto-aanmaken indien ontbrekend.
- Alleen line features toelaten; multi-part overslaan met duidelijke melding.
- Attribuutmapping met defaults + plugin-meta (`source_layer`, `source_fid`, `created_at`, ...).

**Acceptatie (spec-koppeling)**
- AC-01 voor foutgedrag bij ongeldige selectiecontext.
- Main flow "Import selected" stap 1-5 werkt.

**Tests**
- Unit: selectievalidatie en mapping-defaults.
- Integratie (indien PyQGIS testomgeving): import van geselecteerde features naar memory managed layer.

**Opgeleverd**
- Plugin-actie `Import selected` in `otlmow_markeringen/plugin.py`.
- Auto-creatie van beheerde memory-laag `OTLMOW Markeringen` met basisschema.
- Validatie: alleen single-part lijnen worden geimporteerd; multipart en ongeldige selectie worden overgeslagen met melding.
- Mapping/default logica in `otlmow_markeringen/import_selected.py`.
- Nieuwe unittests in `tests/test_phase1_import_logic.py`.

---

## Fase 2 - Copy parallel modus (FR-04/05 basis)
**Doel:** met exact 1 geselecteerde bronlijn en kaartklik een nieuwe parallelle lijn maken in de nieuwe laag.

**Status:** geimplementeerd in deze iteratie (basisversie, klaar voor QGIS 3 smoke test).

**Scope**
- Togglebare `Copy parallel` modus met zichtbare UI-status.
- Preconditions afdwingen: exact 1 single-part bronlijn.
- Klik op kaart triggert offset-creatie door klikpunt.
- Nieuwe feature toevoegen aan dezelfde beheerde laag als fase 1.

**Acceptatie (spec-koppeling)**
- AC-01 en AC-02.
- Subflow "Copy parallel" stap 1-4 en 6 werkt voor happy path.

**Tests**
- Unit: precondition checks (0, 1, >1 selectie; multipart blokkeren).
- Unit: kern offset-berekening (QGIS-onafhankelijk waar mogelijk).
- Integratie: modus aan, klik simuleren, 1 nieuwe feature in managed layer.

**Opgeleverd**
- Nieuwe checkbare plugin-actie `Copy parallel` in zowel `otlmow_markeringen/plugin.py` als `otlmow_markeringen_4/plugin.py`.
- Togglebare kaartmodus met `QgsMapToolEmitPoint`; elke klik probeert exact 1 parallelle lijn te maken.
- Preconditions afgedwongen via testbare helpermodule `copy_parallel.py` (exact 1 selectie, lijngeometrie, single-part).
- Offset-creatie via QGIS `offsetCurve` (beide zijden geprobeerd, dichtst bij klikpunt gekozen).
- Nieuwe lijn wordt aan dezelfde beheerde laag toegevoegd met bestaande attribuutmapping/defaults.
- Nieuwe unittests in `tests/test_phase2_copy_parallel_logic.py`.

---

## Fase 3 - Geometrische validatie en foutmeldingen (FR-05/06)
**Doel:** ongeldige geometrieën worden consequent geweigerd met duidelijke feedback.

**Status:** geimplementeerd in deze iteratie (basisversie, klaar voor QGIS 3 smoke test).

**Scope**
- Minimale lengtecontrole >= 1.0 m.
- Validatie op invalid geometry / self-intersections / niet-construeerbare offset.
- Eenduidige, bruikbare foutmeldingen met herstelhint.

**Acceptatie (spec-koppeling)**
- AC-03.
- Subflow "Copy parallel" stap 5 correct afgedekt.

**Tests**
- Unit: lengtevalidatie en foutcodering.
- Unit/integratie: invalid resultaat wordt niet toegevoegd.

**Opgeleverd**
- Nieuwe validatiemodule `geometry_validation.py` in zowel `otlmow_markeringen/` als `otlmow_markeringen_4/`.
- Bron- en offsetgeometrie worden nu gevalideerd op GEOS-validiteit en self-intersections (`isSimple`).
- Offsetresultaten korter dan 1.0 m worden geweigerd met duidelijke gebruikersmelding.
- Niet-construeerbare offset geeft een expliciete melding met herstelhint (ander klikpunt/eenvoudigere bronlijn).
- Nieuwe unittests in `tests/test_phase3_geometry_validation.py`.

---

## Fase 4 - CRS- en metingen-correctheid (FR-07)
**Doel:** berekeningen en lengtes blijven correct in meters, onafhankelijk van project-/laag-CRS.

**Scope**
- Beslislogica uit spec implementeren:
  - project-CRS in meters -> daarin rekenen,
  - anders tijdelijk Lambert2008 (fallback Lambert72) of geodetische meting.
- Duidelijke documentatie van gekozen pad.

**Acceptatie (spec-koppeling)**
- AC-04.

**Tests**
- Unit: CRS-keuzelogica.
- Integratie: project-CRS != layer-CRS scenario met correcte lengte-uitkomst.

---

## Fase 5 - Vendoring fundament + updateprocedure (NFR-06 t.e.m. NFR-08)
**Doel:** OTLMOW-dependencies reproduceerbaar meeleveren binnen de plugin.

**Scope**
- `vendor/` structuur en `sys.path` injectie voor imports.
- `vendor/README.md` + `vendor/LOCK.json`.
- `scripts/update_vendor.py` voor gecontroleerde updates.
- Basis import-smoke voor vendored libs.

**Acceptatie (spec-koppeling)**
- AC-06 en AC-08 (voor import/start en lock-consistentie).

**Tests**
- Smoke test: vendored import lukt.
- Script test: lockfile wordt correct gelezen/bijgewerkt.

---

## Fase 6 - OTL export end-to-end (FR-08/09)
**Doel:** beheerde laag exporteren naar OTL-conforme output via OTLMOW-model/converter.

**Scope**
- `Export OTL` actie.
- Mapping managed-layer attributen -> OTL objecten.
- Duidelijke foutafhandeling bij ontbrekende verplichte data.

**Acceptatie (spec-koppeling)**
- AC-05.

**Tests**
- Unit: mapping/serialisatie.
- Integratie: n features in managed layer -> n objecten in exportresultaat.

---

## Fase 7 - Cross-platform afronding en release hardening (NFR-05/09/10)
**Doel:** stabiele werking op Linux en Windows + duidelijke installatie/dev workflow.

**Scope**
- README update met symlink/junction stappen voor beide platformen.
- Metadata-validatie uitbreiden waar nodig (`name`, `qgisMinimumVersion`, ...).
- Install/packaging smoke check op beide OS'en.

**Acceptatie (spec-koppeling)**
- AC-07.

**Tests**
- Minstens unit tests op Linux/Windows.
- Handmatige QGIS smoke checklist per OS.

---

## Backlog na deze fases (niet-kritisch)
- `Merge selected` en `Split selected` acties.
- Geavanceerde bulk-opties bovenop `Import selected`.
- Extra UX (preview, geavanceerde instellingen, performance tuning).

## Praktische task-checklist per fase
- [ ] Scope + FR/AC verwijzingen bevestigd
- [ ] Implementatie afgerond
- [ ] Unit tests toegevoegd
- [ ] Integratietest toegevoegd of expliciet gemotiveerd waarom nog niet
- [ ] Docs/README geüpdatet
- [ ] Korte QGIS smoke-run uitgevoerd
