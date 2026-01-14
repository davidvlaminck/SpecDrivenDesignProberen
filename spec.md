# Introductie
Dit project heeft als doel een QGIS-plugin te maken om **OTL-conforme markeringen** (lijnfeatures) aan te maken, te wijzigen/verwijderen en OTL-conform te exporteren.

## Doel
Gebruikers moeten snel een **parallelle lijn** kunnen aanmaken op basis van een bestaande lijn (bronlijn) en een klikpunt, en deze resultaten later kunnen exporteren volgens OTL-afspraken.

## Scope
### In scope
- Een modus **“Copy parallel”** die actief blijft tot de gebruiker die uitzet.
- Op basis van **exact één geselecteerde bronlijn**: bij een klik in de kaart een parallelle lijn toevoegen aan een **door de plugin beheerde laag**.
- Basisvalidatie (o.a. minimale lengte) en duidelijke foutmeldingen.
- Export van de beheerde laag naar een afgesproken **OTL-conform** formaat.
- Gebruik van de externe Python packages **OTLMOW-Model** en **OTLMOW-converter** voor OTL-datamodel en (de)serialisatie/conversie.

### Out of scope (voor nu)
- Bulk-acties op meerdere bronlijnen tegelijk.
- Complexe topologie-/snapping-regels (buiten wat QGIS standaard aanbiedt).
- Multi-user editing / database locking scenarios.

## Terminologie & definities
- **Bronlijn**: de (exact één) geselecteerde lijnfeature waarop de parallelle lijn gebaseerd wordt.
- **Beheerde laag**: een laag die door de plugin wordt aangemaakt/beheerd en waarin alle gegenereerde markeringen terechtkomen.
- **OTL-conform**: het exportresultaat voldoet aan de afgesproken OTL-structuur (verplichte attributen, types, domeinwaarden, …). *(OTL-detail: nog te concretiseren in een volgende iteratie.)*
- **Parallel**: “offset-curve” van de bronlijn. De nieuwe lijn moet door het klikpunt gaan (offsetafstand wordt dus afgeleid uit het punt t.o.v. de bronlijn).

## User flow (gewenst gebruik)
1. Gebruiker selecteert (of tekent en selecteert) één lijn in QGIS (**bronlijn**).
2. Gebruiker activeert de knop **“Copy parallel”** (modus blijft actief).
3. Gebruiker klikt op een punt in de kaart.
4. De plugin maakt een nieuwe lijn aan:
   - parallel aan de bronlijn,
   - door het klikpunt,
   - en voegt deze toe aan de beheerde laag.
5. Gebruiker kan stap 3–4 herhalen om meerdere parallelle lijnen te maken.
6. Gebruiker zet de modus uit (knop deactiveren).
7. Gebruiker klikt op **Export** om de beheerde laag OTL-conform te exporteren.

---

## Functionele requirements (FR)
**FR-01 Selectie van bronlijn**
- De plugin gebruikt exact één geselecteerde lijnfeature als bron.
- Als er **geen** of **meer dan één** feature geselecteerd is: toon een duidelijke melding en voer geen actie uit.

**FR-02 Modus “Copy parallel”**
- De modus kan aan/uit gezet worden via een UI-element (toolbar-knop).
- Terwijl de modus aan staat, creëert elke klik in de kaart precies **één** nieuwe lijnfeature in de beheerde laag.

**FR-03 Beheerde laag**
- Als de beheerde laag nog niet bestaat, maakt de plugin die automatisch aan.
- Alle gegenereerde lijnen worden toegevoegd aan deze laag.
- De beheerde laag is duidelijk herkenbaar (naam/metadata) als “plugin-managed”.

**FR-04 Geometrie: parallelle lijn door klikpunt**
- Bij een kaartklik wordt een parallelle lijn (offset-curve) berekend t.o.v. de bronlijn.
- De resulterende lijn moet door het gekozen klikpunt gaan.
- Als het niet mogelijk is om een geldige parallelle lijn te berekenen: toon foutmelding, voeg niets toe.

**FR-05 Validatie: minimale lengte**
- Alleen lijngeometriën met lengte **≥ 1,0 meter** zijn geldig.
- Ongeldige lijnen worden niet opgeslagen; de gebruiker krijgt een melding met de reden.

**FR-06 CRS / projecties**
- De plugin werkt correct ongeacht project-CRS en bronlaag-CRS.
- Lengtevalidatie gebeurt in **meters**. (Implementatiekeuze: reprojectie naar een meter-gebaseerde CRS of geodetische meting; dit wordt vastgelegd tijdens implementatie en gedekt door tests.)

**FR-07 Export (OTL-conform)**
- Er is een exportactie die de beheerde laag exporteert naar het afgesproken OTL-conforme formaat.
- Als verplichte OTL-attributen of -regels ontbreken: export faalt met een duidelijke melding.

**FR-08 OTLMOW-Model gebruiken**
- Voor het OTL-datamodel gebruikt de plugin de externe Python package **OTLMOW-Model**:
  - repository: https://github.com/davidvlaminck/OTLMOW-Model
- Het genereren/valideren van OTL-objecten gebeurt via deze library (dus niet via een eigen, losstaand model).

**FR-09 OTLMOW-converter gebruiken**
- Voor export/conversie gebruikt de plugin de externe Python package **OTLMOW-converter**:
  - repository: https://github.com/davidvlaminck/OTLMOW-converter
- Export gebruikt deze library als ‘single source of truth’ voor conversielogica waar mogelijk.

---

## Niet-functionele requirements (NFR)
**NFR-01 Gebruiksvriendelijkheid**
- De UI maakt duidelijk of “Copy parallel” aan/uit staat.
- Bij fouten krijgt de gebruiker een actiegerichte melding (wat ging fout + hoe oplossen).

**NFR-02 Testbaarheid**
- Zo veel mogelijk logica moet unit-testbaar zijn zonder QGIS (pure Python modules).
- QGIS/PyQGIS-afhankelijke delen worden dun gehouden (adapterlaag), zodat de kernlogica testbaar blijft.

**NFR-03 Versiebeheer & documentatie**
- Ontwikkeling gebeurt met git.
- Specificatie en technische beslissingen worden bijgehouden (spec-driven development).

**NFR-04 Iteratieve ontwikkeling (fasering)**
- Ontwikkeling gebeurt in fases waarbij elke fase eindigt met:
  - een werkend prototype,
  - geüpdatete spec,
  - en bijhorende tests.
  
**NFR-05 Cross-platform ondersteuning**
- De plugin moet werken op **Windows** en **Linux** (minimaal voor de beoogde QGIS 3.x versies).
- Platform-specifieke codepaden moeten vermeden worden, of expliciet afgeschermd en getest.

**NFR-06 Dependency/packaging workaround voor QGIS Python**
- Er moet een **praktische en veilige workaround** bestaan om **OTLMOW-Model** en **OTLMOW-converter** te gebruiken binnen de QGIS Python-omgeving, zonder dat gebruikers handmatig packages in de QGIS-systeempython hoeven te installeren.
- De oplossing moet gedocumenteerd worden en cross-platform toepasbaar zijn.

**Gekozen aanpak (voorlopig): vendoring/bundling in de plugin**
- De plugin distribueert OTLMOW-Model en OTLMOW-converter (en noodzakelijke pure-Python dependencies) mee in een `vendor/` map in de plugin.
- Bij plugin-initialisatie wordt `vendor/` (of `vendor/site-packages/`) aan `sys.path` toegevoegd vóór imports.
- Doel: werken op een “schone” QGIS-installatie zonder extra pip installs in de QGIS-systeempython.

**Randvoorwaarden bij vendoring**
- We vendor’en enkel dependencies die **pure Python** zijn of waarvan we weten dat ze in QGIS al aanwezig zijn.
- Licenties van meegebundelde dependencies worden opgenomen in de plugin-distributie.

**NFR-07 Versiebeheer van vendored dependencies (updatebeleid)**
- Er is een expliciet versiebeleid voor vendored packages:
  - (a) OTLMOW-Model versie (tag/commit) en OTLMOW-converter versie (tag/commit) liggen vast per plugin-release.
  - (b) We houden een `vendor/README.md` (of `docs/dependencies.md`) bij met:
    - bronrepo + exacte versie/tag/commit,
    - datum van update,
    - korte changelog-impact (breaking changes, migraties).
  - (c) Elke update van vendored packages triggert minimaal de export-tests (PyQGIS integratie) én unit tests.

**(Semi-)automatische integratie van nieuwe versies**
- Er is minstens één reproduceerbare manier om vendoring te updaten, bv. via een script in `scripts/` dat:
  - de gewenste versies vastlegt (tags/commits),
  - de packages ophaalt en in de plugin `vendor/` plaatst,
  - en optioneel een “dependency manifest” bijwerkt (bv. `vendor/LOCK.json`).
- Automatisch updaten zonder review is niet vereist; wél: automatiseren van het **mechanische** deel (download/copy/lockfile bijwerken) om fouten te vermijden.

---

## Acceptatiecriteria (Given/When/Then)
**AC-01 (FR-01)**
- Given: 0 of >1 selectie
- When: gebruiker activeert modus of klikt om te creëren
- Then: er wordt niets aangemaakt en er verschijnt een foutmelding

**AC-02 (FR-02/FR-04)**
- Given: exact één bronlijn geselecteerd en modus “Copy parallel” is aan
- When: gebruiker klikt op punt P
- Then: er verschijnt exact één nieuwe lijn in de beheerde laag die parallel is aan de bronlijn en door P gaat

**AC-03 (FR-05)**
- Given: de berekende lijn heeft lengte < 1,0 m
- When: de plugin probeert deze toe te voegen
- Then: de feature wordt niet toegevoegd en de gebruiker krijgt een melding

**AC-04 (FR-06)**
- Given: project-CRS ≠ bronlaag-CRS
- When: gebruiker maakt parallelle lijnen en exporteert
- Then: geometrie en lengtevalidatie blijven correct (in meters)

**AC-05 (FR-07)**
- Given: beheerde laag bevat n lijnen
- When: gebruiker exporteert
- Then: outputbestand bevat n lijnen en voldoet aan OTL-regels (of faalt expliciet met duidelijke melding)

**AC-06 (FR-08/FR-09, NFR-06)**
- Given: plugin is geïnstalleerd op een “schone” QGIS-installatie (zonder manuele pip installs in QGIS-Python)
- When: gebruiker exporteert OTL
- Then: export gebruikt OTLMOW-Model/OTLMOW-converter succesvol, of faalt met een duidelijke melding die naar de gedocumenteerde oplossing verwijst

**AC-07 (NFR-05)**
- Given: dezelfde pluginversie
- When: installatie/gebruik op Linux en op Windows
- Then: kernflow (copy-parallel + export) werkt op beide platformen

**AC-08 (NFR-07)**
- Given: OTLMOW-Model/Converter worden geüpdatet naar een nieuwe tag/commit
- When: de vendoring-updateprocedure wordt uitgevoerd
- Then:
  - de exacte versies staan gedocumenteerd/gelocked,
  - de plugin start zonder import errors,
  - en de relevante testset draait groen (minimaal exportpad) op Linux én Windows.

---

## Teststrategie (richtlijn)
- **Unit tests (zonder QGIS):**
  - validaties (minimale lengte, input checks),
  - OTL-mapping/serialisatie (zodra OTL concreet is),
  - wiskundige/algoritmische helpers.
- **Integratietests (met PyQGIS):**
  - aanmaken beheerde laag, toevoegen features,
  - CRS-transformaties,
  - export (end-to-end) in een QGIS-omgeving.

## QGIS Python interpreter vs project-venv (veiligheid & werking)
- **PyQGIS werkt meestal enkel betrouwbaar met de Python die bij QGIS hoort** (de “QGIS interpreter”).
- Een **project-venv** is ideaal voor pure Python (unit tests, tooling), maar kan conflicteren met QGIS-dependencies als je PyQGIS probeert te “pip installen”.
- Veilig uitgangspunt:
  - gebruik de QGIS-interpreter voor code die `qgis.*` importeert;
  - gebruik de project-venv voor QGIS-onafhankelijke code en unit tests.
- Belangrijk: installeer niet zomaar packages in de QGIS-systeempython; dependency-conflicten kunnen QGIS breken. Documenteer elke extra dependency expliciet.
- Omdat OTLMOW-Model en OTLMOW-converter externe dependencies zijn, moet de gekozen workaround (zie **NFR-06**) vermijden dat extra pip-installaties in de QGIS-systeempython nodig zijn.
