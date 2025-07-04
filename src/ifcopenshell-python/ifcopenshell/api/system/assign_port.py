# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell
import ifcopenshell.api.owner
import ifcopenshell.api.geometry
import ifcopenshell.guid
import ifcopenshell.util.placement
from typing import Any


def assign_port(
    file: ifcopenshell.file, element: ifcopenshell.entity_instance, port: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    """Assigns a port to an element

    If you have an orphaned port, you may assign it to a distribution
    element using this function. Ports should typically not be orphaned, but
    it may be useful when patching up models.

    :param element: The IfcDistributionElement to assign the port to.
    :param port: The IfcDistributionPort you want to assign.
    :return: The IfcRelNests relationship, or the
        IfcRelConnectsPortToElement for IFC2X3.

    Example:

    .. code:: python

        # Create a duct
        duct = ifcopenshell.api.root.create_entity(model,
            ifc_class="IfcDuctSegment", predefined_type="RIGIDSEGMENT")

        # Create 2 ports, one for either end.
        port1 = ifcopenshell.api.system.add_port(model, element=duct)
        port2 = ifcopenshell.api.system.add_port(model, element=duct)

        # Unassign one port for some weird reason.
        ifcopenshell.api.system.unassign_port(model, element=duct, port=port1)

        # Reassign it back
        ifcopenshell.api.system.assign_port(model, element=duct, port=port1)
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(element, port)


class Usecase:
    file: ifcopenshell.file

    def execute(
        self, element: ifcopenshell.entity_instance, port: ifcopenshell.entity_instance
    ) -> ifcopenshell.entity_instance:
        self.element = element
        self.port = port
        if self.file.schema == "IFC2X3":
            return self.execute_ifc2x3()

        rels = self.element.IsNestedBy or []

        for rel in rels:
            if self.port in rel.RelatedObjects:
                return rel

        if rels:
            rel = rels[0]
            related_objects = set(rel.RelatedObjects) or set()
            related_objects.add(self.port)
            rel.RelatedObjects = list(related_objects)
            ifcopenshell.api.owner.update_owner_history(self.file, element=rel)
        else:
            rel = self.file.create_entity(
                "IfcRelNests",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=ifcopenshell.api.owner.create_owner_history(self.file),
                RelatedObjects=[self.port],
                RelatingObject=self.element,
            )

        self.update_port_placement()

        return rel

    def execute_ifc2x3(self) -> ifcopenshell.entity_instance:
        for rel in self.element.HasPorts or []:
            if rel.RelatingPort == self.port:
                return rel
        rel = self.file.create_entity(
            "IfcRelConnectsPortToElement",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.owner.create_owner_history(self.file),
            RelatingPort=self.port,
            RelatedElement=self.element,
        )
        self.update_port_placement()
        return rel

    def update_port_placement(self) -> None:
        placement = getattr(self.port, "ObjectPlacement", None)
        if placement and placement.is_a("IfcLocalPlacement"):
            ifcopenshell.api.geometry.edit_object_placement(
                self.file,
                product=self.port,
                matrix=ifcopenshell.util.placement.get_local_placement(self.port.ObjectPlacement),
                is_si=False,
            )
