# language: de

Funktionalität: Basisdaten

Um BIM-Daten anzusehen
Für alle beteiligten Akteure
Wir brauchen eine IFC-Datei


Szenario: Bereitstellen von IFC-Daten
 * Die IFC-Daten müssen das "IFC2X3" Schema benutzen


Szenario: Layer
 # * Alle "{ifc_class}" Bauteile haben einen zugeordneten Layer
 * Alle "IfcBuildingElement" Bauteile haben einen zugeordneten Layer
 * Kein "IfcBuildingElement" Bauteil hat einen Layer mit dem Namen "Undefiniert"
 # passiert, wenn Layer im Projekt fehlt
