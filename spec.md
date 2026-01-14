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
