# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell.api
import ifcopenshell.api.profile
import ifcopenshell.util.element
import bonsai.bim.helper
import bonsai.tool as tool
import bonsai.bim.module.model.profile as model_profile
import bonsai.core.profile as core
from bonsai.bim.module.model.decorator import ProfileDecorator
from bonsai.bim.module.profile.prop import generate_thumbnail_for_active_profile
from bonsai.bim.module.profile.data import refresh
from bonsai.bim.module.geometry.helper import Helper


class LoadProfiles(bpy.types.Operator):
    bl_idname = "bim.load_profiles"
    bl_label = "Load Profiles"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Profile.get_profile_props()
        props.profiles.clear()

        filter_material_profiles = props.is_filtering_material_profiles

        for profile in tool.Ifc.get().by_type("IfcProfileDef"):
            if filter_material_profiles:
                inverse_references = tool.Ifc.get().get_inverse(profile)
                related_material_profiles = next(
                    (ref for ref in inverse_references if ref.is_a("IfcMaterialProfile")), None
                )
                if not related_material_profiles:
                    continue
            if not profile.ProfileName:
                continue
            new = props.profiles.add()
            new.ifc_definition_id = profile.id()
            new["name"] = profile.ProfileName or "Unnamed"
            new.ifc_class = profile.is_a()

        props.is_editing = True
        bpy.ops.bim.disable_editing_profile()
        return {"FINISHED"}


class DisableProfileEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_profile_editing_ui"
    bl_label = "Disable Profile Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Profile.get_profile_props()
        props.is_editing = False
        return {"FINISHED"}


class RemoveProfileDef(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_profile_def"
    bl_label = "Remove Profile Definition"
    bl_options = {"REGISTER", "UNDO"}
    profile: bpy.props.IntProperty()

    def _execute(self, context):
        props = tool.Profile.get_profile_props()
        current_index = props.active_profile_index

        ifc_file = tool.Ifc.get()
        profile = ifc_file.by_id(self.profile)

        # Save user from creating invalid IFC.
        inverse_classes = {i.is_a() for i in ifc_file.get_inverse(profile)}
        schema = ifcopenshell.schema_by_name(ifc_file.schema)

        # Allow removing profile with IfcProfileProperties.
        for inverse_class in inverse_classes.copy():
            declaration = schema.declaration_by_name(inverse_class)
            if declaration._is("IfcProfileProperties"):
                inverse_classes.remove(inverse_class)

        if inverse_classes:
            error_msg = "Cannot remove profile as it's still part of other IFC entities:"
            for inverse_class in inverse_classes:
                error_msg += "\n- " + inverse_class
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}

        ifcopenshell.api.profile.remove_profile(ifc_file, profile=profile)
        bpy.ops.bim.load_profiles()

        # preserve selected index if possible
        props.active_profile_index = tool.Blender.get_valid_uilist_index(props.active_profile_index, props.profiles)


class EnableEditingProfile(bpy.types.Operator):
    bl_idname = "bim.enable_editing_profile"
    bl_label = "Enable Editing Profile"
    bl_options = {"REGISTER", "UNDO"}
    profile: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Profile.get_profile_props()
        props.profile_attributes.clear()
        bonsai.bim.helper.import_attributes2(tool.Ifc.get().by_id(self.profile), props.profile_attributes)
        props.active_profile_id = self.profile
        return {"FINISHED"}


class DisableEditingProfile(bpy.types.Operator):
    bl_idname = "bim.disable_editing_profile"
    bl_label = "Disable Editing Profile"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Profile.get_profile_props()
        props.active_profile_id = 0
        bpy.ops.bim.disable_editing_arbitrary_profile()
        return {"FINISHED"}


class EditProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_profile"
    bl_label = "Edit Profile"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Profile.get_profile_props()
        attributes = bonsai.bim.helper.export_attributes(props.profile_attributes)
        profile = tool.Ifc.get().by_id(props.active_profile_id)
        ifcopenshell.api.profile.edit_profile(tool.Ifc.get(), profile=profile, attributes=attributes)
        model_profile.DumbProfileRegenerator().regenerate_from_profile_def(profile)
        bpy.ops.bim.load_profiles()
        generate_thumbnail_for_active_profile()


class AddProfileDef(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_profile_def"
    bl_label = "Add Profile"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Profile.get_profile_props()
        profile_class = props.profile_classes
        if profile_class == "IfcArbitraryClosedProfileDef":
            obj = props.object_to_profile
            indices = []
            if obj:
                if len(obj.data.polygons) == 0:
                    self.report(
                        {"WARNING"},
                        "This mesh is invalid to create a profile. Select a flat mesh with at least one face.",
                    )
                    props.object_to_profile = None
                    return
                helper = Helper(tool.Ifc.get())
                indices = helper.auto_detect_arbitrary_profile_with_voids_extruded_area_solid(obj.data)
                if not indices["inner_curves"]:
                    indices = helper.auto_detect_arbitrary_closed_profile_extruded_area_solid(obj.data)
            props.object_to_profile = None
            if not indices:
                points = [(0, 0), (0.1, 0), (0.1, 0.1), (0, 0.1), (0, 0)]
                profile = ifcopenshell.api.profile.add_arbitrary_profile(tool.Ifc.get(), profile=points)
            else:
                assert obj and isinstance(obj.data, bpy.types.Mesh)
                if "inner_curves" not in indices:
                    points = [(obj.data.vertices[i].co.x, obj.data.vertices[i].co.y) for i in indices["profile"]]
                    points.append(points[0])
                    profile = ifcopenshell.api.profile.add_arbitrary_profile(tool.Ifc.get(), profile=points)
                else:
                    outer_points = [(obj.data.vertices[i].co.x, obj.data.vertices[i].co.y) for i in indices["profile"]]
                    outer_points.append(outer_points[0])
                    inner_points = [
                        [(obj.data.vertices[i].co.x, obj.data.vertices[i].co.y) for i in curve]
                        for curve in indices["inner_curves"]
                    ]
                    for curve in inner_points:
                        curve.append(curve[0])
                    profile = ifcopenshell.api.profile.add_arbitrary_profile_with_voids(
                        tool.Ifc.get(),
                        outer_profile=outer_points,
                        inner_profiles=inner_points,
                    )

        else:
            profile = ifcopenshell.api.profile.add_parameterized_profile(tool.Ifc.get(), ifc_class=profile_class)
            tool.Profile.set_default_profile_attrs(profile)
        profile.ProfileName = "New Profile"
        bpy.ops.bim.load_profiles()


class DuplicateProfileDef(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.duplicate_profile_def"
    bl_label = "Duplicate Profile"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        active_profile = tool.Profile.get_active_profile_ui()
        if active_profile is not None:
            return True
        cls.poll_message_set("No profile selected to duplicate.")
        return False

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        profile_item = tool.Profile.get_active_profile_ui()
        assert profile_item
        profile = ifc_file.by_id(profile_item.ifc_definition_id)
        tool.Profile.duplicate_profile(profile)
        bpy.ops.bim.load_profiles()


class EnableEditingArbitraryProfile(bpy.types.Operator):
    bl_idname = "bim.enable_editing_arbitrary_profile"
    bl_label = "Enable Editing Arbitrary Profile"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Profile.get_profile_props()
        active_profile = props.profiles[props.active_profile_index]
        profile_id = active_profile.ifc_definition_id
        profile = tool.Ifc.get().by_id(profile_id)

        try:
            obj = tool.Model.import_profile(profile)
        except tool.Model.UnsupportedCurveForConversion as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        props.active_arbitrary_profile_id = profile_id
        tool.Ifc.link(profile, obj)
        bpy.context.scene.collection.objects.link(obj)
        tool.Blender.select_and_activate_single_object(context, obj)
        bpy.ops.object.mode_set(mode="EDIT")
        ProfileDecorator.install(context, exit_edit_mode_callback=lambda: disable_editing_arbitrary_profile(context))
        tool.Blender.set_viewport_tool("bim.cad_tool")
        return {"FINISHED"}


def disable_editing_arbitrary_profile(context):
    obj = context.active_object
    if (
        obj
        and (mesh := obj.data)
        and isinstance(mesh, bpy.types.Mesh)
        and tool.Geometry.get_mesh_props(mesh).subshape_type == "PROFILE"
    ):
        ProfileDecorator.uninstall()
        bpy.ops.object.mode_set(mode="OBJECT")
        profile_mesh = obj.data
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(profile_mesh)

    props = tool.Profile.get_profile_props()
    props.active_arbitrary_profile_id = 0
    # need to update profile manager ui
    # if this was called from decorator
    refresh()


class DisableEditingArbitraryProfile(bpy.types.Operator):
    bl_idname = "bim.disable_editing_arbitrary_profile"
    bl_label = "Disable Editing Arbitrary Profile"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        disable_editing_arbitrary_profile(context)
        return {"FINISHED"}


class EditArbitraryProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_arbitrary_profile"
    bl_label = "Edit Arbitrary Profile"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Profile.get_profile_props()
        old_profile = tool.Ifc.get().by_id(props.active_arbitrary_profile_id)

        obj = context.active_object

        ProfileDecorator.uninstall()
        bpy.ops.object.mode_set(mode="OBJECT")

        profile = tool.Model.export_profile(obj)
        if not profile:

            def msg(self, context):
                self.layout.label(text="INVALID PROFILE")

            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            ProfileDecorator.install(
                context, exit_edit_mode_callback=lambda: disable_editing_arbitrary_profile(context)
            )
            bpy.ops.object.mode_set(mode="EDIT")
            return

        prev_profile_id = profile.id()
        profile_mesh = obj.data
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(profile_mesh)

        profile.ProfileType = old_profile.ProfileType
        profile.ProfileName = old_profile.ProfileName
        for inverse in tool.Ifc.get().get_inverse(old_profile):
            ifcopenshell.util.element.replace_attribute(inverse, old_profile, profile)
        ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), old_profile)
        bpy.ops.bim.load_profiles()
        if props.active_profile_id == prev_profile_id:
            props.active_profile_id = profile.id()
        props.active_arbitrary_profile_id = 0

        model_profile.DumbProfileRegenerator().regenerate_from_profile_def(profile)


class SelectProfileInProfilesUI(bpy.types.Operator):
    bl_idname = "bim.profiles_ui_select"
    bl_label = "Select Profile In Profiles UI"
    bl_options = {"REGISTER", "UNDO"}
    profile_id: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Profile.get_profile_props()
        ifc_file = tool.Ifc.get()
        profile = ifc_file.by_id(self.profile_id)
        bpy.ops.bim.load_profiles()

        profile_index = next((i for i, m in enumerate(props.profiles) if m.ifc_definition_id == self.profile_id), None)
        if profile_index is None:
            self.report({"INFO"}, "Profile not found in Profiles UI. Perhaps it's unnamed?")
            return {"CANCELLED"}

        props.active_profile_index = profile_index
        self.report(
            {"INFO"},
            f"Profile '{profile.ProfileName or 'Unnamed'}' is selected in Profiles UI.",
        )
        return {"FINISHED"}


class SelectByProfile(bpy.types.Operator):
    bl_idname = "bim.select_by_profile"
    bl_label = "Select by Profile"
    bl_description = "Select objects using the provided profile."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        active_profile = tool.Profile.get_active_profile_ui()
        if active_profile is not None:
            return True
        cls.poll_message_set("No profile selected to select elements.")
        return False

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        profile_item = tool.Profile.get_active_profile_ui()
        assert profile_item
        profile = ifc_file.by_id(profile_item.ifc_definition_id)
        elements = ifcopenshell.util.element.get_elements_by_profile(profile)
        objects = [o for e in elements if (o := tool.Ifc.get_object(e))]
        if objects:
            tool.Spatial.select_products(elements)
        self.report(
            {"INFO"}, f"{len(elements)} elements were found using profile, {len(objects)} objects were selected."
        )
        return {"FINISHED"}
