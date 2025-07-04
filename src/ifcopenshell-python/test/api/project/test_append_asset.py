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

import test.bootstrap
import ifcopenshell.api.layer
import ifcopenshell.api.geometry
import ifcopenshell.api.georeference
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.api.cost
import ifcopenshell.api.feature
import ifcopenshell.api.style
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.material
import ifcopenshell.api.profile
import ifcopenshell.api.unit
import ifcopenshell.api.owner.settings
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.unit
import numpy as np
from ifcopenshell.util.shape_builder import ShapeBuilder


class TestAppendAssetIFC2X3(test.bootstrap.IFC2X3):
    def test_do_not_append_twice(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        material = ifcopenshell.api.material.add_material(library, name="Material")
        schedule = ifcopenshell.api.cost.add_cost_schedule(library, name="Schedule")
        profile = library.createIfcIShapeProfileDef()

        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=material)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=material)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=schedule)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=schedule)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=profile)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=profile)
        assert len(self.file.by_type("IfcWallType")) == 1

    def test_append_a_type_product(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert len(self.file.by_type("IfcWallType")) == 1

    def test_reuse_an_existing_context_if_it_was_added_from_library_previously(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        project = ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        lib_context = ifcopenshell.api.context.add_context(library, context_type="Model")

        self.file.add(project)  # will add project and it's contexts

        material = ifcopenshell.api.material.add_material(library, name="Material")
        style = ifcopenshell.api.style.add_style(library)
        ifcopenshell.api.style.assign_material_style(library, material=material, style=style, context=lib_context)

        ifcopenshell.api.project.append_asset(self.file, library=library, element=material)
        assert len(self.file.by_type("IfcMaterial")) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationContext")) == 1
        context = self.file.by_type("IfcMaterial")[0].HasRepresentation[0].Representations[0].ContextOfItems
        # make sure it's still valid
        assert context.WorldCoordinateSystem

    def test_add_new_contexts_if_necessary(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        lib_context = ifcopenshell.api.context.add_context(library, context_type="Model")
        lib_subcontext = ifcopenshell.api.context.add_context(
            library, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=lib_context
        )

        # It has no contexts right now
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")

        material = ifcopenshell.api.material.add_material(library, name="Material")
        style = ifcopenshell.api.style.add_style(library)
        ifcopenshell.api.style.assign_material_style(library, material=material, style=style, context=lib_subcontext)

        ifcopenshell.api.project.append_asset(self.file, library=library, element=material)
        assert len(self.file.by_type("IfcProject")) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationSubContext", include_subtypes=False)) == 1
        context = self.file.by_type("IfcMaterial")[0].HasRepresentation[0].Representations[0].ContextOfItems
        # make sure it's still valid
        assert context.WorldCoordinateSystem

    def test_append_a_single_type_product_even_though_an_inverse_material_relationship_is_shared(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        material = ifcopenshell.api.material.add_material(library, name="Material")
        ifcopenshell.api.material.assign_material(library, products=[element], material=material)
        ifcopenshell.api.material.assign_material(library, products=[element2], material=material)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert len(self.file.by_type("IfcWallType")) == 1

    def test_append_a_type_product_with_its_materials(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        material = ifcopenshell.api.material.add_material(library, name="Material")
        ifcopenshell.api.material.assign_material(library, products=[element], material=material)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert self.file.by_type("IfcWallType")[0].HasAssociations[0].RelatingMaterial.Name == "Material"

    def test_append_a_type_product_where_its_inverse_material_relationship_refers_to_products_not_in_scope(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        element_type2 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(library, related_objects=[element], relating_type=element_type)
        material = ifcopenshell.api.material.add_material(library, name="Material")
        ifcopenshell.api.material.assign_material(library, products=[element], material=material)
        ifcopenshell.api.material.assign_material(library, products=[element_type], material=material)
        ifcopenshell.api.material.assign_material(library, products=[element_type2], material=material)

        # appending another type not connected to IfcWall directly
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element_type2)
        assert set(self.file.by_type("IfcWall")) == set()

        # appending type of IfcWall
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element_type2)
        assert set(self.file.by_type("IfcWall")) == set()

    def test_append_two_type_products_sharing_the_same_material_indirectly_via_a_material_set(self):
        ifcopenshell.api.root.create_entity(self.file, "IfcProject")
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, "IfcProject")
        element1 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        material = ifcopenshell.api.material.add_material(library, name="Material")

        layer_set1 = ifcopenshell.api.material.add_material_set(library, set_type="IfcMaterialLayerSet")
        ifcopenshell.api.material.add_layer(library, layer_set=layer_set1, material=material)
        ifcopenshell.api.material.add_layer(library, layer_set=layer_set1, material=material)

        layer_set2 = ifcopenshell.api.material.add_material_set(library, set_type="IfcMaterialLayerSet")
        ifcopenshell.api.material.add_layer(library, layer_set=layer_set2, material=material)
        ifcopenshell.api.material.add_layer(library, layer_set=layer_set2, material=material)

        ifcopenshell.api.material.assign_material(library, products=[element1], material=layer_set1)
        ifcopenshell.api.material.assign_material(library, products=[element2], material=layer_set2)

        new1 = ifcopenshell.api.project.append_asset(self.file, library=library, element=element1)
        new2 = ifcopenshell.api.project.append_asset(self.file, library=library, element=element2)

        material = self.file.by_type("IfcMaterial")[0]
        assert ifcopenshell.util.element.get_material(new1).MaterialLayers[0].Material == material
        assert ifcopenshell.util.element.get_material(new1).MaterialLayers[1].Material == material
        assert ifcopenshell.util.element.get_material(new2).MaterialLayers[0].Material == material
        assert ifcopenshell.util.element.get_material(new2).MaterialLayers[1].Material == material

    def test_append_a_type_product_with_its_styles(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        history = library.createIfcOwnerHistory()
        element.OwnerHistory = history

        material = ifcopenshell.api.material.add_material(library, name="Material")
        rel = ifcopenshell.api.material.assign_material(library, products=[element], material=material)
        # We share a history. This ensures that we continue to check all
        # whitelisted inverses even though one of the subelements (i.e. this
        # shared history) is already processed. See bug #2837.
        rel.OwnerHistory = history

        item = library.createIfcBoundingBox()
        library.createIfcStyledItem(Item=item)
        mapped_rep = library.createIfcShapeRepresentation(Items=[item])
        element.RepresentationMaps = [library.createIfcRepresentationMap(MappedRepresentation=mapped_rep)]
        new = ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert len(new.RepresentationMaps[0].MappedRepresentation.Items[0].StyledByItem) == 1
        assert self.file.by_type("IfcStyledItem")[0].Item == self.file.by_type("IfcBoundingBox")[0]

    def test_append_product_with_styles_to_reuse_styleditems(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        element_type = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        history = library.createIfcOwnerHistory()
        element_type.OwnerHistory = history
        item = library.createIfcBoundingBox()
        library.createIfcStyledItem(Item=item)
        context = self.file.createIfcGeometricRepresentationContext()
        mapped_rep = library.createIfcShapeRepresentation(Items=[item], ContextOfItems=context)
        element_type.RepresentationMaps = [library.createIfcRepresentationMap(MappedRepresentation=mapped_rep)]

        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(library, related_objects=[element], relating_type=element_type)

        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert len(self.file.by_type("IfcStyledItem")) == 1

    def test_append_a_type_product_with_a_styled_materials(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        local_context = ifcopenshell.api.context.add_context(self.file, context_type="Model")

        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        context = ifcopenshell.api.context.add_context(library, context_type="Model")

        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        material = ifcopenshell.api.material.add_material(library, name="Material")
        ifcopenshell.api.material.assign_material(library, products=[element], material=material)
        style = ifcopenshell.api.style.add_style(library)
        ifcopenshell.api.style.assign_material_style(library, material=material, style=style, context=context)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert self.file.by_type("IfcWallType")[0].HasAssociations[0].RelatingMaterial.Name == "Material"
        assert self.file.by_type("IfcWallType")[0].HasAssociations[0].RelatingMaterial.HasRepresentation
        assert len(self.file.by_type("IfcGeometricRepresentationContext")) == 1

    def test_append_a_material(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        material = ifcopenshell.api.material.add_material(library, name="Material")
        ifcopenshell.api.project.append_asset(self.file, library=library, element=material)
        assert len(self.file.by_type("IfcMaterial")) == 1

    def test_append_a_material_with_a_representation(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")

        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        material = ifcopenshell.api.material.add_material(library, name="Material")
        style = ifcopenshell.api.style.add_style(library)
        context = ifcopenshell.api.context.add_context(library, context_type="Model")
        ifcopenshell.api.style.assign_material_style(library, material=material, style=style, context=context)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=material)
        assert len(self.file.by_type("IfcMaterial")) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationContext")) == 1
        context = self.file.by_type("IfcMaterial")[0].HasRepresentation[0].Representations[0].ContextOfItems
        assert context.ContextType == "Model"

    def test_append_a_material_with_a_representation_and_reuse_an_existing_context(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        file_context = ifcopenshell.api.context.add_context(self.file, context_type="Model")

        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        material = ifcopenshell.api.material.add_material(library, name="Material")
        style = ifcopenshell.api.style.add_style(library)
        context = ifcopenshell.api.context.add_context(library, context_type="Model")
        ifcopenshell.api.style.assign_material_style(library, material=material, style=style, context=context)

        ifcopenshell.api.project.append_asset(self.file, library=library, element=material)
        assert len(self.file.by_type("IfcMaterial")) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationContext")) == 1
        context = self.file.by_type("IfcMaterial")[0].HasRepresentation[0].Representations[0].ContextOfItems
        assert context == file_context
        # make sure it's still valid
        assert context.WorldCoordinateSystem

    def test_append_a_material_with_a_representation_and_reuse_an_existing_subcontext(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        file_context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        file_subcontext = ifcopenshell.api.context.add_context(
            self.file,
            parent=file_context,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
        )

        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        material = ifcopenshell.api.material.add_material(library, name="Material")
        style = ifcopenshell.api.style.add_style(library)
        context = ifcopenshell.api.context.add_context(library, context_type="Model")
        subcontext = ifcopenshell.api.context.add_context(
            library,
            parent=context,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
        )
        ifcopenshell.api.style.assign_material_style(library, material=material, style=style, context=subcontext)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=material)
        assert len(self.file.by_type("IfcMaterial")) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationSubContext", include_subtypes=False)) == 1
        subcontext = self.file.by_type("IfcMaterial")[0].HasRepresentation[0].Representations[0].ContextOfItems
        assert subcontext == file_subcontext
        # make sure it's still valid
        assert subcontext.ParentContext.WorldCoordinateSystem

    def test_append_a_material_with_a_representation_and_reuse_an_existing_context_by_a_new_subcontext(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        file_context = ifcopenshell.api.context.add_context(self.file, context_type="Model")

        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        material = ifcopenshell.api.material.add_material(library, name="Material")
        style = ifcopenshell.api.style.add_style(library)
        context = ifcopenshell.api.context.add_context(library, context_type="Model")
        subcontext = ifcopenshell.api.context.add_context(
            library,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=context,
        )
        ifcopenshell.api.style.assign_material_style(library, material=material, style=style, context=subcontext)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=material)
        assert len(self.file.by_type("IfcMaterial")) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationSubContext", include_subtypes=False)) == 1
        subcontext = self.file.by_type("IfcMaterial")[0].HasRepresentation[0].Representations[0].ContextOfItems
        assert subcontext.ContextType == "Model"
        assert subcontext.ContextIdentifier == "Body"
        assert subcontext.TargetView == "MODEL_VIEW"
        assert subcontext.ParentContext == file_context

    def test_append_a_profile_def(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        profile = library.createIfcIShapeProfileDef()
        ifcopenshell.api.project.append_asset(self.file, library=library, element=profile)
        assert len(self.file.by_type("IfcIShapeProfileDef")) == 1

    def test_append_a_product(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert len(self.file.by_type("IfcWall")) == 1

    def test_append_a_product_with_all_properties(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        ifcopenshell.api.pset.add_pset(library, product=element, name="Foo_Bar")
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert ifcopenshell.util.element.get_psets(self.file.by_type("IfcWall")[0])["Foo_Bar"]

    def test_append_a_product_with_its_type(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(library, related_objects=[element], relating_type=element_type)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert ifcopenshell.util.element.get_type(self.file.by_type("IfcWall")[0]).is_a("IfcWallType")

    def test_append_only_specified_occurrences_of_a_typed_product(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        element3 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(library, related_objects=[element], relating_type=element_type)
        ifcopenshell.api.type.assign_type(library, related_objects=[element2], relating_type=element_type)
        ifcopenshell.api.type.assign_type(library, related_objects=[element3], relating_type=element_type)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element2)
        assert len(ifcopenshell.util.element.get_types(self.file.by_type("IfcWallType")[0])) == 2
        assert len(self.file.by_type("IfcWall")) == 2

    def test_append_a_product_with_materials(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(library, name="Material")
        ifcopenshell.api.material.assign_material(library, products=[element], material=material)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert ifcopenshell.util.element.get_material(self.file.by_type("IfcWall")[0]).Name == "Material"

    def test_append_a_product_where_its_inverse_material_relationship_refers_to_product_types_not_in_scope(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        element_type2 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(library, related_objects=[element], relating_type=element_type)
        material = ifcopenshell.api.material.add_material(library, name="Material")
        ifcopenshell.api.material.assign_material(library, products=[element], material=material)
        ifcopenshell.api.material.assign_material(library, products=[element_type], material=material)
        ifcopenshell.api.material.assign_material(library, products=[element_type2], material=material)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert [e.GlobalId for e in self.file.by_type("IfcWallType")] == [element_type.GlobalId]

    def test_append_a_product_with_its_styles(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        item = library.createIfcBoundingBox()
        library.createIfcStyledItem(Item=item)
        representation = library.createIfcShapeRepresentation(Items=[item])
        element.Representation = library.createIfcProductDefinitionShape(Representations=[representation])
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert self.file.by_type("IfcStyledItem")[0].Item == self.file.by_type("IfcBoundingBox")[0]

    def test_append_a_product_with_openings(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        opening = ifcopenshell.api.root.create_entity(library, ifc_class="IfcOpeningElement")
        ifcopenshell.api.feature.add_feature(library, feature=opening, element=element)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        assert self.file.by_type("IfcWall")[0].HasOpenings[0].RelatedOpeningElement.is_a("IfcOpeningElement")

    def test_append_a_product_when_projects_have_georeference(self):
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(ifc_file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(ifc_file)
        ifcopenshell.api.georeference.edit_georeferencing(
            ifc_file, coordinate_operation={"Eastings": 3.0, "Northings": 23.0}
        )

        library = ifcopenshell.file.from_string(ifc_file.to_string())
        ifcopenshell.api.georeference.edit_georeferencing(
            library, coordinate_operation={"Eastings": 29, "Northings": 42}
        )
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        matrix = np.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(library, element, matrix)
        new = ifcopenshell.api.project.append_asset(ifc_file, library=library, element=element)
        resulting_matrix = np.array(
            (
                (1.0, 0.0, 0.0, 27.0),
                (0.0, 1.0, 0.0, 21.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        assert np.array_equal(ifcopenshell.util.placement.get_local_placement(new.ObjectPlacement), resulting_matrix)

    def test_append_a_surface_style(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")

        style_name = "New Style"
        style = ifcopenshell.api.style.add_style(library, style_name)
        shading_attrs = {"SurfaceColour": {"Name": "", "Red": 1, "Green": 1, "Blue": 1}}
        ifcopenshell.api.style.add_surface_style(
            library, style, ifc_class="IfcSurfaceStyleShading", attributes=shading_attrs
        )

        new_style = ifcopenshell.api.project.append_asset(self.file, library=library, element=style)
        assert self.file.by_type("IfcSurfaceStyle") == [new_style]
        assert new_style.Name == style_name
        style_elements = new_style.Styles
        assert len(style_elements) == 1

        # Check shading style.
        shading_style = style_elements[0]
        assert shading_style.is_a("IfcSurfaceStyleShading")
        shading_colour_info = shading_style.SurfaceColour.get_info()
        del shading_colour_info["id"], shading_colour_info["type"]
        assert shading_colour_info == shading_attrs["SurfaceColour"]

    def test_update_rels_appending_subsequent_assets(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element1 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(library, product=element1, name="Test")
        element2 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        ifcopenshell.api.pset.assign_pset(library, pset=pset, products=[element2])

        reuse_identities = {}
        element1_ = ifcopenshell.api.project.append_asset(
            self.file, library, element1, reuse_identities=reuse_identities
        )
        element2_ = ifcopenshell.api.project.append_asset(
            self.file, library, element2, reuse_identities=reuse_identities
        )
        pset_data = ifcopenshell.util.element.get_psets(element1_)
        assert "Test" in pset_data
        assert ifcopenshell.util.element.get_psets(element2_) == pset_data

    def test_update_rels_appending_subsequent_assets_identifying_rels_by_guids(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element1 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(library, product=element1, name="Test")
        element2 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        pset_rel = ifcopenshell.api.pset.assign_pset(library, pset=pset, products=[element2])
        assert pset_rel
        pset_rel_guid: str = pset_rel.GlobalId

        element1_ = ifcopenshell.api.project.append_asset(self.file, library, element1)
        element2_ = ifcopenshell.api.project.append_asset(self.file, library, element2)
        pset_data = ifcopenshell.util.element.get_psets(element1_)

        appended_rels = [e for e in self.file.by_type("IfcRelDefinesByProperties") if e.GlobalId == pset_rel_guid]
        assert len(appended_rels) == 1
        assert set(appended_rels[0].RelatedObjects) == {element1_, element2_}
        assert ifcopenshell.util.element.get_psets(element2_) == pset_data

    def test_reuse_identities_to_avoid_removed_entities_and_possible_crashes(self):
        self.file.create_entity("IfcProject")
        context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        library.create_entity("IfcProject")
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        item = library.create_entity("IfcBoundingBox")
        lib_context = ifcopenshell.api.context.add_context(library, context_type="Model")
        representation = library.create_entity("IfcShapeRepresentation", Items=[item], ContextOfItems=lib_context)
        element.Representation = library.create_entity("IfcProductDefinitionShape", Representations=[representation])
        reuse_identities: dict[int, ifcopenshell.entity_instance] = {}
        ifcopenshell.api.project.append_asset(
            self.file, library=library, element=element, reuse_identities=reuse_identities
        )
        str(reuse_identities)  # Will trigger crash if there are no removed entities.

    def test_file_add_to_convert_units(self):
        library = ifcopenshell.file()
        builder = ShapeBuilder(library)
        ifcopenshell.api.root.create_entity(library, "IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(library, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(library, units=[unit])
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, "IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(ifc_file, units=[unit])

        # Simple floats.
        profile = ifcopenshell.api.profile.add_parameterized_profile(library, "IfcCircleProfileDef")
        profile.Radius = 10.0
        new_profile = ifcopenshell.api.project.append_asset(ifc_file, library, profile)
        assert new_profile.Radius == 0.01

        # Aggregates of floats.
        arbitrary_profile = builder.profile(builder.rectangle((1000, 1000)))
        new_arbitrary_profile = ifcopenshell.api.project.append_asset(ifc_file, library, arbitrary_profile)
        updated_points = np.array(arbitrary_profile.OuterCurve.Points) * 0.001
        assert np.allclose(updated_points, new_arbitrary_profile.OuterCurve.Points)

        # Entities without ids.
        annotation = ifcopenshell.api.root.create_entity(library, "IfcAnnotation")
        annotation.ObjectType = "LineOfSight"
        pset = ifcopenshell.api.pset.add_pset(library, annotation, "Pset_AnnotationLineOfSight")
        ifcopenshell.api.pset.edit_pset(library, pset, properties={"RoadVisibleDistanceLeft": 10})
        new_annotation = ifcopenshell.api.project.append_asset(ifc_file, library, annotation)
        assert (
            ifcopenshell.util.element.get_pset(new_annotation, "Pset_AnnotationLineOfSight", "RoadVisibleDistanceLeft")
            == 0.01
        )

    def test_append_presentation_layer_for_representation_item(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        builder = ShapeBuilder(library)
        model = ifcopenshell.api.context.add_context(library, context_type="Model")
        item = builder.extrude(builder.profile(builder.rectangle((1, 1))))
        representation = builder.get_representation(model, item)
        ifcopenshell.api.geometry.assign_representation(library, element, representation)
        layer = ifcopenshell.api.layer.add_layer(library, name="TestLayer")
        ifcopenshell.api.layer.assign_layer(library, items=[item], layer=layer)

        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        extrusions = tuple(self.file.by_type("IfcExtrudedAreaSolid"))
        assert self.file.by_type("IfcPresentationLayerAssignment")[0].AssignedItems == extrusions

    def test_append_presentation_layer_for_representation(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall")
        builder = ShapeBuilder(library)
        model = ifcopenshell.api.context.add_context(library, context_type="Model")
        item = builder.extrude(builder.profile(builder.rectangle((1, 1))))
        representation = builder.get_representation(model, item)
        ifcopenshell.api.geometry.assign_representation(library, element, representation)
        layer = ifcopenshell.api.layer.add_layer(library, name="TestLayer")
        ifcopenshell.api.layer.assign_layer(library, items=[representation], layer=layer)

        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.project.append_asset(self.file, library=library, element=element)
        representations = tuple(self.file.by_type("IfcRepresentation"))
        assert self.file.by_type("IfcPresentationLayerAssignment")[0].AssignedItems == representations

    def test_append_owner_history_without_producing_duplicates(self):
        ifc_file = ifcopenshell.file()
        library = ifcopenshell.file()

        # Setup owner history.
        ifcopenshell.api.owner.settings.factory_reset()
        person = ifcopenshell.api.owner.add_person(library)
        ifcopenshell.api.owner.add_role(library, person, "CONTRIBUTOR")
        organization = ifcopenshell.api.owner.add_organisation(library)
        user = ifcopenshell.api.owner.add_person_and_organisation(library, person=person, organisation=organization)
        application = ifcopenshell.api.owner.add_application(library)
        assert len(library.by_type("IfcPerson")) == 1
        assert len(library.by_type("IfcPersonAndOrganization")) == 1
        assert len(library.by_type("IfcApplication")) == 1
        assert len(library.by_type("IfcOrganization")) == 2

        # IfcOrganization's attributes.
        assert len(library.by_type("IfcTelecomAddress")) == 1
        # IfcPerson's attributes.
        assert len(library.by_type("IfcActorRole")) == 2

        # Add 2 wall types.
        wall_type_1 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        wall_type_2 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")

        ifcopenshell.api.project.append_asset(ifc_file, library, wall_type_1)
        ifcopenshell.api.project.append_asset(ifc_file, library, wall_type_2)

        assert len(ifc_file.by_type("IfcPerson")) == 1
        assert len(ifc_file.by_type("IfcPersonAndOrganization")) == 1
        assert len(ifc_file.by_type("IfcApplication")) == 1
        assert len(ifc_file.by_type("IfcOrganization")) == 2
        # Ensure their attributes are also not duplicated.
        assert len(ifc_file.by_type("IfcTelecomAddress")) == 1
        assert len(ifc_file.by_type("IfcActorRole")) == 2


class TestAppendAssetIFC4(test.bootstrap.IFC4, TestAppendAssetIFC2X3):
    # NOTE: breaks in IFC2X3 since IfcProfileDef doesn't have "HasProperties" inverse in ifc2x3
    # and we use it in whitelisted_inverse_attributes for appending IfcProfileDef
    def test_append_a_profile_def_with_all_properties(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        profile = library.createIfcIShapeProfileDef()
        ifcopenshell.api.pset.add_pset(library, product=profile, name="Foo_Bar")
        ifcopenshell.api.project.append_asset(self.file, library=library, element=profile)
        assert len(self.file.by_type("IfcIShapeProfileDef")) == 1
        assert self.file.by_type("IfcIShapeProfileDef")[0].HasProperties[0].Name == "Foo_Bar"

    # NOTE: breaks in IFC2X3 since IfcMaterial doesn't have "HasProperties" inverse in ifc2x3
    # and we use it in whitelisted_inverse_attributes for appending IfcTypeProduct
    def test_append_two_type_products_sharing_the_same_material_with_properties(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        element1 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType")
        material = ifcopenshell.api.material.add_material(library, name="Material")

        pset = ifcopenshell.api.pset.add_pset(library, product=material, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(library, pset=pset, properties={"Foo": "Bar"})

        ifcopenshell.api.material.assign_material(library, products=[element1], material=material)
        ifcopenshell.api.material.assign_material(library, products=[element2], material=material)
        new1 = ifcopenshell.api.project.append_asset(self.file, library=library, element=element1)
        new2 = ifcopenshell.api.project.append_asset(self.file, library=library, element=element2)

        assert len(self.file.by_type("IfcMaterialProperties")) == 1
        material = self.file.by_type("IfcMaterial")[0]
        assert ifcopenshell.util.element.get_material(new1) == material
        assert ifcopenshell.util.element.get_material(new2) == material
        assert ifcopenshell.util.element.get_psets(material)["Foo_Bar"]["Foo"] == "Bar"

    # NOTE: breaks in IFC2X3 since IfcCostItem doesn't have "IsNestedBy" inverse in ifc2x3
    # and we use it in whitelisted_inverse_attributes for appending IfcCostSchedule
    def test_append_a_cost_schedule(self):
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        schedule = ifcopenshell.api.cost.add_cost_schedule(library, name="Schedule")
        item = ifcopenshell.api.cost.add_cost_item(library, cost_schedule=schedule)
        item2 = ifcopenshell.api.cost.add_cost_item(library, cost_item=item)
        ifcopenshell.api.project.append_asset(self.file, library=library, element=schedule)
        assert len(self.file.by_type("IfcCostSchedule")) == 1
        assert len(self.file.by_type("IfcCostItem")) == 2
        assert self.file.by_type("IfcCostSchedule")[0].Name == "Schedule"
        appended_item = self.file.by_type("IfcCostSchedule")[0].Controls[0].RelatedObjects[0]
        assert appended_item.is_a("IfcCostItem")
        assert appended_item.IsNestedBy[0].RelatedObjects[0].is_a("IfcCostItem")

    def test_not_duplicate_profiles_materials_styles_based_on_name(self):
        # Setup library.
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(library, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            library, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        column_type = ifcopenshell.api.root.create_entity(library, "IfcColumnType")
        library_profile = ifcopenshell.api.profile.add_parameterized_profile(library, "IfcCircleProfileDef")
        library_profile.ProfileName = "TestProfile"
        material_set = ifcopenshell.api.material.add_material_set(library, set_type="IfcMaterialProfileSet")
        library_material = ifcopenshell.api.material.add_material(library, "TestMaterial")
        library_style = ifcopenshell.api.style.add_style(library, "TestStyle", ifc_class="IfcSurfaceStyle")
        ifcopenshell.api.style.assign_material_style(library, library_material, library_style, body)
        ifcopenshell.api.material.add_profile(library, material_set, library_material, library_profile)
        ifcopenshell.api.material.assign_material(
            library, [column_type], material=material_set, type="IfcMaterialProfileSet"
        )

        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        # Test adding a profile with existing name.
        profile = ifcopenshell.api.profile.add_parameterized_profile(self.file, "IfcCircleProfileDef")
        profile.ProfileName = "TestProfile"
        ifcopenshell.api.project.append_asset(self.file, library, library_profile)
        profiles = self.file.by_type("IfcProfileDef")
        assert len(profiles) == 1 and profiles[0].ProfileName == "TestProfile"

        # Test adding a material with existing name.
        ifcopenshell.api.material.add_material(self.file, "TestMaterial")
        ifcopenshell.api.project.append_asset(self.file, library, library_material)
        materials = self.file.by_type("IfcMaterial")
        assert len(materials) == 1 and materials[0].Name == "TestMaterial"

        # Test adding a style with existing name.
        ifcopenshell.api.style.add_style(self.file, "TestStyle", ifc_class="IfcSurfaceStyle")
        ifcopenshell.api.project.append_asset(self.file, library, library_style)
        styles = self.file.by_type("IfcSurfaceStyle")
        assert len(styles) == 1 and styles[0].Name == "TestStyle"

        # Test implicitly adding profile+material+style with existing names.
        ifcopenshell.api.project.append_asset(self.file, library, column_type)
        assert len(self.file.by_type("IfcColumnType")) == 1
        profiles = self.file.by_type("IfcProfileDef")
        assert len(profiles) == 1 and profiles[0].ProfileName == "TestProfile"
        materials = self.file.by_type("IfcMaterial")
        assert len(materials) == 1 and materials[0].Name == "TestMaterial"
        styles = self.file.by_type("IfcSurfaceStyle")
        assert len(styles) == 1 and styles[0].Name == "TestStyle"

    def test_duplicate_profiles_materials_styles_based_on_name_if_uniqueness_is_not_assumed(self):
        # Setup library.
        library = ifcopenshell.api.project.create_file(version=self.file.schema)
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(library, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            library, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        column_type = ifcopenshell.api.root.create_entity(library, "IfcColumnType")
        library_profile = ifcopenshell.api.profile.add_parameterized_profile(library, "IfcCircleProfileDef")
        library_profile.ProfileName = "TestProfile"
        material_set = ifcopenshell.api.material.add_material_set(library, set_type="IfcMaterialProfileSet")
        library_material = ifcopenshell.api.material.add_material(library, "TestMaterial")
        library_style = ifcopenshell.api.style.add_style(library, "TestStyle", ifc_class="IfcSurfaceStyle")
        ifcopenshell.api.style.assign_material_style(library, library_material, library_style, body)
        ifcopenshell.api.material.add_profile(library, material_set, library_material, library_profile)
        ifcopenshell.api.material.assign_material(
            library, [column_type], material=material_set, type="IfcMaterialProfileSet"
        )

        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        # Test adding a profile with existing name.
        profile = ifcopenshell.api.profile.add_parameterized_profile(self.file, "IfcCircleProfileDef")
        profile.ProfileName = "TestProfile"
        ifcopenshell.api.project.append_asset(
            self.file, library, library_profile, assume_asset_uniqueness_by_name=False
        )
        profiles = self.file.by_type("IfcProfileDef")
        assert len(profiles) == 2 and all(p.ProfileName == "TestProfile" for p in profiles)

        # Test adding a material with existing name.
        ifcopenshell.api.material.add_material(self.file, "TestMaterial")
        ifcopenshell.api.project.append_asset(
            self.file, library, library_material, assume_asset_uniqueness_by_name=False
        )
        materials = self.file.by_type("IfcMaterial")
        assert len(materials) == 2 and all(m.Name == "TestMaterial" for m in materials)

        # Test adding a style with existing name.
        ifcopenshell.api.style.add_style(self.file, "TestStyle", ifc_class="IfcSurfaceStyle")
        ifcopenshell.api.project.append_asset(self.file, library, library_style, assume_asset_uniqueness_by_name=False)
        styles = self.file.by_type("IfcSurfaceStyle")
        assert len(styles) == 2 and all(s.Name == "TestStyle" for s in styles)

        # Test implicitly adding profile+material+style with existing names.
        ifcopenshell.api.project.append_asset(self.file, library, column_type, assume_asset_uniqueness_by_name=False)
        assert len(self.file.by_type("IfcColumnType")) == 1
        profiles = self.file.by_type("IfcProfileDef")
        assert len(profiles) == 2 and all(p.ProfileName == "TestProfile" for p in profiles)
        materials = self.file.by_type("IfcMaterial")
        assert len(materials) == 2 and all(m.Name == "TestMaterial" for m in materials)
        styles = self.file.by_type("IfcSurfaceStyle")
        assert len(styles) == 2 and all(s.Name == "TestStyle" for s in styles)
