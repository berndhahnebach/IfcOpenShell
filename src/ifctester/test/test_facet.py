# IfcTester - IDS based model auditing
# Copyright (C) 2021-2022 Thomas Krijnen <thomas@aecgeeks.com>, Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcTester.
#
# IfcTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcTester.  If not, see <http://www.gnu.org/licenses/>.


import uuid
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.aggregate
import ifcopenshell.api.classification
import ifcopenshell.api.group
import ifcopenshell.api.material
import ifcopenshell.api.nest
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.type
import ifcopenshell.api.unit
import ifcopenshell.guid
import ifcopenshell.util.pset
import ifctester.facet
from ifctester.facet import Entity, Attribute, Classification, Property, PartOf, Material, Restriction


def set_facet(facet):
    pass


def run(name, *, facet, inst, expected):
    ifctester.facet.get_pset.cache_clear()
    ifctester.facet.get_psets.cache_clear()
    assert bool(facet(inst)) is expected


class TestEntity:
    def test_creating_an_entity_facet(self):
        facet = Entity(name="IfcName")
        assert facet.asdict("applicability") == {"name": {"simpleValue": "IfcName"}}
        facet = Entity(name="IfcName", predefinedType="predefinedType", instructions="instructions")
        assert facet.asdict("requirement") == {
            "name": {"simpleValue": "IfcName"},
            "predefinedType": {"simpleValue": "predefinedType"},
            "@instructions": "instructions",
        }

    def test_filtering_using_an_entity_facet(self):
        set_facet("entity")

        ifc = ifcopenshell.file()
        facet = Entity(name="IFCRABBIT")
        run("Invalid entities always fail", facet=facet, inst=ifc.createIfcWall(), expected=False)

        ifc = ifcopenshell.file()
        facet = Entity(name="IFCWALL")
        run("A matching entity should pass", facet=facet, inst=ifc.createIfcWall(), expected=True)
        ifc = ifcopenshell.file()
        run(
            "An matching entity should pass regardless of predefined type",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="SOLIDWALL"),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run(
            "An entity not matching the specified class should fail",
            facet=facet,
            inst=ifc.createIfcSlab(),
            expected=False,
        )
        # TODO: Some votes to prefer inheritance (For: Moult, Evandro, Artur)
        # Possible argument: CAD tools don't understand IFC
        ifc = ifcopenshell.file()
        run(
            "Subclasses are not considered as matching",
            facet=facet,
            inst=ifc.createIfcWallStandardCase(),
            expected=False,
        )

        facet = Entity(name="IfcWall")
        ifc = ifcopenshell.file()
        run(
            "Entities must be specified as uppercase strings",
            facet=facet,
            inst=ifc.createIfcWall(),
            expected=False,
        )

        facet = Entity(name="IFCWALL", predefinedType="SOLIDWALL")
        ifc = ifcopenshell.file()
        run(
            "A matching predefined type should pass",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="SOLIDWALL"),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run(
            "A null predefined type should always fail a specified predefined types",
            facet=facet,
            inst=ifc.createIfcWall(),
            expected=False,
        )
        ifc = ifcopenshell.file()
        run(
            "An entity not matching a specified predefined type will fail",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="PARTITIONING"),
            expected=False,
        )

        facet = Entity(name="IFCWALL", predefinedType="solidwall")
        ifc = ifcopenshell.file()
        run(
            "A predefined type from an enumeration must be uppercase",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="SOLIDWALL"),
            expected=False,
        )

        facet = Entity(name="IFCWALL", predefinedType="WALDO")
        ifc = ifcopenshell.file()
        run(
            "A predefined type may specify a user-defined object type",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="USERDEFINED", ObjectType="WALDO"),
            expected=True,
        )

        facet = Entity(name="IFCWALL", predefinedType="WALDO")
        ifc = ifcopenshell.file()
        run(
            "User-defined types are checked case sensitively",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="USERDEFINED", ObjectType="waldo"),
            expected=False,
        )

        facet = Entity(name="IFCWALLTYPE", predefinedType="WALDO")
        ifc = ifcopenshell.file()
        run(
            "A predefined type may specify a user-defined element type",
            facet=facet,
            inst=ifc.createIfcWallType(PredefinedType="USERDEFINED", ElementType="WALDO"),
            expected=True,
        )

        facet = Entity(name="IFCTASKTYPE", predefinedType="TASKY")
        ifc = ifcopenshell.file()
        run(
            "A predefined type may specify a user-defined process type",
            facet=facet,
            inst=ifc.createIfcTaskType(PredefinedType="USERDEFINED", ProcessType="TASKY"),
            expected=True,
        )

        facet = Entity(name="IFCWALL", predefinedType="USERDEFINED")
        ifc = ifcopenshell.file()
        run(
            "A predefined type must always specify a meaningful type, not USERDEFINED itself",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="USERDEFINED", ObjectType="WALDO"),
            expected=False,
        )

        ifc = ifcopenshell.file()
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType", predefined_type="X")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[wall], relating_type=wall_type)
        facet = Entity(name="IFCWALL", predefinedType="X")
        run("Inherited predefined types should pass", facet=facet, inst=wall, expected=True)

        ifc = ifcopenshell.file()
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall", predefined_type="X")
        wall_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType", predefined_type="NOTDEFINED")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[wall], relating_type=wall_type)
        facet = Entity(name="IFCWALL", predefinedType="X")
        run("Overridden predefined types should pass", facet=facet, inst=wall, expected=True)

        restriction = Restriction(options={"enumeration": ["IFCWALL", "IFCSLAB"]})
        facet = Entity(name=restriction)
        ifc = ifcopenshell.file()
        run("Entities can be specified as an enumeration 1/3", facet=facet, inst=ifc.createIfcWall(), expected=True)
        ifc = ifcopenshell.file()
        run("Entities can be specified as an enumeration 2/3", facet=facet, inst=ifc.createIfcSlab(), expected=True)
        ifc = ifcopenshell.file()
        run("Entities can be specified as an enumeration 3/3", facet=facet, inst=ifc.createIfcBeam(), expected=False)

        restriction = Restriction(options={"pattern": "IFC.*TYPE"})
        facet = Entity(name=restriction)
        ifc = ifcopenshell.file()
        run(
            "Entities can be specified as a XSD regex pattern 1/2",
            facet=facet,
            inst=ifc.createIfcWall(),
            expected=False,
        )
        ifc = ifcopenshell.file()
        run(
            "Entities can be specified as a XSD regex pattern 2/2",
            facet=facet,
            inst=ifc.createIfcWallType(PredefinedType="USERDEFINED"),
            expected=True,
        )

        restriction = Restriction(options={"pattern": "FOO.*"})
        facet = Entity(name="IFCWALL", predefinedType=restriction)
        ifc = ifcopenshell.file()
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall", predefined_type="FOOBAR")
        run("Restrictions an be specified for the predefined type 1/3", facet=facet, inst=wall, expected=True)
        ifc = ifcopenshell.file()
        wall2 = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall", predefined_type="FOOBAZ")
        run("Restrictions an be specified for the predefined type 2/3", facet=facet, inst=wall2, expected=True)
        ifc = ifcopenshell.file()
        wall3 = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall", predefined_type="BAZFOO")
        run("Restrictions an be specified for the predefined type 3/3", facet=facet, inst=wall3, expected=False)


class TestAttribute:
    def test_creating_an_attribute_facet(self):
        attribute = Attribute(name="name")
        assert attribute.asdict("applicability") == {"name": {"simpleValue": "name"}}
        attribute = Attribute(name="name", value="value")
        assert attribute.asdict("applicability") == {"name": {"simpleValue": "name"}, "value": {"simpleValue": "value"}}
        attribute = Attribute(name="name", value="value", cardinality="required", instructions="instructions")
        assert attribute.asdict("requirement") == {
            "name": {"simpleValue": "name"},
            "value": {"simpleValue": "value"},
            "@cardinality": "required",
            "@instructions": "instructions",
        }

    def test_filtering_using_an_attribute_facet(self):
        set_facet("attribute")

        ifc = ifcopenshell.file()
        facet = Attribute(name="Rabbit")
        run("Invalid attribute names always fail", facet=facet, inst=ifc.createIfcWall(), expected=False)

        ifc = ifcopenshell.file()
        facet = Attribute(name="Name")
        run(
            "Attributes with a string value should pass",
            facet=facet,
            inst=ifc.createIfcWall(Name="Foobar"),
            expected=True,
        )

        ifc = ifcopenshell.file()
        facet = Attribute(name="Name")
        element = ifc.createIfcWall(Name="Foobar")
        run("A required facet checks all parameters as normal", facet=facet, inst=element, expected=True)

        facet = Attribute(name="Name", cardinality="prohibited")
        run("A prohibited facet returns the opposite of a required facet", facet=facet, inst=element, expected=False)
        facet = Attribute(name="Name", cardinality="optional")
        run(
            "An optional facet only checks requirements if there is a value to check 1/2",
            facet=facet,
            inst=element,
            expected=True,
        )
        facet = Attribute(name="Rabbit", cardinality="optional")
        run(
            "An optional facet only checks requirements if there is a value to check 2/2",
            facet=facet,
            inst=element,
            expected=True,
        )

        ifc = ifcopenshell.file()
        facet = Attribute(name="Name")
        run("Attributes with null values always fail", facet=facet, inst=ifc.createIfcWall(), expected=False)
        # The logic is that unfortunately most BIM users cannot differentiate between the two.
        ifc = ifcopenshell.file()
        run("Attributes with empty strings always fail", facet=facet, inst=ifc.createIfcWall(Name=""), expected=False)

        facet = Attribute(name="CountValue")
        ifc = ifcopenshell.file()
        run(
            "Attributes with a zero number have meaning and should pass",
            facet=facet,
            inst=ifc.createIfcQuantityCount(Name="Foobar", CountValue=0),
            expected=True,
        )

        facet = Attribute(name="IsCritical")
        ifc = ifcopenshell.file()
        element = ifc.createIfcTaskTime(IsCritical=True)
        run("Attributes with a boolean true should pass", facet=facet, inst=element, expected=True)
        element.IsCritical = False
        run("Attributes with a boolean false should pass", facet=facet, inst=element, expected=True)

        facet = Attribute(name="RelatingPriorities")
        ifc = ifcopenshell.file()
        run(
            "Attributes with an empty list always fail",
            facet=facet,
            inst=ifc.createIfcRelConnectsPathElements(
                RelatingElement=ifc.createIfcWall(),
                RelatedElement=ifc.createIfcWall(),
                RelatingPriorities=[],
                RelatedPriorities=[],
                RelatedConnectionType="ATSTART",
                RelatingConnectionType="ATEND",
            ),
            expected=False,
        )

        facet = Attribute(name="LayerStyles")
        ifc = ifcopenshell.file()
        item = ifc.createIfcCartesianPoint([0.0, 0.0, 0.0])
        layer = ifc.createIfcPresentationLayerWithStyle("Foo", None, [item], None, True, False, False, [])
        run("Attributes with an empty set always fail", facet=facet, inst=layer, expected=False)

        layer.LayerOn = "UNKNOWN"
        facet = Attribute(name="LayerOn")
        run("Attributes with a logical unknown always fail", facet=facet, inst=layer, expected=False)

        facet = Attribute(name="ScheduleDuration")
        ifc = ifcopenshell.file()
        element = ifc.createIfcTaskTime(ScheduleDuration="P0D")
        run("Attributes with a zero duration should pass", facet=facet, inst=element, expected=True)

        facet = Attribute(name="TaskTime")
        ifc = ifcopenshell.file()
        element = ifc.createIfcTask(IsMilestone=True, TaskTime=ifc.createIfcTaskTime())
        run("Attributes referencing an object should pass", facet=facet, inst=element, expected=True)

        facet = Attribute(name="DiffuseColour")
        ifc = ifcopenshell.file()
        rgb = ifc.createIfcColourRgb(None, 1, 1, 1)
        run(
            "Attributes with a select referencing an object should pass",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRendering(
                SurfaceColour=rgb, ReflectanceMethod="FLAT", DiffuseColour=ifc.createIfcColourRgb(None, 1, 1, 1)
            ),
            expected=True,
        )

        ifc = ifcopenshell.file()
        rgb = ifc.createIfcColourRgb(None, 1, 1, 1)
        run(
            "Attributes with a select referencing a primitive should pass",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRendering(
                SurfaceColour=rgb, ReflectanceMethod="FLAT", DiffuseColour=ifc.createIfcNormalisedRatioMeasure(0.5)
            ),
            expected=True,
        )

        ifc = ifcopenshell.file()
        facet = Attribute(name="EngagedIn")
        person = ifc.createIfcPerson()
        organisation = ifc.createIfcOrganization(Name="Foo")
        ifc.createIfcPersonAndOrganization(ThePerson=person, TheOrganization=organisation)
        run("Inverse attributes cannot be checked and always fail", facet=facet, inst=person, expected=False)

        ifc = ifcopenshell.file()
        facet = Attribute(name="Dim")
        run(
            "Derived attributes cannot be checked and always fail",
            facet=facet,
            inst=ifc.createIfcCartesianPoint([0.0, 0.0, 0.0]),
            expected=False,
        )

        facet = Attribute(name="Name", value="Foobar")
        ifc = ifcopenshell.file()
        run(
            "Attributes should check strings case sensitively 1/2",
            facet=facet,
            inst=ifc.createIfcWall(Name="Foobar"),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run(
            "Attributes should check strings case sensitively 2/2",
            facet=facet,
            inst=ifc.createIfcWall(Name="foobar"),
            expected=False,
        )

        ifc = ifcopenshell.file()
        facet = Attribute(name="Name", value="♫Don'tÄrgerhôtelЊет")
        run(
            "Non-ascii characters are treated without encoding",
            facet=facet,
            inst=ifc.createIfcWall(Name="♫Don'tÄrgerhôtelЊет"),
            expected=True,
        )

        facet = Attribute(name="TaskTime", value="Foobar")
        ifc = ifcopenshell.file()
        run(
            "Value checks always fail for objects",
            facet=facet,
            inst=ifc.createIfcTask(IsMilestone=False, TaskTime=ifc.createIfcTaskTime()),
            expected=False,
        )

        facet = Attribute(name="DiffuseColour", value="Foobar")
        ifc = ifcopenshell.file()
        rgb = ifc.createIfcColourRgb(None, 1, 1, 1)
        run(
            "Value checks always fail for selects",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRendering(
                SurfaceColour=rgb, ReflectanceMethod="FLAT", DiffuseColour=ifc.createIfcNormalisedRatioMeasure(0.5)
            ),
            expected=False,
        )

        facet = Attribute(name="Coordinates", value="Foobar")
        ifc = ifcopenshell.file()
        run(
            "Value checks always fail for lists",
            facet=facet,
            inst=ifc.createIfcCartesianPoint([0.0, 0.0, 0.0]),
            expected=False,
        )

        ifc = ifcopenshell.file()
        ns = uuid.UUID("b59aa156-82a4-4b4c-a6e5-3d04a0236af9")
        element = ifc.createIfcWall()
        element.GlobalId = ifcopenshell.guid.compress(uuid.uuid5(ns, str(element.id())).hex)
        facet = Attribute(name="GlobalId", value=element.GlobalId)
        run(
            "GlobalIds are treated as strings and not expanded",
            facet=facet,
            inst=element,
            expected=True,
        )

        # 255 characters
        identifier = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345"
        facet = Attribute(name="Identification", value=identifier + "_extra_characters")
        ifc = ifcopenshell.file()
        run(
            "IDS does not handle string truncation such as for identifiers",
            facet=facet,
            inst=ifc.createIfcPerson(Identification=identifier),
            expected=False,
        )

        facet = Attribute(name="RefractionIndex", value="42")
        ifc = ifcopenshell.file()
        run(
            "Numeric values are checked using type casting 1/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42),
            expected=True,
        )
        facet = Attribute(name="RefractionIndex", value="42.")
        ifc = ifcopenshell.file()
        run(
            "Numeric values are checked using type casting 2/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.0),
            expected=True,
        )
        facet = Attribute(name="RefractionIndex", value="42.0")
        ifc = ifcopenshell.file()
        run(
            "Numeric values are checked using type casting 3/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.0),
            expected=True,
        )
        facet = Attribute(name="RefractionIndex", value="42")
        ifc = ifcopenshell.file()
        run(
            "Numeric values are checked using type casting 4/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.3),
            expected=False,
        )
        facet = Attribute(name="RefractionIndex", value="42,3")
        ifc = ifcopenshell.file()
        run(
            "Only specifically formatted numbers are allowed 1/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.3),
            expected=False,
        )
        facet = Attribute(name="RefractionIndex", value="123,4.5")
        ifc = ifcopenshell.file()
        run(
            "Only specifically formatted numbers are allowed 2/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=1234.5),
            expected=False,
        )
        facet = Attribute(name="RefractionIndex", value="1.2345e3")
        ifc = ifcopenshell.file()
        run(
            "Only specifically formatted numbers are allowed 3/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=1234.5),
            expected=True,
        )
        facet = Attribute(name="RefractionIndex", value="1.2345E3")
        ifc = ifcopenshell.file()
        run(
            "Only specifically formatted numbers are allowed 4/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=1234.5),
            expected=True,
        )

        facet = Attribute(name="RefractionIndex", value="42.")
        ifc = ifcopenshell.file()
        run(
            "Floating point numbers are compared with a 1e-6 tolerance 1/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.0 * (1.0 + 1e-6)),
            expected=True,
        )
        run(
            "Floating point numbers are compared with a 1e-6 tolerance 2/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.0 * (1.0 - 1e-6)),
            expected=True,
        )
        run(
            "Floating point numbers are compared with a 1e-6 tolerance 3/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.0 * (1.0 + 2e-6)),
            expected=False,
        )
        run(
            "Floating point numbers are compared with a 1e-6 tolerance 4/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.0 * (1.0 - 2e-6)),
            expected=False,
        )

        facet = Attribute(name="NumberOfRisers", value="42")
        ifc = ifcopenshell.file()
        run(
            "Integers follow the same rules as numbers",
            facet=facet,
            inst=ifc.createIfcStairFlight(NumberOfRisers=42),
            expected=True,
        )
        facet = Attribute(name="NumberOfRisers", value="42.0")
        ifc = ifcopenshell.file()
        run(
            "Integers follow the same rules as numbers 2/2",
            facet=facet,
            inst=ifc.createIfcStairFlight(NumberOfRisers=42),
            expected=True,
        )

        facet = Attribute(name="NumberOfRisers", value="42.3")
        ifc = ifcopenshell.file()
        run(
            "Specifying a float when the value is an integer will fail",
            facet=facet,
            inst=ifc.createIfcStairFlight(NumberOfRisers=42),
            expected=False,
        )

        facet = Attribute(name="IsMilestone", value="true")
        ifc = ifcopenshell.file()
        element = ifc.createIfcTask(IsMilestone=False)
        run("Booleans must be specified as lowercase strings 1/3", facet=facet, inst=element, expected=False)
        facet = Attribute(name="IsMilestone", value="false")
        run("Booleans must be specified as lowercase strings 2/3", facet=facet, inst=element, expected=True)
        facet = Attribute(name="IsMilestone", value="False")
        run("Booleans must be specified as lowercase strings 2/3", facet=facet, inst=element, expected=False)

        facet = Attribute(name="IsMilestone", value="0")
        run("Booleans can be specified as a 0 or 1 1/2", facet=facet, inst=element, expected=True)
        facet = Attribute(name="IsMilestone", value="1")
        run("Booleans can be specified as a 0 or 1 2/2", facet=facet, inst=element, expected=False)

        facet = Attribute(name="EditionDate", value="2022-01-01")
        ifc = ifcopenshell.file()
        run(
            "Dates are treated as strings 1/2",
            facet=facet,
            inst=ifc.createIfcClassification(Name="Name", EditionDate="2022-01-01"),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run(
            "Dates are treated as strings 1/2",
            facet=facet,
            inst=ifc.createIfcClassification(Name="Name", EditionDate="2022-01-01+00:00"),
            expected=False,
        )

        facet = Attribute(name="ScheduleDuration", value="PT16H")
        ifc = ifcopenshell.file()
        run(
            "Durations are treated as strings 1/2",
            facet=facet,
            inst=ifc.createIfcTaskTime(Name="Name", ScheduleDuration="PT16H"),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run(
            "Durations are treated as strings 2/2",
            facet=facet,
            inst=ifc.createIfcTaskTime(Name="Name", ScheduleDuration="P2D"),
            expected=False,
        )

        restriction = Restriction(options={"pattern": ".*Name.*"})
        facet = Attribute(name=restriction)
        ifc = ifcopenshell.file()
        run(
            "Name restrictions will match any result 1/3",
            facet=facet,
            inst=ifc.createIfcMaterialLayerSet(
                MaterialLayers=[ifc.createIfcMaterialLayer(LayerThickness=1)], LayerSetName="Foo"
            ),
            expected=True,
        )
        restriction = Restriction(options={"enumeration": ["Name", "Description"]})
        facet = Attribute(name=restriction)
        ifc = ifcopenshell.file()
        run(
            "Name restrictions will match any result 2/3",
            facet=facet,
            inst=ifc.createIfcWall(Name="Foo"),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run(
            "Name restrictions will match any result 3/3",
            facet=facet,
            inst=ifc.createIfcWall(Description="Bar"),
            expected=True,
        )

        restriction = Restriction(options={"enumeration": ["Foo", "Bar"]})
        facet = Attribute(name="Name", value=restriction)
        ifc = ifcopenshell.file()
        run("Value restrictions may be used 1/3", facet=facet, inst=ifc.createIfcWall(Name="Foo"), expected=True)
        ifc = ifcopenshell.file()
        run("Value restrictions may be used 2/3", facet=facet, inst=ifc.createIfcWall(Name="Bar"), expected=True)
        ifc = ifcopenshell.file()
        run("Value restrictions may be used 3/3", facet=facet, inst=ifc.createIfcWall(Name="Foobar"), expected=False)

        ifc = ifcopenshell.file()
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[wall], relating_type=wall_type)
        wall_type.Description = "Foobar"
        facet = Attribute(name="Description", value="Foobar")
        run("Attributes are not inherited by the occurrence", facet=facet, inst=wall, expected=False)

        restriction = Restriction(options={"enumeration": ["42", "43"]})
        facet = Attribute(name="RefractionIndex", value=restriction)
        ifc = ifcopenshell.file()
        run(
            "Typecast checking may also occur within enumeration restrictions",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42),
            expected=True,
        )

        restriction = Restriction(options={"minInclusive": 42, "maxInclusive": 42}, base="decimal")
        facet = Attribute(name="RefractionIndex", value=restriction)
        ifc = ifcopenshell.file()
        run(
            "Strict numeric checking may be done with a bounds restriction",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42),
            expected=True,
        )


class TestClassification:
    def test_creating_a_classification_facet(self):
        facet = Classification(system="system")
        assert facet.asdict("requirement") == {"system": {"simpleValue": "system"}, "@cardinality": "required"}
        facet = Classification(value="value", system="system")
        assert facet.asdict("requirement") == {
            "value": {"simpleValue": "value"},
            "system": {"simpleValue": "system"},
            "@cardinality": "required",
        }
        facet = Classification(
            value="value",
            system="system",
            uri="https://test.com",
            cardinality="required",
            instructions="instructions",
        )
        assert facet.asdict("requirement") == {
            "value": {"simpleValue": "value"},
            "system": {"simpleValue": "system"},
            "@uri": "https://test.com",
            "@cardinality": "required",
            "@instructions": "instructions",
        }

    def test_filtering_using_a_classification_facet(self):
        set_facet("classification")

        library = ifcopenshell.file()
        system_a = library.createIfcClassification(Name="Foobar")
        ref1 = library.createIfcClassificationReference(Identification="1", ReferencedSource=system_a)
        ref11 = library.createIfcClassificationReference(Identification="11", ReferencedSource=ref1)
        ref2 = library.createIfcClassificationReference(Identification="2", ReferencedSource=system_a)
        ref22 = library.createIfcClassificationReference(Identification="22", ReferencedSource=ref2)
        system_b = library.createIfcClassification(Name="Foobaz")
        refx = library.createIfcClassificationReference(Identification="X", ReferencedSource=system_b)

        ifc = ifcopenshell.file()
        project = ifc.createIfcProject()
        system_a = ifcopenshell.api.classification.add_classification(ifc, classification=system_a)
        element0 = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        element1 = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSlab")
        ifcopenshell.api.classification.add_reference(ifc, products=[element1], reference=ref1, classification=system_a)
        element11 = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcColumn")
        ifcopenshell.api.classification.add_reference(
            ifc, products=[element11], reference=ref11, classification=system_a
        )
        element22 = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeam")
        ifcopenshell.api.classification.add_reference(
            ifc,
            products=[element22],
            reference=ref22,
            classification=system_a,
            is_lightweight=False,
        )
        material = ifc.createIfcMaterial(Name="Material")
        ifcopenshell.api.classification.add_reference(ifc, products=[material], reference=ref1, classification=system_a)

        facet = Classification(system="Foobar")
        run(
            "A classification facet with no value matches any classification 1/2",
            facet=facet,
            inst=element0,
            expected=False,
        )
        run(
            "A classification facet with no value matches any classification 2/2",
            facet=facet,
            inst=element1,
            expected=True,
        )

        run("A required facet checks all parameters as normal", facet=facet, inst=element1, expected=True)
        facet = Classification(system="Foobar", cardinality="prohibited")
        run("A prohibited facet returns the opposite of a required facet", facet=facet, inst=element1, expected=False)
        facet = Classification(system="Foobar", cardinality="optional")
        run(
            "An optional facet only checks requirements if there is a value to check 1/2",
            facet=facet,
            inst=element0,
            expected=True,
        )
        facet = Classification(system="Foobar", cardinality="optional")
        run(
            "An optional facet only checks requirements if there is a value to check 2/2",
            facet=facet,
            inst=element1,
            expected=True,
        )

        facet = Classification(system="Foobar", value="1")
        run(
            "Values should match exactly if lightweight classifications are used",
            facet=facet,
            inst=element1,
            expected=True,
        )

        facet = Classification(system="Foobar", value="2")
        run(
            "Values match subreferences if full classifications are used (e.g. EF_25_10 should match EF_25_10_25, EF_25_10_30, etc)",
            facet=facet,
            inst=element22,
            expected=True,
        )

        facet = Classification(system="Foobar", value="1")
        run(
            "Non-rooted resources that have external classification references should also pass",
            facet=facet,
            inst=material,
            expected=True,
        )

        facet = Classification(system="Foobar")
        run("Systems should match exactly 1/5", facet=facet, inst=project, expected=True)
        run("Systems should match exactly 2/5", facet=facet, inst=element0, expected=False)
        run("Systems should match exactly 3/5", facet=facet, inst=element1, expected=True)
        run("Systems should match exactly 4/5", facet=facet, inst=element11, expected=True)
        run("Systems should match exactly 5/5", facet=facet, inst=element22, expected=True)

        restriction = Restriction(options={"pattern": "1.*"})
        facet = Classification(system="Foobar", value=restriction)
        run("Restrictions can be used for values 1/3", facet=facet, inst=element1, expected=True)
        run("Restrictions can be used for values 2/3", facet=facet, inst=element11, expected=True)
        run("Restrictions can be used for values 3/3", facet=facet, inst=element22, expected=False)

        restriction = Restriction(options={"pattern": "Foo.*"})
        facet = Classification(system=restriction)
        run("Restrictions can be used for systems 1/2", facet=facet, inst=element0, expected=False)
        run("Restrictions can be used for systems 2/2", facet=facet, inst=element1, expected=True)

        facet = Classification(system="Foobar", value="1")
        run(
            "Both system and value must match (all, not any) if specified 1/2",
            facet=facet,
            inst=element1,
            expected=True,
        )
        run(
            "Both system and value must match (all, not any) if specified 2/2",
            facet=facet,
            inst=element11,
            expected=False,
        )

        # IFC doesn't yet formally specify how inheritance and overrides work here. We follow these rules:
        # https://github.com/buildingSMART/IFC4.3.x-development/issues/475
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[wall], relating_type=wall_type)
        ifcopenshell.api.classification.add_reference(ifc, products=[wall], reference=ref11, classification=system_a)
        ifcopenshell.api.classification.add_reference(
            ifc, products=[wall_type], reference=ref22, classification=system_a
        )

        system_b = ifcopenshell.api.classification.add_classification(ifc, classification=system_b)
        ifcopenshell.api.classification.add_reference(
            ifc, products=[wall_type], reference=refx, classification=system_b
        )

        facet = Classification(system="Foobar", value="11")
        run("Occurrences override the type classification per system 1/3", facet=facet, inst=wall, expected=True)
        facet = Classification(system="Foobar", value="22")
        run("Occurrences override the type classification per system 2/3", facet=facet, inst=wall, expected=False)
        facet = Classification(system="Foobaz", value="X")
        run("Occurrences override the type classification per system 3/3", facet=facet, inst=wall, expected=True)


class TestProperty:
    def test_creating_a_property_facet(self):
        facet = Property()
        assert facet.asdict("requirement") == {
            "propertySet": {"simpleValue": "Property_Set"},
            "baseName": {"simpleValue": "PropertyName"},
            "@cardinality": "required",
        }
        facet = Property(
            propertySet="propertySet",
            baseName="baseName",
            value="value",
            dataType="dataType",
            uri="https://test.com",
            cardinality="required",
            instructions="instructions",
        )
        assert facet.asdict("requirement") == {
            "propertySet": {"simpleValue": "propertySet"},
            "baseName": {"simpleValue": "baseName"},
            "value": {"simpleValue": "value"},
            "@dataType": "DATATYPE",
            "@uri": "https://test.com",
            "@cardinality": "required",
            "@instructions": "instructions",
        }

    def test_filtering_using_a_property_facet(self):
        set_facet("property")

        ifc = self.setup_ifc()

        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCLABEL")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        run("Elements with no properties always fail", facet=facet, inst=element, expected=False)
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"AnotherProperty": "AnotherValue"})
        run("Elements with a matching pset but no property also fail", facet=facet, inst=element, expected=False)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"AnotherProperty": None})
        run("Properties with a null value fail", facet=facet, inst=element, expected=False)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "Bar"})
        run("A name check will match any property with any string value", facet=facet, inst=element, expected=True)

        ifc = self.setup_ifc()
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCLABEL")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "Bar"})
        run("A required facet checks all parameters as normal", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCLABEL", cardinality="prohibited")
        run("A prohibited facet returns the opposite of a required facet", facet=facet, inst=element, expected=False)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCLABEL", cardinality="optional")
        run(
            "An optional facet only checks requirements if there is a value to check 1/2",
            facet=facet,
            inst=element,
            expected=True,
        )
        facet = Property(propertySet="Foo_Bar", baseName="Bar", dataType="IFCLABEL", cardinality="optional")
        run(
            "An optional facet only checks requirements if there is a value to check 2/2",
            facet=facet,
            inst=element,
            expected=True,
        )

        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ""})
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCLABEL")
        run("An empty string is considered falsey and will not pass", facet=facet, inst=element, expected=False)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcLogical("UNKNOWN")})
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCLOGICAL")
        run("A logical unknown is considered falsey and will not pass", facet=facet, inst=element, expected=False)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcDuration("P0D")})
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCDURATION")
        run("A zero duration will pass", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCBOOLEAN")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcBoolean(True)})
        run("A property set to true will pass a name check", facet=facet, inst=element, expected=True)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": False})
        run(
            "A property set to false is still considered a value and will pass a name check",
            facet=facet,
            inst=element,
            expected=True,
        )

        ifc = self.setup_ifc()
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="Bar", dataType="IFCLABEL")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "Bar"})
        run("Specifying a value performs a case-sensitive match 1/2", facet=facet, inst=element, expected=True)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "bar"})
        run("Specifying a value performs a case-sensitive match 2/2", facet=facet, inst=element, expected=False)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "Baz"})
        run("Specifying a value fails against different values", facet=facet, inst=element, expected=False)

        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="♫Don'tÄrgerhôtelЊет", dataType="IFCLABEL")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "♫Don'tÄrgerhôtelЊет"})
        run("Non-ascii characters are treated without encoding", facet=facet, inst=element, expected=True)

        identifier = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345"
        facet = Property(
            propertySet="Foo_Bar", baseName="Foo", value=identifier + "_extra_characters", dataType="IFCIDENTIFIER"
        )
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcIdentifier(identifier)})
        run("IDS does not handle string truncation such as for identifiers", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="1", dataType="IFCLABEL")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "1"})
        run("A number specified as a string is treated as a string", facet=facet, inst=element, expected=True)

        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="42", dataType="IFCINTEGER")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcInteger(42)})
        run("Integer values are checked using type casting 1/4", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="42.", dataType="IFCINTEGER")
        run("Integer values are checked using type casting 2/4", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="42.0", dataType="IFCINTEGER")
        run("Integer values are checked using type casting 3/4", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="42.3", dataType="IFCINTEGER")
        run("Integer values are checked using type casting 4/4", facet=facet, inst=element, expected=False)

        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="42", dataType="IFCREAL")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcReal(42.0)})
        run("Real values are checked using type casting 1/3", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="42.0", dataType="IFCREAL")
        run("Real values are checked using type casting 2/3", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="42.3", dataType="IFCREAL")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcReal(42.3)})
        run("Real values are checked using type casting 3/3", facet=facet, inst=element, expected=True)

        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="42,3", dataType="IFCREAL")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcReal(42.3)})
        run("Only specifically formatted numbers are allowed 1/4", facet=facet, inst=element, expected=False)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="123,4.5", dataType="IFCREAL")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcReal(1234.5)})
        run("Only specifically formatted numbers are allowed 2/4", facet=facet, inst=element, expected=False)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="1.2345e3", dataType="IFCREAL")
        run("Only specifically formatted numbers are allowed 3/4", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="1.2345E3", dataType="IFCREAL")
        run("Only specifically formatted numbers are allowed 4/4", facet=facet, inst=element, expected=True)

        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="42.", dataType="IFCREAL")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcReal(42.0 * (1.0 + 1e-6))})
        run("Floating point numbers are compared with a 1e-6 tolerance 1/4", facet=facet, inst=element, expected=True)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcReal(42.0 * (1.0 - 1e-6))})
        run("Floating point numbers are compared with a 1e-6 tolerance 2/4", facet=facet, inst=element, expected=True)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcReal(42.0 * (1.0 + 2e-6))})
        run("Floating point numbers are compared with a 1e-6 tolerance 3/4", facet=facet, inst=element, expected=False)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcReal(42.0 * (1.0 - 2e-6))})
        run("Floating point numbers are compared with a 1e-6 tolerance 4/4", facet=facet, inst=element, expected=False)

        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="true", dataType="IFCBOOLEAN")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcBoolean(False)})
        run("Booleans must be specified as uppercase strings 1/3", facet=facet, inst=element, expected=False)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="false", dataType="IFCBOOLEAN")
        run("Booleans must be specified as uppercase strings 2/3", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="False", dataType="IFCBOOLEAN")
        run("Booleans must be specified as uppercase strings 3/3", facet=facet, inst=element, expected=False)

        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="0", dataType="IFCBOOLEAN")
        run("Booleans can be specified as as a 0 or 1 1/2", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="1", dataType="IFCBOOLEAN")
        run("Booleans can be specified as as a 0 or 1 2/2", facet=facet, inst=element, expected=False)

        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="2022-01-01", dataType="IFCDATE")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcDate("2022-01-01")})
        run("Dates are treated as strings 1/2", facet=facet, inst=element, expected=True)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcDate("2022-01-01+00:00")})
        run("Dates are treated as strings 2/2", facet=facet, inst=element, expected=False)

        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="PT16H", dataType="IFCDURATION")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcDuration("PT16H")})
        run("Durations are treated as strings 1/2", facet=facet, inst=element, expected=True)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcDuration("P2D")})
        run("Durations are treated as strings 1/2", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Pset_WallCommon")
        pset_template = ifcopenshell.util.pset.get_template("IFC4").get_by_name("Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(
            ifc,
            pset=pset,
            properties={"Status": ["EXISTING", "DEMOLISH"]},
            pset_template=pset_template,
        )
        facet = Property(propertySet="Pset_WallCommon", baseName="Status", value="EXISTING", dataType="IFCLABEL")
        run("Any matching value in an enumerated property will pass 1/3", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Pset_WallCommon", baseName="Status", value="DEMOLISH", dataType="IFCLABEL")
        run("Any matching value in an enumerated property will pass 2/3", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Pset_WallCommon", baseName="Status", value="NEW", dataType="IFCLABEL")
        run("Any matching value in an enumerated property will pass 3/3", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        list_property = ifc.createIfcPropertyListValue(
            Name="Foo", ListValues=[ifc.createIfcLabel("X"), ifc.createIfcLabel("Y")]
        )
        pset.HasProperties = [list_property]
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="X", dataType="IFCLABEL")
        run("Any matching value in a list property will pass 1/3", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="Y", dataType="IFCLABEL")
        run("Any matching value in a list property will pass 2/3", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="Z", dataType="IFCLABEL")
        run("Any matching value in a list property will pass 3/3", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        bounded_property = ifc.createIfcPropertyBoundedValue(
            Name="Foo",
            UpperBoundValue=ifc.createIfcLengthMeasure(5000),
            LowerBoundValue=ifc.createIfcLengthMeasure(1000),
            SetPointValue=ifc.createIfcLengthMeasure(3000),
        )
        pset.HasProperties = [bounded_property]
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="1", dataType="IFCLENGTHMEASURE")
        run("Any matching value in a bounded property will pass 1/4", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="5", dataType="IFCLENGTHMEASURE")
        run("Any matching value in a bounded property will pass 2/4", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="3", dataType="IFCLENGTHMEASURE")
        run("Any matching value in a bounded property will pass 3/4", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="2", dataType="IFCLENGTHMEASURE")
        run("Any matching value in a bounded property will pass 4/4", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        table_property = ifc.createIfcPropertyTableValue(
            Name="Foo", DefiningValues=[ifc.createIfcLabel("X")], DefinedValues=[ifc.createIfcLengthMeasure(1000)]
        )
        pset.HasProperties = [table_property]
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="X", dataType="IFCLABEL")
        run("Any matching value in a table property will pass 1/3", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="1", dataType="IFCLENGTHMEASURE")
        run("Any matching value in a table property will pass 2/3", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="Y", dataType="IFCLABEL")
        run("Any matching value in a table property will pass 3/3", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        pset.HasProperties = [ifc.createIfcPropertyReferenceValue(Name="Foo")]
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCLABEL")
        run("Reference properties are treated as objects and not supported", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcDoor")
        pset = ifc.create_entity(
            "IfcDoorPanelProperties",
            GlobalId=ifcopenshell.guid.new(),
            Name="Foo_Bar",
            PanelOperation="SWINGING",
            PanelPosition="LEFT",
        )
        ifc.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[element],
            RelatingPropertyDefinition=pset,
        )
        facet = Property(
            propertySet="Foo_Bar", baseName="PanelOperation", value="SWINGING", dataType="IFCDOORPANELOPERATIONENUM"
        )
        run("Predefined properties are supported but discouraged 1/2", facet=facet, inst=element, expected=True)
        facet = Property(
            propertySet="Foo_Bar", baseName="PanelOperation", value="SWONGING", dataType="IFCDOORPANELOPERATIONENUM"
        )
        run("Predefined properties are supported but discouraged 2/2", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCLENGTHMEASURE")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_qto(ifc, qto=qto, properties={"Foo": ifc.createIfcLengthMeasure(42)})
        run("A name check will match any quantity with any value", facet=facet, inst=element, expected=True)
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCAREAMEASURE")
        run("Quantities must also match the appropriate measure", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        complex_property = ifc.createIfcComplexProperty(Name="Foo", UsageName="RabbitAgilityTraining")
        ifcopenshell.api.pset.edit_pset(ifc, pset=complex_property, properties={"Rabbits": "Awesome"})
        pset.HasProperties = [complex_property]
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCLABEL")
        run("Complex properties are not supported 1/2", facet=facet, inst=element, expected=False)
        facet = Property(propertySet="Foo", baseName="Rabbits", dataType="IFCLABEL")
        run("Complex properties are not supported 2/2", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(ifc, product=element, name="Foo_Bar")
        complex_quantity = ifc.createIfcPhysicalComplexQuantity(Name="Foo", Discrimination="FurThickness")
        ifcopenshell.api.pset.edit_qto(
            ifc, qto=complex_quantity, properties={"MyLength": ifc.createIfcLengthMeasure(42)}
        )
        qto.Quantities = [complex_quantity]
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCLENGTHMEASURE")
        run("Complex properties are not supported 1/2", facet=facet, inst=element, expected=False)
        facet = Property(propertySet="Foo", baseName="MyLength", dataType="IFCLENGTHMEASURE")
        run("Complex properties are not supported 2/2", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        restriction = Restriction(options={"pattern": "Foo_.*"})
        facet = Property(propertySet=restriction, baseName="Foo", dataType="IFCLABEL")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "Bar"})
        run("All matching property sets must satisfy requirements 1/3", facet=facet, inst=element, expected=True)
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Baz")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"AnotherProperty": "AnotherValue"})
        run("All matching property sets must satisfy requirements 2/3", facet=facet, inst=element, expected=False)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "Bar"})
        run("All matching property sets must satisfy requirements 3/3", facet=facet, inst=element, expected=True)

        ifc = self.setup_ifc()
        restriction = Restriction(options={"pattern": "Foo.*"})
        facet = Property(propertySet="Foo_Bar", baseName=restriction, value="x", dataType="IFCLABEL")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foobar": "x"})
        run("All matching properties must satisfy requirements 1/3", facet=facet, inst=element, expected=True)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foobar": "x", "Foobaz": "x"})
        run("All matching properties must satisfy requirements 2/3", facet=facet, inst=element, expected=True)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foobar": "x", "Foobaz": "y"})
        run("All matching properties must satisfy requirements 3/3", facet=facet, inst=element, expected=False)

        ifc = self.setup_ifc()
        restriction1 = Restriction(options={"pattern": "Foo.*"})
        restriction2 = Restriction(options={"enumeration": ["x", "y"]})
        facet = Property(propertySet="Foo_Bar", baseName=restriction1, value=restriction2, dataType="IFCLABEL")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foobar": "x", "Foobaz": "y"})
        run(
            "If multiple properties are matched, all values must satisfy requirements 1/2",
            facet=facet,
            inst=element,
            expected=True,
        )
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foobar": "x", "Foobaz": "z"})
        run(
            "If multiple properties are matched, all values must satisfy requirements 2/2",
            facet=facet,
            inst=element,
            expected=False,
        )

        ifc = self.setup_ifc()
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="2", dataType="IFCTIMEMEASURE")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcMassMeasure(2)})
        run("Measures are used to specify an IFC data type 1/2", facet=facet, inst=element, expected=False)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcTimeMeasure(2)})
        run("Measures are used to specify an IFC data type 2/2", facet=facet, inst=element, expected=True)

        ifc = self.setup_ifc()
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="2", dataType="IFCLENGTHMEASURE")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcLengthMeasure(2)})
        run(
            "Unit conversions shall take place to IDS-nominated standard units 1/2",
            facet=facet,
            inst=element,
            expected=False,
        )
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": ifc.createIfcLengthMeasure(2000)})
        run(
            "Unit conversions shall take place to IDS-nominated standard units 2/2",
            facet=facet,
            inst=element,
            expected=True,
        )

        ifc = self.setup_ifc()
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[wall], relating_type=wall_type)
        pset = ifcopenshell.api.pset.add_pset(ifc, product=wall_type, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "Bar"})
        facet = Property(propertySet="Foo_Bar", baseName="Foo", dataType="IFCLABEL")
        run("Properties can be inherited from the type 1/2", facet=facet, inst=wall, expected=True)
        run("Properties can be inherited from the type 2/2", facet=facet, inst=wall_type, expected=True)

        ifc = self.setup_ifc()
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[wall], relating_type=wall_type)
        pset = ifcopenshell.api.pset.add_pset(ifc, product=wall_type, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "Baz"})
        pset = ifcopenshell.api.pset.add_pset(ifc, product=wall, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "Bar"})
        facet = Property(propertySet="Foo_Bar", baseName="Foo", value="Bar", dataType="IFCLABEL")
        run("Properties can be overriden by an occurrence 1/2", facet=facet, inst=wall, expected=True)
        run("Properties can be overriden by an occurrence 2/2", facet=facet, inst=wall_type, expected=False)

    def setup_ifc(self):
        ifc = ifcopenshell.file()
        ifc.createIfcProject()
        # Milli prefix used to check measurement conversions
        lengthunit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        areaunit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="AREAUNIT", prefix="MILLI")
        volumeunit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="VOLUMEUNIT", prefix="MILLI")
        timeunit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="TIMEUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[lengthunit, areaunit, volumeunit, timeunit])
        return ifc


class TestMaterial:
    def test_creating_a_material_facet(self):
        facet = Material()
        assert facet.asdict("requirement") == {"@cardinality": "required"}
        facet = Material(value="value", uri="https://test.com", cardinality="required", instructions="instructions")
        assert facet.asdict("requirement") == {
            "value": {"simpleValue": "value"},
            "@uri": "https://test.com",
            "@cardinality": "required",
            "@instructions": "instructions",
        }

    def test_filtering_using_a_material_facet(self):
        set_facet("material")

        facet = Material()
        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        run("Elements without a material always fail", facet=facet, inst=element, expected=False)
        material = ifcopenshell.api.material.add_material(ifc)
        ifcopenshell.api.material.assign_material(ifc, products=[element], material=material)
        run("Elements with any material will pass an empty material facet", facet=facet, inst=element, expected=True)

        run("A required facet checks all parameters as normal", facet=facet, inst=element, expected=True)
        facet = Material(cardinality="prohibited")
        run("A prohibited facet returns the opposite of a required facet", facet=facet, inst=element, expected=False)
        facet = Material(cardinality="optional")
        run(
            "An optional facet only checks requirements if there is a value to check 1/2",
            facet=facet,
            inst=element,
            expected=True,
        )
        facet = Material(value="Foo", cardinality="optional")
        run(
            "An optional facet only checks requirements if there is a value to check 1/2",
            facet=facet,
            inst=element,
            expected=False,
        )

        ifc = ifcopenshell.file()
        facet = Material(value="Foo")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(ifc)
        ifcopenshell.api.material.assign_material(ifc, products=[element], material=material)
        material.Name = "Foo"
        run("A material name may pass the value check", facet=facet, inst=element, expected=True)
        material.Name = "Bar"
        material.Category = "Foo"
        run("A material category may pass the value check", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        facet = Material(value="Foo")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        material_set = ifcopenshell.api.material.add_material_set(ifc, set_type="IfcMaterialList")
        ifcopenshell.api.material.assign_material(ifc, products=[element], material=material_set)
        material = ifcopenshell.api.material.add_material(ifc)
        ifcopenshell.api.material.add_list_item(ifc, material_list=material_set, material=material)
        material.Name = "Foo"
        run("Any material Name in a list will pass a value check", facet=facet, inst=element, expected=True)
        material.Name = "Bar"
        material.Category = "Foo"
        run("Any material Category in a list will pass a value check", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        facet = Material(value="Foo")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        material_set = ifcopenshell.api.material.add_material_set(ifc, set_type="IfcMaterialLayerSet")
        ifcopenshell.api.material.assign_material(ifc, products=[element], material=material_set)
        material = ifcopenshell.api.material.add_material(ifc)
        layer = ifcopenshell.api.material.add_layer(ifc, layer_set=material_set, material=material)
        layer.Name = "Foo"
        run("Any layer Name in a layer set will pass a value check", facet=facet, inst=element, expected=True)
        layer.Name = "Bar"
        layer.Category = "Foo"
        run("Any layer Category in a layer set will pass a value check", facet=facet, inst=element, expected=True)
        layer.Category = "Bar"
        material.Name = "Foo"
        run("Any material Name in a layer set will pass a value check", facet=facet, inst=element, expected=True)
        material.Name = "Bar"
        material.Category = "Foo"
        run("Any material Category in a layer set will pass a value check", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        facet = Material(value="Foo")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        material_set = ifcopenshell.api.material.add_material_set(ifc, set_type="IfcMaterialProfileSet")
        ifcopenshell.api.material.assign_material(ifc, products=[element], material=material_set)
        material = ifcopenshell.api.material.add_material(ifc)
        profile = ifcopenshell.api.material.add_profile(ifc, profile_set=material_set, material=material)
        profile.Name = "Foo"
        profile.Profile = ifc.createIfcCircleProfileDef("AREA", None, None, 1)
        run("Any profile Name in a profile set will pass a value check", facet=facet, inst=element, expected=True)
        profile.Name = "Bar"
        profile.Category = "Foo"
        run("Any profile Category in a profile set will pass a value check", facet=facet, inst=element, expected=True)
        profile.Category = "Bar"
        material.Name = "Foo"
        run("Any material Name in a profile set will pass a value check", facet=facet, inst=element, expected=True)
        material.Name = "Bar"
        material.Category = "Foo"
        run("Any material category in a profile set will pass a value check", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        facet = Material(value="Foo")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        material_set = ifcopenshell.api.material.add_material_set(ifc, set_type="IfcMaterialConstituentSet")
        ifcopenshell.api.material.assign_material(ifc, products=[element], material=material_set)
        run("A constituent set with no data will fail a value check", facet=facet, inst=element, expected=False)
        material = ifcopenshell.api.material.add_material(ifc)
        constituent = ifcopenshell.api.material.add_constituent(ifc, constituent_set=material_set, material=material)
        constituent.Name = "Foo"
        run(
            "Any constituent Name in a constituent set will pass a value check",
            facet=facet,
            inst=element,
            expected=True,
        )
        constituent.Name = "Bar"
        constituent.Category = "Foo"
        run(
            "Any constituent Category in a constituent set will pass a value check",
            facet=facet,
            inst=element,
            expected=True,
        )
        constituent.Category = "Bar"
        material.Name = "Foo"
        run("Any material Name in a constituent set will pass a value check", facet=facet, inst=element, expected=True)
        material.Name = "Bar"
        material.Category = "Foo"
        run(
            "Any material Category in a constituent set will pass a value check",
            facet=facet,
            inst=element,
            expected=True,
        )

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[element], relating_type=element_type)
        material = ifcopenshell.api.material.add_material(ifc)
        ifcopenshell.api.material.assign_material(ifc, products=[element_type], material=material)
        material.Name = "Foo"
        facet = Material(value="Foo")
        run("Occurrences can inherit materials from their types", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[element], relating_type=element_type)
        material = ifcopenshell.api.material.add_material(ifc)
        ifcopenshell.api.material.assign_material(ifc, products=[element_type], material=material)
        material.Name = "Bar"
        material = ifcopenshell.api.material.add_material(ifc)
        ifcopenshell.api.material.assign_material(ifc, products=[element], material=material)
        material.Name = "Foo"
        facet = Material(value="Foo")
        run("Occurrences can override materials from their types", facet=facet, inst=element, expected=True)


class TestPartOf:
    def test_creating_a_partof_facet(self):
        facet = PartOf()
        assert facet.asdict("requirement") == {
            "entity": {"name": {"simpleValue": "IFCWALL"}},
            "@cardinality": "required",
        }
        facet = PartOf(
            name="IFCGROUP",
            predefinedType="predefinedType",
            relation="IFCRELASSIGNSTOGROUP",
            cardinality="required",
            instructions="instructions",
        )
        assert facet.asdict("requirement") == {
            "entity": {
                "name": {"simpleValue": "IFCGROUP"},
                "predefinedType": {"simpleValue": "predefinedType"},
            },
            "@relation": "IFCRELASSIGNSTOGROUP",
            "@cardinality": "required",
            "@instructions": "instructions",
        }

    def test_filtering_using_a_partof_facet(self):
        set_facet("partof")

        ifc = ifcopenshell.file()

        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        facet = PartOf(name="IFCELEMENTASSEMBLY", relation="IFCRELAGGREGATES")
        run("A non aggregated element fails an aggregate relationship", facet=facet, inst=subelement, expected=False)
        ifcopenshell.api.aggregate.assign_object(ifc, products=[subelement], relating_object=element)
        run("The aggregated whole fails an aggregate relationship", facet=facet, inst=element, expected=False)
        run("The aggregated part passes an aggregate relationship", facet=facet, inst=subelement, expected=True)

        run("A required facet checks all parameters as normal", facet=facet, inst=subelement, expected=True)
        facet = PartOf(name="IFCELEMENTASSEMBLY", relation="IFCRELAGGREGATES", cardinality="prohibited")
        run("A prohibited facet returns the opposite of a required facet", facet=facet, inst=subelement, expected=False)

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSlab")
        subelement = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeam")
        ifcopenshell.api.aggregate.assign_object(ifc, products=[subelement], relating_object=element)
        facet = PartOf(name="IFCSLAB", relation="IFCRELAGGREGATES")
        run("An aggregate may specify the entity of the whole 1/2", facet=facet, inst=subelement, expected=True)
        facet = PartOf(name="IFCWALL", relation="IFCRELAGGREGATES")
        run("An aggregate may specify the entity of the whole 2/2", facet=facet, inst=subelement, expected=False)

        element.PredefinedType = "BASESLAB"
        facet = PartOf(name="IFCSLAB", predefinedType="BASESLAB", relation="IFCRELAGGREGATES")
        run(
            "An aggregate may specify the predefined type of the whole 1/2", facet=facet, inst=subelement, expected=True
        )
        facet = PartOf(name="IFCSLAB", predefinedType="SLABRADOR", relation="IFCRELAGGREGATES")
        run(
            "An aggregate may specify the predefined type of the whole 2/2",
            facet=facet,
            inst=subelement,
            expected=False,
        )

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSlab")
        subsubelement = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeam")
        ifcopenshell.api.aggregate.assign_object(ifc, products=[subelement], relating_object=element)
        ifcopenshell.api.aggregate.assign_object(ifc, products=[subsubelement], relating_object=subelement)
        facet = PartOf(name="IFCELEMENTASSEMBLY", relation="IFCRELAGGREGATES")
        run("An aggregate entity may pass any ancestral whole passes", facet=facet, inst=subsubelement, expected=True)

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcElementAssembly")
        group = ifcopenshell.api.group.add_group(ifc)
        facet = PartOf(name="IFCGROUP", relation="IFCRELASSIGNSTOGROUP")
        run("A non grouped element fails a group relationship", facet=facet, inst=element, expected=False)
        ifcopenshell.api.group.assign_group(ifc, products=[element], group=group)
        run("A grouped element passes a group relationship", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcElementAssembly")
        group = ifc.createIfcInventory()
        facet = PartOf(name="IFCGROUP", relation="IFCRELASSIGNSTOGROUP")
        ifcopenshell.api.group.assign_group(ifc, products=[element], group=group)
        run("A group entity must match exactly 1/2", facet=facet, inst=element, expected=False)
        facet = PartOf(name="IFCINVENTORY", relation="IFCRELASSIGNSTOGROUP")
        run("A group entity must match exactly 2/2", facet=facet, inst=element, expected=True)

        group.ObjectType = "BUNNY"
        facet = PartOf(name="IFCINVENTORY", predefinedType="BUNNARY", relation="IFCRELASSIGNSTOGROUP")
        run("A group predefined type must match exactly 2/2", facet=facet, inst=element, expected=False)
        facet = PartOf(name="IFCINVENTORY", predefinedType="BUNNY", relation="IFCRELASSIGNSTOGROUP")
        run("A group predefined type must match exactly 2/2", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcElementAssembly")
        container = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSpace")
        facet = PartOf(name="IFCSPACE", relation="IFCRELCONTAINEDINSPATIALSTRUCTURE")
        run("Any contained element passes a containment relationship 1/2", facet=facet, inst=element, expected=False)
        ifcopenshell.api.spatial.assign_container(ifc, products=[element], relating_structure=container)
        run("Any contained element passes a containment relationship 2/2", facet=facet, inst=element, expected=True)
        run("The container itself always fails", facet=facet, inst=container, expected=False)

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcElementAssembly")
        container = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSpace")
        ifcopenshell.api.spatial.assign_container(ifc, products=[element], relating_structure=container)
        facet = PartOf(relation="IFCRELCONTAINEDINSPATIALSTRUCTURE", name="IFCSITE")
        run("The container entity must match exactly 1/2", facet=facet, inst=element, expected=False)
        facet = PartOf(relation="IFCRELCONTAINEDINSPATIALSTRUCTURE", name="IFCSPACE")
        run("The container entity must match exactly 2/2", facet=facet, inst=element, expected=True)

        container.ObjectType = "BURROW"
        facet = PartOf(relation="IFCRELCONTAINEDINSPATIALSTRUCTURE", name="IFCSPACE", predefinedType="WARREN")
        run("The container predefined type must match exactly 1/2", facet=facet, inst=element, expected=False)
        facet = PartOf(relation="IFCRELCONTAINEDINSPATIALSTRUCTURE", name="IFCSPACE", predefinedType="BURROW")
        run("The container predefined type must match exactly 2/2", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSlab")
        subelement = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeam")
        ifcopenshell.api.aggregate.assign_object(ifc, products=[subelement], relating_object=element)
        container = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSpace")
        ifcopenshell.api.spatial.assign_container(ifc, products=[element], relating_structure=container)
        facet = PartOf(relation="IFCRELCONTAINEDINSPATIALSTRUCTURE", name="IFCSPACE")
        run("The container may be indirect", facet=facet, inst=subelement, expected=True)

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcFurniture")
        subelement = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcDiscreteAccessory")
        ifcopenshell.api.nest.assign_object(ifc, related_objects=[subelement], relating_object=element)
        facet = PartOf(name="IFCFURNITURE", relation="IFCRELNESTS")
        run("Any nested part passes a nest relationship", facet=facet, inst=subelement, expected=True)
        run("Any nested whole fails a nest relationship", facet=facet, inst=element, expected=False)

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcFurniture")
        subelement = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcDiscreteAccessory")
        ifcopenshell.api.nest.assign_object(ifc, related_objects=[subelement], relating_object=element)
        facet = PartOf(relation="IFCRELNESTS", name="IFCBEAM")
        run("The nest entity must match exactly 1/2", facet=facet, inst=subelement, expected=False)
        facet = PartOf(relation="IFCRELNESTS", name="IFCFURNITURE")
        run("The nest entity must match exactly 2/2", facet=facet, inst=subelement, expected=True)

        element.PredefinedType = "USERDEFINED"
        element.ObjectType = "WATERBOTTLE"
        facet = PartOf(relation="IFCRELNESTS", name="IFCFURNITURE", predefinedType="LITTERBOX")
        run("The nest predefined type must match exactly 1/2", facet=facet, inst=subelement, expected=False)
        facet = PartOf(relation="IFCRELNESTS", name="IFCFURNITURE", predefinedType="WATERBOTTLE")
        run("The nest predefined type must match exactly 2/2", facet=facet, inst=subelement, expected=True)

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcFurniture")
        subelement = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcDiscreteAccessory")
        subsubelement = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcMechanicalFastener")
        ifcopenshell.api.nest.assign_object(ifc, related_objects=[subelement], relating_object=element)
        ifcopenshell.api.nest.assign_object(ifc, related_objects=[subsubelement], relating_object=subelement)
        facet = PartOf(relation="IFCRELNESTS", name="IFCFURNITURE")
        run("Nesting may be indirect", facet=facet, inst=subsubelement, expected=True)


class TestRestriction:
    def test_creating_a_restriction(self):
        restriction = Restriction(options={"enumeration": ["foo", "bar"]})
        assert restriction.asdict() == {"@base": "xs:string", "xs:enumeration": [{"@value": "foo"}, {"@value": "bar"}]}

    def test_enumeration(self):
        restriction = Restriction(options={"enumeration": ["foo", "bar"]})
        assert restriction == "foo"
        assert restriction == "bar"
        assert restriction != "Foo"
        assert restriction != "baz"

    def test_bounds(self):
        restriction = Restriction(options={"minInclusive": 0, "maxExclusive": 10}, base="integer")
        assert restriction == 0
        assert restriction != 10
        assert restriction == 5
        assert restriction != -1

    def test_pattern(self):
        restriction = Restriction(options={"pattern": "[A-Z]{2}[0-9]{2}"})
        assert restriction == "AB01"
        assert restriction != "AB"
        assert restriction != "01"

    def test_filtering_using_restrictions(self):
        set_facet("restriction")

        ifc = ifcopenshell.file()
        restriction = Restriction(options={"enumeration": ["Foo", "Bar"]})
        facet = Attribute(name="Name", value=restriction)
        element = ifc.createIfcWall(Name="Foo")
        run("An enumeration matches case sensitively 1/3", facet=facet, inst=element, expected=True)
        element.Name = "Bar"
        run("An enumeration matches case sensitively 2/3", facet=facet, inst=element, expected=True)
        element.Name = "Baz"
        run("An enumeration matches case sensitively 3/3", facet=facet, inst=element, expected=False)

        ifc = ifcopenshell.file()
        restriction = Restriction(options={"minInclusive": 0, "maxInclusive": 10}, base="integer")
        element = ifc.createIfcSurfaceStyleRefraction(RefractionIndex=0)
        facet = Attribute(name="RefractionIndex", value=restriction)
        run("A bound can be inclusive 1/4", facet=facet, inst=element, expected=True)
        element.RefractionIndex = 5
        run("A bound can be inclusive 2/4", facet=facet, inst=element, expected=True)
        element.RefractionIndex = 10
        run("A bound can be inclusive 3/4", facet=facet, inst=element, expected=True)
        element.RefractionIndex = 100
        run("A bound can be inclusive 4/4", facet=facet, inst=element, expected=False)

        restriction = Restriction(options={"minExclusive": 0, "maxExclusive": 10}, base="integer")
        facet = Attribute(name="RefractionIndex", value=restriction)
        element.RefractionIndex = 0
        run("A bound can be inclusive 1/3", facet=facet, inst=element, expected=False)
        element.RefractionIndex = 5
        run("A bound can be inclusive 2/3", facet=facet, inst=element, expected=True)
        element.RefractionIndex = 10
        run("A bound can be inclusive 3/3", facet=facet, inst=element, expected=False)

        ifc = ifcopenshell.file()
        restriction = Restriction(options={"pattern": "[A-Z]{2}[0-9]{2}"})
        facet = Attribute(name="Name", value=restriction)
        element = ifc.createIfcWall(Name="WT01")
        run("Regex patterns can be used 1/3", facet=facet, inst=element, expected=True)
        element.Name = "XY99"
        run("Regex patterns can be used 2/3", facet=facet, inst=element, expected=True)
        element.Name = "A5"
        run("Regex patterns can be used 3/3", facet=facet, inst=element, expected=False)

        ifc = ifcopenshell.file()
        restriction = Restriction(options={"pattern": ".*"})
        element = ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42)
        facet = Attribute(name="RefractionIndex", value=restriction)
        run("Patterns only work on strings and nothing else", facet=facet, inst=element, expected=False)

        ifc = ifcopenshell.file()
        restriction = Restriction(options={"length": 2})
        facet = Attribute(name="Name", value=restriction)
        element = ifc.createIfcWall(Name="AB")
        run("Length checks can be used 1/2", facet=facet, inst=element, expected=True)
        element.Name = "ABC"
        run("Length checks can be used 1/2", facet=facet, inst=element, expected=False)

        ifc = ifcopenshell.file()
        restriction = Restriction(options={"minLength": 2, "maxLength": 3})
        facet = Attribute(name="Name", value=restriction)
        element = ifc.createIfcWall(Name="A")
        run("Max and min length checks can be used 1/3", facet=facet, inst=element, expected=False)
        element.Name = "AB"
        run("Max and min length checks can be used 2/3", facet=facet, inst=element, expected=True)
        element.Name = "ABC"
        run("Max and min length checks can be used 3/3", facet=facet, inst=element, expected=True)
        element.Name = "ABCD"
        run("Max and min length checks can be used 4/3", facet=facet, inst=element, expected=False)
