# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
import time
import ifcopenshell
import ifcopenshell.util.attribute
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper
from typing import Union, Any, Literal

# This is highly experimental and incomplete, however, it may work for simple datasets.

cwd = os.path.dirname(os.path.realpath(__file__))
IFC_SCHEMA = Literal["IFC2X3", "IFC4", "IFC4X3"]


def get_fallback_schema(version: str) -> IFC_SCHEMA:
    """Fallback to the schema version we do have docs and mapping for.

    Needed to support IFC versions like 4X3_RC1, 4X1 etc.

    :param version: Typically a string from ``ifcopenshell.file.schema_identifier``, e.g. IFC4X3_ADD2
    """
    if version.startswith("IFC4X3"):
        version = "IFC4X3"
    elif version.startswith("IFC4"):
        version = "IFC4"
    elif version.startswith("IFC2X3"):
        version = "IFC2X3"
    else:
        assert False, f"Unexpected schema version: {version}."
    return version


def get_declaration(element: ifcopenshell.entity_instance):
    """Get the schema declaration of an actively used entity instance

    IFC models are made out of instances (e.g. with a STEP ID) of entities
    (e.g. IfcWall). Those entities are defined through a **Schema
    Declaration**.

    **Schema Declaration** objects can be used to query information about the
    IFC schema itself, such as data types, enumeration values, and inheritance.

    :param element: Any instance, typically from a loaded or created IFC model

    Example:

    .. code:: python

        wall = model.createIfcWall()
        declaration = ifcopenshell.util.schema.get_declaration(wall)
        print(declaration.name()) # IfcWall
        print(declaration.is_abstract()) # False
        print(declaration.supertype().name()) # IfcBuildingElement
    """
    return element.wrapped_data.declaration().as_entity()


def is_a(declaration: ifcopenshell.ifcopenshell_wrapper.declaration, ifc_class: str) -> bool:
    """Checks if a schema declaration is a class

    :param declaration: The declaration from the schema.
    :param ifc_class: A case insensitive IFC class name (e.g. IfcRoot)
    :return: True is the declaration is of that class

    Example:

    .. code:: python

        wall = model.createIfcWall()
        declaration = ifcopenshell.util.schema.get_declaration(wall)
        ifcopenshell.util.schema.is_a(declaration, "IfcRoot") # True
    """
    return declaration._is(ifc_class)


def get_supertypes(
    declaration: ifcopenshell.ifcopenshell_wrapper.entity,
) -> list[ifcopenshell.ifcopenshell_wrapper.entity]:
    """Gets a list of supertype declarations

    :param declaration: The declaration from the schema, as an entity.
    :return: A list of supertypes in order from parent to grandparent.

    Example:

    .. code:: python

        wall = model.createIfcWall()
        results = ifcopenshell.util.schema.get_supertypes(wall.wrapped_data.declaration().as_entity())
        # [<entity IfcBuildingElement>, <entity IfcElement>, ..., <entity IfcRoot>]
    """
    results = []
    while True:
        if not (declaration := declaration.supertype()):
            break
        results.append(declaration)
    return results


def get_subtypes(
    declaration: ifcopenshell.ifcopenshell_wrapper.entity,
) -> list[ifcopenshell.ifcopenshell_wrapper.entity]:
    """Get a flat list of subtype declarations

    Abstract classes are skipped.

    Inconsistently, the declaration itself is also added to this list. This
    should be fixed exclude the declaration itself.

    :param declaration: The declaration from the schema, as an entity.
    :return: A list of subtypes in order from child to grandchild.

    .. code:: python

        schema = ifcopenshell.schema_by_name("IFC4")
        declaration = schema.declaration_by_name("IfcFlowSegment")
        print(ifcopenshell.util.schema.get_subtypes(declaration))
        [<entity IfcFlowSegment>, <entity IfcCableCarrierSegment>, ..., <entity IfcPipeSegment>]
    """

    def get_classes(decl: ifcopenshell_wrapper.entity) -> list[ifcopenshell_wrapper.entity]:
        results: list[ifcopenshell_wrapper.entity] = []
        if not decl.is_abstract():
            results.append(decl)
        for subtype in decl.subtypes():
            results.extend(get_classes(subtype))
        return results

    return get_classes(declaration)


def reassign_class(
    ifc_file: Union[ifcopenshell.file, None], element: ifcopenshell.entity_instance, new_class: str
) -> ifcopenshell.entity_instance:
    """
    Attempts to change the class (entity name) of `element` to `new_class` by
    removing element and recreating a similar instance of type `new_class`
    with the same id.

    In certain cases it may affect the structure of inversely related instances:
    - Multiple occurrences of reassigned instance within the same aggregate
      (such as start and end-point of polyline)
    - Occurrences of reassigned instance within an ordered aggregate
      (such as IfcRelNests)

    It's unlikely that this affects real-world usage of this function.

    :raises ValueError: If ``new_class`` does not exist in the provided file schema.
    """

    if element.is_a() == new_class:
        return element

    if not ifc_file:
        ifc_file = element.file

    schema = ifcopenshell_wrapper.schema_by_name(ifc_file.schema_identifier)
    try:
        declaration = schema.declaration_by_name(new_class)
    except RuntimeError:
        raise ValueError(
            f"Class of {element} could not be changed to {new_class} as the class does not exist in schema {ifc_file.schema_identifier}."
        )

    info = element.get_info()

    new_attributes = {}
    for attribute in declaration.all_attributes():
        name = attribute.name()
        old_attribute = info.get(name, None)
        if old_attribute:
            if ifcopenshell.util.attribute.get_primitive_type(attribute) == "enum":
                if old_attribute in ifcopenshell.util.attribute.get_enum_items(attribute):
                    new_attributes[name] = old_attribute
            else:
                new_attributes[name] = old_attribute

    inverse_pairs = ifc_file.get_inverse(element, allow_duplicate=True, with_attribute_indices=True)
    ifc_file.remove(element)

    try:
        new_element = ifc_file.create_entity(new_class, id=info["id"], **new_attributes)
    except:
        print(f"Class of {element} could not be changed to {new_class}")
        old_class = info.pop("type")
        return ifc_file.create_entity(old_class, **info)

    for inverse_pair in inverse_pairs:
        inverse, index = inverse_pair
        if inverse[index] is None:
            inverse[index] = new_element
        elif isinstance(inverse[index], tuple):
            item = list(inverse[index])
            item.append(new_element)
            inverse[index] = item

    return new_element


class BatchReassignClass:
    def __init__(self, file: ifcopenshell.file):
        self.file = file
        self.purge()

    def reassign(self, element: ifcopenshell.entity_instance, new_class: str) -> ifcopenshell.entity_instance:
        try:
            new_element = self.file.create_entity(new_class)
        except:
            print(f"Class of {element} could not be changed to {new_class}")
            return element
        new_attributes = [new_element.attribute_name(i) for i, attribute in enumerate(new_element)]
        for i, attribute in enumerate(element):
            try:
                new_element[new_attributes.index(element.attribute_name(i))] = attribute
            except:
                continue
        for inverse_pair in self.file.get_inverse(element, allow_duplicate=True, with_attribute_indices=True):
            inverse, index = inverse_pair
            self.replacements.setdefault(inverse, {}).setdefault(index, {})[element] = new_element
        self.to_delete.add(element)
        return new_element

    def unbatch(self):
        for inverse, replacements in self.replacements.items():
            for index, element_map in replacements.items():
                value = inverse[index]
                new = inverse.walk(lambda x: True, lambda v: element_map.get(v, v), value)
                if value != new:
                    inverse[index] = new

        for element in self.to_delete:
            self.file.remove(element)
        self.purge()

    def purge(self) -> None:
        # mapping {inverse: {attribute_index: {old_element: new_element} } }
        self.replacements: dict[
            ifcopenshell.entity_instance, dict[int, dict[ifcopenshell.entity_instance, ifcopenshell.entity_instance]]
        ] = {}
        self.to_delete: set[ifcopenshell.entity_instance] = set()


class Migrator:
    migrated_ids: dict[int, int]
    attribute_overrides: dict[int, dict[int, str]]

    def __init__(self):
        self.migrated_ids = {}
        self.attribute_overrides = {}
        self.class_4_to_2x3 = json.load(open(os.path.join(cwd, "class_4_to_2x3.json"), "r"))
        self.class_2x3_to_4 = json.load(open(os.path.join(cwd, "class_2x3_to_4.json"), "r"))

        # IFC classes, and their IFC attributes mapping
        self.attributes_mapping = {
            ("IFC4", "IFC2X3"): json.load(open(os.path.join(cwd, "attribute_4_to_2x3.json"), "r")),
            ("IFC4X3", "IFC4"): json.load(open(os.path.join(cwd, "attribute_4x3_to_4.json"), "r")),
        }

        self.default_values = {
            "ChangeAction": "NOCHANGE",
            "CompositionType": "ELEMENT",
            "CrossSectionArea": 1,
            "DataValue": 0,
            "DefinedValues": [0],
            "DefiningValues": [0],
            "DestabilizingLoad": False,
            "Edition": "",
            "EndParam": 1.0,
            "EnumerationValues": [0],
            "GeodeticDatum": "",
            "Intent": "",
            "IsHeading": False,
            "ListValues": [0],
            "LongitudinalBarCrossSectionArea": 1,
            "LongitudinalBarNominalDiameter": 1,
            "LongitudinalBarSpacing": 1,
            "Name": "",
            "NominalDiameter": 1,
            "PredefinedType": "NOTDEFINED",
            "RowCells": [0],
            "SequenceType": "NOTDEFINED",
            "Source": "",
            "StartParam": 0.0,
            "TransverseBarCrossSectionArea": 1,
            "TransverseBarNominalDiameter": 1,
            "TransverseBarSpacing": 1,
            # Manual additions from experience
            "InteriorOrExteriorSpace": "NOTDEFINED",
            "AssemblyPlace": "NOTDEFINED",  # See bug https://github.com/Autodesk/revit-ifc/issues/395
        }
        self.default_entities = {
            "CurrentValue": None,
            "DepreciatedValue": None,
            "Jurisdiction": None,
            "OriginalValue": None,
            "Owner": None,
            "OwnerHistory": None,
            "Position": None,
            "PropertyReference": None,
            "RepresentationContexts": None,
            "ResponsiblePerson": None,
            "ResponsiblePersons": None,
            "Rows": None,
            "TotalReplacementCost": None,
            "UnitsInContext": None,
            "User": None,
        }

    def preprocess(self, old_file: ifcopenshell.file, new_file: ifcopenshell.file) -> None:
        new_file.assign_header_from(old_file)
        to_delete = set()

        if old_file.schema == "IFC2X3" and new_file.schema == "IFC4":
            # IfcCalendarDate is deprecated in IFC4
            for element in old_file.by_type("IfcCalendarDate"):
                for inverse, attribute_index in old_file.get_inverse(
                    element, allow_duplicate=True, with_attribute_indices=True
                ):
                    self.attribute_overrides.setdefault(inverse.id(), {})[
                        attribute_index
                    ] = f"{element[2]}-{element[1]}-{element[0]}"
                to_delete.add(element)

        if old_file.schema == "IFC4" and new_file.schema == "IFC4X3":
            # IfcPresentationStyleAssignment is deprecated
            for assignment in old_file.by_type("IfcPresentationStyleAssignment"):
                for styled_item in old_file.get_inverse(assignment):
                    if not styled_item.is_a("IfcStyledItem"):
                        continue
                    styled_item.Styles = [s for s in styled_item.Styles if s.is_a("IfcPresentationStyle")] + list(
                        assignment.Styles
                    )
                to_delete.add(assignment)

        for element in to_delete:
            old_file.remove(element)

    def migrate(
        self, element: ifcopenshell.entity_instance, new_file: ifcopenshell.file
    ) -> ifcopenshell.entity_instance:
        if element.id() == 0:
            ifc_class = element.is_a()
            if ifc_class == "IfcCountMeasure" and new_file.schema == "IFC4X3":
                value = element.wrappedValue
                if isinstance(value, float):
                    ifc_class = "IfcNumericMeasure"
            return new_file.create_entity(ifc_class, element.wrappedValue)
        try:
            return new_file.by_id(self.migrated_ids[element.id()])
        except:
            pass
        # print("Migrating", element)
        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(new_file.schema_identifier)
        new_element = self.migrate_class(element, new_file)
        # print("Migrated class from {} to {}".format(element, new_element))
        new_element_schema = schema.declaration_by_name(new_element.is_a())
        if not hasattr(new_element_schema, "all_attributes"):
            return element  # The element has no attributes, so migration is done
        new_element = self.migrate_attributes(element, new_file, new_element, new_element_schema)
        self.migrated_ids[element.id()] = new_element.id()
        return new_element

    def migrate_class(
        self, element: ifcopenshell.entity_instance, new_file: ifcopenshell.file
    ) -> ifcopenshell.entity_instance:
        ifc_class = element.is_a()
        if ifc_class == "IfcQuantityCount" and new_file.schema == "IFC4X3":
            # 3 IfcPhysicalSimpleQuantity Value
            value = element[3]
            if isinstance(value, float):
                ifc_class = "IfcQuantityNumber"
        try:
            new_element = new_file.create_entity(ifc_class)
        except:
            # The element does not exist in this schema
            # Complex migration is not yet supported (e.g. polygonal face set to faceted brep)
            if new_file.schema == "IFC2X3":
                new_element = new_file.create_entity(self.class_4_to_2x3[ifc_class])
            elif new_file.schema == "IFC4":
                new_element = new_file.create_entity(self.class_2x3_to_4[ifc_class])
        return new_element

    def migrate_attributes(
        self,
        element: ifcopenshell.entity_instance,
        new_file: ifcopenshell.file,
        new_element: ifcopenshell.entity_instance,
        new_element_schema: ifcopenshell_wrapper.declaration,
    ) -> ifcopenshell.entity_instance:
        for attribute_index, value in self.attribute_overrides.get(element.id(), {}).items():
            new_element[attribute_index] = value
        for i, attribute in enumerate(new_element_schema.all_attributes()):
            if new_element_schema.derived()[i]:
                continue
            self.migrate_attribute(attribute, element, new_file, new_element, new_element_schema)
        return new_element

    def find_equivalent_attribute(
        self,
        new_element: ifcopenshell.entity_instance,
        attribute: ifcopenshell_wrapper.attribute,
        element: ifcopenshell.entity_instance,
        attributes_mapping: dict[str, dict[str, str]],
        reverse_mapping: bool = False,
    ) -> Union[Any, None]:
        # print("Searching for an equivalent", element, new_element, attribute.name())
        ifc_class = new_element.is_a()
        attr_name = attribute.name()
        try:
            if reverse_mapping:
                equivalent_map = attributes_mapping[ifc_class]
                equivalent = list(equivalent_map.keys())[list(equivalent_map.values()).index(attr_name)]
            else:
                equivalent = attributes_mapping[ifc_class][attr_name]
            if hasattr(element, equivalent):
                # print("Equivalent found", equivalent)
                return getattr(element, equivalent)
            else:
                return
        except Exception as e:
            if (
                ifc_class == "IfcQuantityNumber"
                and attr_name == "NumberValue"
                and new_element.file.schema == "IFC4X3"
                and element.is_a("IfcQuantityCount")
            ):
                # 3 IfcPhysicalSimpleQuantity Value
                return element[3]

            print(
                "Unable to find equivalent attribute of {} to migrate from {} to {}".format(
                    attr_name, element, new_element
                )
            )
            raise e

    def migrate_attribute(
        self,
        attribute: ifcopenshell_wrapper.attribute,
        element: ifcopenshell.entity_instance,
        new_file: ifcopenshell.file,
        new_element: ifcopenshell.entity_instance,
        new_element_schema: ifcopenshell_wrapper.declaration,
    ) -> None:
        # NOTE: `attribute` is an attribute in new file schema
        # print("Migrating attribute", element, new_element, attribute.name())
        old_file = element.wrapped_data.file
        if hasattr(element, attribute.name()):
            value = getattr(element, attribute.name())
            # print("Attribute names matched", value)

        elif new_file.schema == "IFC2X3" and old_file.schema == "IFC4":
            # IFC4 to IFC2X3: We know the IFC2X3 attribute name, but not its IFC4 equivalent
            try:
                value = self.find_equivalent_attribute(
                    new_element, attribute, element, self.attributes_mapping[("IFC4", "IFC2X3")], reverse_mapping=True
                )
            except:  # We tried our best
                return

        elif new_file.schema == "IFC4" and old_file.schema == "IFC2X3":
            # IFC2X3 to IFC4: We know the IFC4 attribute name, but not its IFC2X3 equivalent
            try:
                value = self.find_equivalent_attribute(
                    new_element, attribute, element, self.attributes_mapping[("IFC4", "IFC2X3")]
                )
            except:  # We tried our best
                return

        elif new_file.schema == "IFC4X3" and old_file.schema == "IFC4":
            try:
                value = self.find_equivalent_attribute(
                    new_element, attribute, element, self.attributes_mapping[("IFC4X3", "IFC4")]
                )
            except:  # We tried our best
                return

        elif new_file.schema == "IFC4" and old_file.schema == "IFC4X3":
            try:
                value = self.find_equivalent_attribute(
                    new_element, attribute, element, self.attributes_mapping[("IFC4X3", "IFC4")], reverse_mapping=True
                )
            except:  # We tried our best
                return

        try:
            value
        except UnboundLocalError:
            print(
                f"Couldn't match attribute {attribute.name()} by name to migrate from {element} "
                f"to {new_element} and there is no special mapping to handle migration "
                f"from {old_file.schema} -> {new_file.schema}"
            )
            return

        # print("Continuing migration of {} to migrate from {} to {}".format(attribute.name(), element, new_element))
        if value is None and not attribute.optional():
            value = self.generate_default_value(attribute, new_file)
            if value is None:
                print("Failed to generate default value for {} on {}".format(attribute.name(), element))
        elif isinstance(value, ifcopenshell.entity_instance):
            value = self.migrate(value, new_file)
        elif isinstance(value, (list, tuple)):
            if value and isinstance(value[0], ifcopenshell.entity_instance):
                new_value = []
                for item in value:
                    new_value.append(self.migrate(item, new_file))
                value = new_value
        if value is not None:
            setattr(new_element, attribute.name(), value)

    def generate_default_value(self, attribute: ifcopenshell_wrapper.attribute, new_file: ifcopenshell.file) -> Any:
        if attribute.name() in self.default_values:
            return self.default_values[attribute.name()]
        elif attribute.name() == "OwnerHistory":
            self.default_entities[attribute.name()] = new_file.create_entity(
                "IfcOwnerHistory",
                **{
                    "OwningUser": new_file.create_entity(
                        "IfcPersonAndOrganization",
                        **{
                            "ThePerson": new_file.create_entity("IfcPerson"),
                            "TheOrganization": new_file.create_entity(
                                "IfcOrganization", **{"Name": "IfcOpenShell Migrator"}
                            ),
                        },
                    ),
                    "OwningApplication": new_file.create_entity(
                        "IfcApplication",
                        **{
                            "ApplicationDeveloper": new_file.create_entity(
                                "IfcOrganization", **{"Name": "IfcOpenShell Migrator"}
                            ),
                            "Version": "Works for me",
                            "ApplicationFullName": "IfcOpenShell Migrator",
                            "ApplicationIdentifier": "IfcOpenShell Migrator",
                        },
                    ),
                    "ChangeAction": "NOCHANGE",
                    "CreationDate": int(time.time()),
                },
            )
        return self.default_entities.get(attribute.name(), None)
