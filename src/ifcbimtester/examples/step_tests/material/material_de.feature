# language: de

Funktionalität: Basisdaten

Um BIM-Daten anzusehen
Für alle beteiligten Akteure
Wir brauchen eine IFC-Datei


Szenario: Bereitstellen von IFC-Daten
 * Die IFC-Daten müssen das "IFC2X3" Schema benutzen


Szenario: Material
 * Alle "IfcBuildingElement" Bauteile haben ein zugeordnetes Material
 # nicht mögich in Allplan, aber in FreeCAD
 # nicht möglich in behave, es muss ein zeichen zwischen den "" sein
 # TODO am besten ein ganz anderer text für das ... name darf nicht leer sein und nur leerzeichen ist eben auch ein leerer namen
 #* Kein "IfcBuildingElement" Bauteil hat ein Material mit dem Namen ""
 # Allplan 2021.1 leeres Material wird als Leerzeichen geschrieben
 * Kein "IfcBuildingElement" Bauteil hat ein Material mit dem Namen " "
