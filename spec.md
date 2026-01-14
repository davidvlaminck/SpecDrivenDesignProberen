# Introductie
Dit project heeft als doel een QGIS plugin te maken om OTL conforme markeringen aan te maken, wijzigen of te verwijderen.

# Hoe een gebruiker de plugin gebruikt 
- selecteert of tekent een lijn in QGIS
- activeert de knop 'copy parallel' (blijft aan staan)
- klikt op één punt buiten de lijn
- de plugin maakt een lijn aan, parallel aan de geselecteerde lijn door het punt, in een door de plugin beheerde laag (=feature class)
- de gebruiker kan de vorige 2 acties herhalen
- de gebruiker kan nu de knop deactiveren om uit de kopieer modus te gaan.
- door op de export knop te klikken, wordt de door de plugin beheerde laag OTL conform geëxporteerd.

# Vereisten
- gebruik maken van QGIS
- zoveel unit testen als mogelijk
- spec driven design implementeren
- ontwikkelen in fases (zo snel mogelijk naar een werkend prototype dat wordt verbeterd)
- gebruik maken van een versiebeheersysteem (git)
- documentatie bijhouden
- OTL conform exporteren
- enkel lijngeometriën langer dan 1 meter zijn geldig
- de plugin moet omgaan met projecties
- de plugin moet gebruiksvriendelijk zijn
