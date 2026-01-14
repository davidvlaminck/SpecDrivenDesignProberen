# Plan van aanpak in fases (voorbeeld)

Doel: **zo snel mogelijk een werkende QGIS plugin** die we in QGIS kunnen testen (smoke test), en daarna iteratief uitbreiden met extra functionaliteit, hardere validaties en betere UX.

Dit document is bedoeld als:
- ontwikkel-roadmap (in fases), én
- stappenplan voor implementatie (ook geschikt om door een coding agent te laten uitvoeren).

## Uitgangspunten
- Werk **iteratief**: elke fase eindigt met een installeerbare plugin + korte demo-instructies + tests.
- Hou de kernlogica zo veel mogelijk **QGIS-onafhankelijk** (unit testbaar), en bouw een dunne PyQGIS “adapterlaag”.
- **Vendoring** is voorlopig de gekozen manier om OTLMOW-Model en OTLMOW-converter te gebruiken zonder pip-installaties in de QGIS-systeempython (zie `spec.md` NFR-06).
- Doelplatformen: **Linux en Windows** (zie `spec.md` NFR-05).

## Definition of Done (algemeen, voor elke fase)
- Code op main branch bouwt/werkt lokaal.
- Spec en docs zijn bijgewerkt waar relevant.
- Minstens 1 geautomatiseerde test waar mogelijk (unit of integratie).
- Er is een korte “Try it in QGIS” checklist.

---

## Fase 0 — Repo skeleton + “kan in QGIS laden” (0.5–1 dag)
**Doel:** zo snel mogelijk bevestigen dat de plugin laadt in QGIS, met een minimale knop/actie.

**Scope**
- Plugin-skelet (QGIS plugin structuur) met:
  - minimaal 1 toolbar-knop die een melding toont (“Plugin loaded”).
  - basis metadata.
- Simpele logging.

**Deliverables**
- Werkende plugin die je kan installeren via “Install from ZIP” of via QGIS plugin folder.
- Korte stappen om te testen in QGIS.

**Acceptatie**
- Plugin verschijnt in QGIS en kan geactiveerd worden.
- Klik op knop → toont melding en logt naar QGIS message log.

**Tests**
- (Optioneel) minimumeenheidstest voor een dummy helperfunctie.

---

## Fase 1 — Copy-parallel “happy path” (1–3 dagen)
**Doel:** eerste echte kernflow: bronlijn selecteren + modus aan + klikpunt → nieuwe lijn in beheerde laag.

**Scope**
- UI:
  - Toggle knop “Copy parallel” (aan/uit).
- Basisbusiness rules:
  - FR-01: exactly 1 bronlijn geselecteerd.
  - FR-03: beheerde laag automatisch aanmaken.
  - FR-04: bereken parallelle offset-lijn door klikpunt (eerste implementatie mag simplistisch zijn, zolang het duidelijk werkt).

**Deliverables**
- Werkende copy-parallel flow in QGIS.
- “Beheerde laag” zichtbaar in layer panel.

**Acceptatie**
- AC-01, AC-02 uit `spec.md` werken voor de happy path.

**Tests**
- Unit tests voor input checks (0, 1, >1 selectie) via pure Python logic waar mogelijk.
- (Als PyQGIS testomgeving beschikbaar is) 1 integratietest die een memory layer maakt en een feature toevoegt.

---

## Fase 2 — Validaties + foutmeldingen + minimale UX (1–2 dagen)
**Doel:** fouten zijn begrijpelijk, en ongeldige features worden niet toegevoegd.

**Scope**
- FR-05: minimale lengte ≥ 1.0 m (meters).
- Basismeldingen:
  - geen selectie / te veel selectie
  - geen geldige parallel mogelijk
  - resultaat te kort
- UX:
  - duidelijke status “modus aan/uit” (bv. checked state/tooltip).

**Deliverables**
- Gebruiksvriendelijke foutmeldingen.
- Validatie actief.

**Acceptatie**
- AC-03 werkt.

**Tests**
- Unit test suite voor validatieregels (min length).

---

## Fase 3 — CRS/projecties correct (1–3 dagen)
**Doel:** correct werken met verschillende CRS’en; lengtevalidatie gebeurt in meters.

**Scope**
- FR-06 implementeren met een expliciete keuze:
  - optie A: geodetische meting (ellipsoïdaal) of
  - optie B: herprojectie naar geschikte meter-CRS voor meting.
- Documenteer de keuze in de repo.

**Deliverables**
- Consistente metingen/validaties.

**Acceptatie**
- AC-04 werkt (project-CRS ≠ laag-CRS scenario).

**Tests**
- Unit tests voor CRS-keuze/logica (waar mogelijk).
- Integratietest: project in CRS A, laag in CRS B, maak feature, check lengtevalidatie.

---

## Fase 4 — Vendoring OTLMOW packages + import smoke (1–3 dagen)
**Doel:** OTLMOW-Model en OTLMOW-converter zijn beschikbaar in QGIS zonder pip install.

**Scope**
- Implementatie van vendoring:
  - `vendor/` folder in plugin.
  - `sys.path` injectie bij plugin start.
  - eenvoudige smoke-check: imports lukken.
- Basis dependency-documentatie:
  - versies/tags/commits vastleggen.

**Deliverables**
- Plugin start in QGIS met OTLMOW imports beschikbaar.
- `vendor/` bevat de gekozen versies.
- `vendor/README.md` of `docs/dependencies.md` met versie-informatie.

**Acceptatie**
- AC-06 werkt in een “schone” QGIS omgeving.

**Tests**
- Integratietest/smoke: plugin start → `import` OTLMOW-Model + Converter ok.

---

## Fase 5 — Eerste OTL-export “end-to-end” (2–5 dagen)
**Doel:** export werkt met OTLMOW-converter.

**Scope**
- FR-07, FR-08, FR-09:
  - minimal viable export (een eerste formaat kiezen).
  - mapping van beheerde laag → OTL objects (minimale verplichte velden).
  - duidelijke error bij ontbrekende verplichte data.

**Deliverables**
- Exportknop + bestand output.
- Document: “welk formaat, welke verplichte velden”.

**Acceptatie**
- AC-05 werkt voor een klein testdataset.

**Tests**
- Unit tests voor mapping/serialisatie (waar QGIS-onafhankelijk).
- Integratietest: maak 1 feature → export → output bestaat + basis inhoud controles.

---

## Fase 6 — Cross-platform hardening (Windows + Linux) (1–3 dagen)
**Doel:** installeren/werken op beide platformen zonder handmatige fixes.

**Scope**
- Pad-handling (pathlib), file dialogs, newline/encoding.
- Plugin packaging check (ZIP) op Windows.

**Deliverables**
- Testnotities per OS.

**Acceptatie**
- AC-07 werkt.

**Tests**
- CI (indien repo later CI krijgt): matrix Linux/Windows met minimaal unit tests.
- Handmatige smoke test stappenlijst voor Windows.

---

## Fase 7 — Update-proces voor vendored dependencies (NFR-07) (1–2 dagen)
**Doel:** nieuwe versies van OTLMOW-Model/Converter gecontroleerd en reproduceerbaar integreren.

**Scope**
- Script in `scripts/` om vendoring te updaten (semi-automatisch):
  - input: gewenste tag/commit per package
  - output: bijgewerkte `vendor/` + lock/manifest
- Documenteer besluit: tags vs commits.

**Deliverables**
- Update-script + lockfile (bv. `vendor/LOCK.json`).

**Acceptatie**
- AC-08 werkt.

**Tests**
- Smoke test: na update-script → plugin start + imports ok.

---

## Fase 8 — UX & kwaliteitsverbeteringen (doorlopend)
**Mogelijke uitbreidingen**
- Extra instellingen (offset lock, preview, snapping hints).
- Undo/redo integratie.
- Batch-export, extra OTL velden, validatie tegen domeinwaarden.
- Performance bij grote bronlijnen.

---

## Praktische task breakdown template (copy/paste)
Voor elke fase kunnen we tickets zo uitschrijven:
- [ ] Spec update (FR/NFR/AC’s waar nodig)
- [ ] Implementatie (code)
- [ ] Tests (unit/integratie)
- [ ] Docs: “Try it in QGIS” stappen
- [ ] Review checklist: Windows/Linux, clean QGIS install, logging

