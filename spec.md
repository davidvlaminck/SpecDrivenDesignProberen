# Introductie
Dit project heeft als doel een QGIS-plugin te maken om **OTL-conforme markeringen** (lijnfeatures) aan te maken, te wijzigen/verwijderen en OTL-conform te exporteren.

# Doel
Gebruikers moeten snel een **parallelle lijn** kunnen aanmaken op basis van een bestaande lijn (bronlijn) en een klikpunt, en deze resultaten later kunnen exporteren conform de OTL-standaard. 

Daarbij moeten de knoppen in deze plug-in zo gebruiksvriendelijk mogelijk zijn, zodat de gebruikers minimale kennis en expertise nodig hebben om dit te kunnen gebruiken.

We maken hierbij gebruik van Agentic AI en willen de repository zo inrichten dat we deze kunnen gebruiken om de ontwikkeling te versnellen, zonder dat we de controle verliezen over het eindresultaat.

We testen hierbij het gebruik van Spec Driven Design waarbij je zoveel mogelijk gerichte context schrijft voor AI. We schrijven dus een uitgebreide specificatie van wat we willen bereiken, en laten AI deze specificatie gebruiken om de code te genereren. We zorgen er ook voor dat we zelf de controle houden over deze specificatie, en dat we deze kunnen aanpassen waar nodig. We zorgen er ook voor dat we de code die gegenereerd wordt kunnen testen, zodat we zeker weten dat deze doet wat we willen dat deze doet. AI mag geen bestanden zelf committen of de git historiek aanpassen.

We hergebruiken zoveel mogelijk de QGIS features.


# Voorbeeld flow
De korte voorbeeldstappen zijn hieronder geïntegreerd in de sectie "Gedetailleerde user flow". Zie ook de gescheiden kernflows in de scope: "Import selected" (bulk import van geselecteerde features) en "Copy parallel" (kaartklik gebaseerde offset-creatie).




## Scope 

### Belangrijke splitsing van flows
Om verwarring te vermijden beschrijven we twee duidelijke en afzonderlijke flows:

- Import selected
  - Doel: één of meerdere geselecteerde lijnen uit een bestaande bronlaag kopiëren naar de door de plugin beheerde laag ('Markeringen'), waarbij relevante attributen worden overgenomen en aangevuld met plugin-specifieke velden (keuzelijsten, status, afgeleide waarden).
  - Gebruik: gebruiker selecteert één of meerdere features en klikt op "Import selected".

- Copy parallel
  - Doel: op basis van exact één geselecteerde bronlijn en een kaartklik een nieuwe parallelle lijn (offset-curve) aanmaken die door het klikpunt gaat en toevoegen aan de door de plugin beheerde laag. Deze modus blijft actief totdat de gebruiker ze uitschakelt.
  - Voorwaarden: precies één geselecteerde bronlijn (FR-01). Als dat niet het geval is: geen creatie en duidelijke melding.
  - Door het klikken op de knop gaat de modus copy parallel aan, totdat deze gedeactiveerd wordt (zelfde knop of cancel). Tijdens deze modus creëert elke kaartklik een nieuwe parallelle lijn op basis van de geselecteerde bronlijn en het klikpunt, of toont een foutmelding als creatie niet mogelijk is (multi-part geometrie, korte lijnen, self-intersections).

### In scope
- Implementatie van beide hierboven beschreven flows, waarbij "Copy parallel" de kernfunctionaliteit is.
- Basisvalidatie (o.a. minimale lengte) en duidelijke foutmeldingen.
- Export van de beheerde laag naar een afgesproken OTL-conform formaat met gebruik van OTLMOW-Model en OTLMOW-converter.

### Out of scope (voor nu)
- Complexe bulk bewerkingen tijdens de eerste iteraties (bulk-opties kunnen later toegevoegd worden als optionele feature aan de import-flow).
- Geavanceerde topologie rules beyond default QGIS snapping.
- Multi-user editing / database locking.

## Terminologie & definities (uitgebreid)
- **Bronlijn**: de geselecteerde enkelvoudige (single-part) lijnfeature (exact één) waarop een "Copy parallel" operatie is gebaseerd. Multi-part geometrieën zijn **niet toegestaan** als bronlijn; bij selectie van een multi-part geometrie moet de plugin een foutmelding tonen en de actie blokkeren.
- **Beheerde laag**: een vectorlaag (memory of geopackage afhankelijk van implementatie) die door de plugin gemaakt en beheerd wordt en alle gegenereerde markeringen bevat.
- **OTL-conform**: het exportresultaat voldoet aan de OTL (= datastandaard) en vereiste attributen voor de doelconversie.
- **Offset-referentiepunt**: het punt op de bronlijn dat het dichtst bij het klikpunt ligt (projectie van klikpunt op de bronlijn). Dat punt bepaalt het lokale tangentsegment voor het maken van de offset.

## Main user flow — Import selected
1. Gebruiker selecteert één of meerdere lijnfeatures in een bronlaag.
2. Gebruiker klikt op **Import selected**.
3. De plugin valideert geselecteerde features: alleen single-part lijnen toegestaan in de beheerde laag; bij multi-part features: toon melding en sla die feature over (option: in een toekomstige uitbreiding aanbieden om automatisch te splitten).
4. Voor elke toegestane feature: kopieer geometrie en relevante attributen volgens een vooraf gedefinieerde mapping naar de beheerde laag; vul plugin-specifieke velden aan met defaults en voeg plugin-meta (bron-id, timestamp) toe.
5. Na import: toon samenvatting (aantal succesvol geïmporteerd, overgeslagen wegens validatie, fouten) en zet de gebruiker in de beheerde laag verder (bewerken, attributen invullen, symbologie aanpassen).
6. De gebruiker kan vanuit de beheerde laag de **Copy parallel** subflow activeren om offsets op basis van één bronlijn te maken (zie subflow).
7. Uiteindelijk kan de gebruiker de beheerde laag exporteren naar OTL via de export-knop.

## Subflow — Copy parallel
Doel: een hulpmiddel binnen de main workflow waarmee de gebruiker op basis van exact één geselecteerde single-part bronlijn en een kaartklik een parallelle lijn kan maken.
1. Gebruiker selecteert exact één single-part lijn in de beheerde laag of in de bronlaag (bronlijn). Als de geselecteerde feature een multi-part geometrie is: toon foutmelding en stop.
2. Gebruiker activeert de knop **"Copy parallel"**; de modus blijft actief en de UI geeft dit zichtbaar aan.
3. Gebruiker klikt op een punt in de kaart.
4. De plugin projecteert het klikpunt op de bronlijn om het offset-referentiepunt te bepalen en berekent een offset-curve die lokaal parallel is aan het bronsegment en door het klikpunt gaat.
5. Validatie: controleer lengte (≥ 1.0 m) en geometrische geldigheid (geen self-intersections, geen invalid geometry). Ongeldige resultaten worden niet toegevoegd; toon een duidelijke melding en suggesties voor correctie.
6. Indien geldig: voeg de nieuwe lijn toe aan de beheerde laag (met benodigde OTL-velden en plugin-meta).
7. Gebruiker kan stap 3–6 herhalen zolang de modus actief blijft en afsluiten door opnieuw op de knop te klikken of via cancel.

---

## Functionele requirements (FR) — geüpdatet en gescheiden per flow
**FR-01 Import selected — selectie & import**
- De plugin ondersteunt import van één of meerdere geselecteerde lijnfeatures in een bronlaag naar de beheerde laag.
- Een gebruiker kan dit meerdere keren doen: alle geïmporteerde features worden verzameld in één enkele beheerde laag (dus herhaalde imports vanuit een bronlaag voegen toe aan dezelfde beheerde laag, zonder meerdere beheerde lagen aan te maken).
- Alleen single-part lijnen worden geaccepteerd; multi-part geometrieën worden overgeslagen en de gebruiker ontvangt een melding met uitleg.

**FR-02 Import selected — attributen & mapping**
- Bij import worden relevante attributen gekopieerd volgens een vooraf gedefinieerde mapping; ontbrekende velden worden aangevuld met defaultwaarden.

**FR-03 Beheerde laag**
- Als de beheerde laag nog niet bestaat, maakt de plugin die automatisch aan (memory of geopackage configuratie optie).
- Alle geïmporteerde en gegenereerde lijnen worden toegevoegd aan deze laag. Het schema bevat velden voor OTL-attributes en plugin-meta (bron-id, afgeleid waarden).

**FR-04 Copy parallel — modus & gebruik**
- Copy parallel is een subflow/modaliteit die exact één geselecteerde single-part bronlijn vereist.
- De modus kan aan/uit gezet worden via een UI-element (toolbar-knop). Terwijl de modus actief is, creëert elke kaartklik maximaal één nieuwe lijnfeature in de beheerde laag (of toont een foutmelding als creatie niet mogelijk is).

**FR-05 Geometrie: parallelle lijn door klikpunt (technisch, Copy parallel)**
- Offset-referentie: de plugin projecteert het klikpunt op de (single-part) bronlijn en gebruikt het dichtstbijzijnde punt op de lijn als referentie.
- Offset-algoritme: voorkeur gaat uit naar het hergebruiken van de QGIS-geometrie-implementatie/algoritmes (PyQGIS API) om offsets en geometriebewerkingen uit te voeren. Alleen als dat niet mogelijk of onacceptabel is (compatibiliteit, performance of licentie) wordt een pure-Python fallback gebruikt. Details en testcases zijn vereist voor beide paden.
- Multi-part lijnen: niet toegestaan als bronlijn; bij detectie: toon foutmelding en sla de actie over.
- Speciale gevallen (korte lijnen, self-intersections) leiden tot validatiefouten en duidelijke meldingen.

**FR-06 Validatie: minimale lengte**
- Alleen lijngeometriën met lengte **≥ 1,0 meter** (gemeten in meters) zijn geldig.

**FR-07 CRS / projecties**
- De plugin moet correct werken ongeacht project-CRS en bronlaag-CRS.
- Standaard (default) werken we in het Belgische projectieprofiel: Lambert2008 (of als fallback Lambert72). Dat betekent dat berekeningen en validatie in meters standaard uitgevoerd worden in Lambert2008 wanneer mogelijk.
- Implementatie-keuze: indien het project-CRS afwijkt van Lambert2008 en project-CRS is projected en units in meters: berekeningen en validatie gebeuren in het project-CRS. Anders: reprojecteer tijdelijk naar Lambert2008 (of gebruik geodetische metingen via QgsDistanceArea) om lengte in meters te bepalen. Deze keuze moet getest en gedocumenteerd.

**FR-08 Export (OTL-conform)**
- De exportactie gebruikt OTLMOW-Model (datamodel) en OTLMOW-converter (wegschrijven naar bestanden) om OTL-conforme output te produceren.

**FR-09 Externe libraries: OTLMOW-Model & OTLMOW-converter**
- Gebruik de twee opgegeven externe repositories als single source of truth voor datamodel en conversie.

---

## Niet-functionele requirements (NFR) — verduidelijkingen
**NFR-01 Gebruiksvriendelijkheid**
- Duidelijke UI-status, foutmeldingen met oplossingssuggesties.

**NFR-02 Testbaarheid**
- Kernlogica moet unit-testbaar zijn zonder QGIS. PyQGIS-afhankelijke integratiecode blijft beperkt tot adapterlaag.
- Indien mogelijk en praktisch uitvoerbaar in de CI/dev-omgeving: voorziet de teststraat ook unit/integratietests die QGIS-functies aanroepen (mocked of via een geconfigureerde PyQGIS-testomgeving) om te verifiëren dat de juiste QGIS-API functies worden aangesproken en dat adapterlagen correct werken.

**NFR-03 Versiebeheer & documentatie**
- Git en spec-driven besluitvorming; changelogs bij grote wijzigingen.

**NFR-04 Iteratieve ontwikkeling (fasering)**
- Elke fase levert werkend prototype, bijgewerkte spec en tests.

**NFR-05 Cross-platform ondersteuning**
- Plugin moet werken op Windows en Linux. Documenteer verschillen (symlink/junction gedrag op Windows, path separators, bestandspermissies) en test beide platformen.

**NFR-06 Dependency/packaging workaround voor QGIS Python**
- Gekozen aanpak (voorlopig): vendoring/bundling van OTLMOW-Model en OTLMOW-converter (en noodzakelijke pure-Python dependencies) in `vendor/` map binnen de plugin.
- Bij plugin-initialisatie wordt `vendor/` (of `vendor/site-packages/`) vóór imports aan `sys.path` toegevoegd.

**NFR-06a Vendoring randvoorwaarden**
- Alleen pure-Python dependencies of libraries waarvan we weten dat de binaire delen compatibel zijn met QGIS-systempython mogen vendor'ed worden.
- Neem licentieteksten op (LICENSES of vendor/README.md).

**NFR-07 Versiebeheer van vendored dependencies (updatebeleid)**
- OTLMOW-Model en OTLMOW-converter versie (tag/commit) wordt vastgezet per plugin-release.
- Houd `vendor/LOCK.json` of `vendor/MANIFEST.md` bij met exacte commit/tags en datum.

**NFR-08 Semi-automatische integratie / update procedure**
- Voorzie een script `scripts/update_vendor.py` (documentatie en voorbeeld) dat:
  - leest gewenste versies (bv. `vendor/LOCK.json` of `scripts/vendor-versions.yaml`),
  - clone/copy de repository of download de distributie-artifacten,
  - plaatst de relevante Python modules in `plugin_folder/vendor/`,
  - werkt `vendor/LOCK.json` bij met bron-URL en exacte commit/tag,
  - valideert basisimport (importeert de vendored package in een tijdelijke Python-proces om import errors te detecteren).
- Updates vereisen code-review en test-run; automatische deploys zonder review zijn niet toegestaan.

**NFR-09 Metadata & installability**
- De plugin bevat een geldig `metadata.txt` (of `metadata.json`, afhankelijk van target QGIS) met de verplichte velden: name, qgisMinimumVersion, description, version, author, email, tags en speciaal: `title` of `name` (zorg dat QGIS de vereiste velden ziet). Deze metadata wordt gevalideerd door de repo-scripts (`scripts/check_plugin_structure.py`).

**NFR-10 Ontwikkelingssymlinks & cross-platform dev workflow**
- Documenteer hoe ontwikkelaars de plugin als symlink/junction toevoegen in QGIS op zowel Linux als Windows. Op Windows kan dit extra rechten of gebruik van NTFS-junctions vereisen. Voeg instructies toe in `README.md`.

---

## Acceptatiecriteria (Given/When/Then) — aangepast
**AC-01 (FR-01)**
- Given: 0 of >1 selectie bij "Copy parallel"
- When: gebruiker activeert modus of klikt om te creëren
- Then: er wordt niets aangemaakt en een duidelijke melding wordt getoond

**AC-02 (FR-02/FR-05)**
- Given: exact één bronlijn geselecteerd en modus "Copy parallel" is aan
- When: gebruiker klikt op punt P
- Then: er verschijnt exact één nieuwe lijn in de beheerde laag die parallel is aan de bronlijn en door P gaat (of faalt met duidelijk bericht)

**AC-03 (FR-05)**
- Given: berekende lijn heeft lengte < 1,0 m
- When: probeert toe te voegen
- Then: feature wordt niet toegevoegd en gebruiker krijgt melding

**AC-04 (FR-06)**
- Given: project-CRS ≠ bronlaag-CRS
- When: gebruiker maakt parallelle lijnen en exporteert
- Then: geometrie en lengtevalidatie blijven correct (in meters)

**AC-05 (FR-07/FR-08)**
- Given: beheerde laag bevat n lijnen
- When: gebruiker exporteert
- Then: outputbestand bevat n assets/objecten en voldoet aan OTL-regels (of faalt expliciet met duidelijke melding)

## Attributen & UI-knoppen
Deze sectie specificeert de attributen die in de beheerde laag aanwezig kunnen zijn en de belangrijkste UI-knoppen die de plugin aanbiedt om lijnen te beheren.

Attributen (voorstel; schema kan later verfijnd worden):
- id (intern)
- source_layer (naam bronlaag)
- source_fid (originele feature id)
- geometry_length_m (afgeleide lengte in meters)
- position (links/midden/rechts) — keuzewaarde
- type (bv. markeringstype) — keuzewaarde
- coprocode (string / code)
- color (hex of naam)
- status (draft/validated/exported)
- created_by (user/automation)
- created_at (timestamp)
- comment (vrij tekst)

Extra plugin-knoppen / UI-elementen (voorstel):
- Import selected — importeer geselecteerde features naar de beheerde laag
- Copy parallel — activeer modaliteit voor click-to-create offset
- Merge selected — combineer geselecteerde lijnen in de beheerde laag (vermijdt dubbele punten)
- Split selected — splits een geselecteerde lijn in meerdere lijnen en kopieer/modify attributen
- Export OTL — exporteer de beheerde laag naar OTL via OTLMOW-converter
- Settings — open plugin instellingen (vendor policy, default CRS, storage optie memory/geopackage)

Deze attributen en knoppen kunnen tijdens implementatie verder worden aangepast; ze vormen nu de basis voor de UI en het schema van de beheerde laag.

**AC-06 (NFR-06)**
- Given: plugin geïnstalleerd op een schone QGIS-installatie
- When: gebruiker exporteert
- Then: export gebruikt vendored OTLMOW-Model/Converter succesvol, of faalt met duidelijke melding naar documentatie

**AC-07 (NFR-05)**
- Given: dezelfde pluginversie
- When: installatie/gebruik op Linux en op Windows
- Then: kernflow werkt op beide platformen

**AC-08 (NFR-07)**
- Given: vendored packages worden geüpdatet via de update-procedure
- When: procedure is uitgevoerd
- Then: `vendor/LOCK.json` bevat exacte versies, plugin start zonder import errors en relevante tests draaien groen

---

## Teststrategie (aangevuld)
- Unit tests:
  - offset-berekening en helpers (zonder QGIS)
  - lengtevalidatie (met simulaties in verschillende CRS)
  - OTL-mapping (zolang OTLMOW-Model stabiel is; bij vendoring: import van vendored module in venv tijdens CI)
- Integratietests (PyQGIS):
  - aanmaken beheerde laag, toevoegen features,
  - copy-parallel end-to-end in een QGIS test-omgeving,
  - export end-to-end met vendored OTLMOW libraries.
- Lint/structure checks:
  - `scripts/check_plugin_structure.py` moet metadata validatie doen (inclusief `title`/`name`).

## Deployment & developer notes (kort)
- `vendor/README.md` beschrijft hoe vendoren werkt en welke bestanden gelockt zijn.
- `README.md` beschrijft symlink/junction stappen voor development op Linux en Windows.
- CI moet ten minste:
  - checken dat `metadata.txt` aanwezig en valide is,
  - unit tests draaien,
  - (optioneel) integratie export-test uitvoeren op een geschikte runner.

## Appendix: Aanbevelingen voor implementatie-details
- Gebruik `QgsGeometry.closestSegmentWithContext` of `QgsGeometry.project` / `line.interpolate` om het offset referentiepunt te vinden.
- Gebruik `QgsDistanceArea` voor geodetische lengtemetingen indien nodig.
- Houd PyQGIS-specifieke code in een adaptermodule (bv. `plugin/adapter/qgis_adapter.py`) zodat kernalgoritmes onafhankelijk getest kunnen worden.
- Zorg dat `vendor/` toegevoegd wordt aan `sys.path` vóór de eerste import van vendored libraries, en log een duidelijke foutmelding als import faalt, met link naar vendor/README.md.

---
