# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.pset_template
import bonsai.bim.schema
import bonsai.bim.handler
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore


class AddPsetTemplateFile(bpy.types.Operator):
    bl_idname = "bim.add_pset_template_file"
    bl_label = "Add Pset Template File"
    bl_options = {"REGISTER", "UNDO"}

    new_template_filename: bpy.props.StringProperty(name="New Template Filename", options={"SKIP_SAVE"})

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)

    def draw(self, context):
        self.layout.prop(self, "new_template_filename", text="Filename")

    def execute(self, context):
        template = ifcopenshell.file()
        filepath = (tool.Blender.get_data_dir_path("pset") / self.new_template_filename).with_suffix(".ifc").__str__()

        pset_template = ifcopenshell.api.pset_template.add_pset_template(template)
        ifcopenshell.api.pset_template.add_prop_template(template, pset_template=pset_template)
        template.write(filepath)
        bonsai.bim.handler.refresh_ui_data()
        bonsai.bim.schema.reload(tool.Ifc.get().schema)
        props = tool.PsetTemplate.get_pset_template_props()
        props.pset_template_files = filepath
        tool.PsetTemplate.enable_editing_pset_template()
        return {"FINISHED"}


class AddPsetTemplate(bpy.types.Operator, tool.PsetTemplate.PsetTemplateOperator):
    bl_idname = "bim.add_pset_template"
    bl_label = "Add Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        existing_psets = {template.Name for template in self.template_file.by_type("IfcPropertySetTemplate")}
        name = tool.Blender.ensure_unique_name("New_Pset", existing_psets)
        template = ifcopenshell.api.pset_template.add_pset_template(self.template_file, name=name)
        ifcopenshell.api.pset_template.add_prop_template(self.template_file, pset_template=template)
        self.template_file.write(IfcStore.pset_template_path)
        bonsai.bim.handler.refresh_ui_data()
        bonsai.bim.schema.reload(tool.Ifc.get().schema)
        props = tool.PsetTemplate.get_pset_template_props()
        props.pset_templates = str(template.id())


class RemovePsetTemplate(bpy.types.Operator, tool.PsetTemplate.PsetTemplateOperator):
    bl_idname = "bim.remove_pset_template"
    bl_label = "Remove Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.PsetTemplate.get_pset_template_props()
        current_pset_template_id = int(props.pset_templates)
        if props.active_pset_template_id == current_pset_template_id:
            bpy.ops.bim.disable_editing_pset_template()
        ifcopenshell.api.pset_template.remove_pset_template(
            self.template_file,
            pset_template=self.template_file.by_id(current_pset_template_id),
        )
        self.template_file.write(IfcStore.pset_template_path)
        bonsai.bim.handler.refresh_ui_data()
        bonsai.bim.schema.reload(tool.Ifc.get().schema)
        tool.Blender.ensure_enum_is_valid(props, "pset_templates")


class EnableEditingPsetTemplate(bpy.types.Operator):
    bl_idname = "bim.enable_editing_pset_template"
    bl_label = "Enable Editing Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        tool.PsetTemplate.enable_editing_pset_template()
        return {"FINISHED"}


class DisableEditingPsetTemplate(bpy.types.Operator):
    bl_idname = "bim.disable_editing_pset_template"
    bl_label = "Disable Editing Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.PsetTemplate.get_pset_template_props()
        props.active_pset_template_id = 0
        return {"FINISHED"}


class EnableEditingPropTemplate(bpy.types.Operator):
    bl_idname = "bim.enable_editing_prop_template"
    bl_label = "Enable Editing Prop Template"
    bl_options = {"REGISTER", "UNDO"}
    prop_template: bpy.props.IntProperty()

    def execute(self, context):
        tool.PsetTemplate.enable_editing_prop_template(IfcStore.pset_template_file.by_id(self.prop_template))
        return {"FINISHED"}


class DeletePropEnum(bpy.types.Operator):
    bl_idname = "bim.delete_prop_enum"
    bl_label = "Delete Property Enumeration"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.PsetTemplate.get_pset_template_props()
        active_prop = props.active_prop_template
        active_prop.enum_values.remove(self.index)
        return {"FINISHED"}


class AddPropEnum(bpy.types.Operator):
    bl_idname = "bim.add_prop_enum"
    bl_label = "Add Property Enumeration"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.PsetTemplate.get_pset_template_props()
        active_prop = props.active_prop_template
        active_prop.enum_values.add()
        return {"FINISHED"}


class DisableEditingPropTemplate(bpy.types.Operator):
    bl_idname = "bim.disable_editing_prop_template"
    bl_label = "Disable Editing Prop Template"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.PsetTemplate.get_pset_template_props()
        props.active_prop_template_id = 0
        return {"FINISHED"}


class EditPsetTemplate(bpy.types.Operator, tool.PsetTemplate.PsetTemplateOperator):
    bl_idname = "bim.edit_pset_template"
    bl_label = "Edit Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.PsetTemplate.get_pset_template_props()
        ifcopenshell.api.pset_template.edit_pset_template(
            IfcStore.pset_template_file,
            pset_template=IfcStore.pset_template_file.by_id(props.active_pset_template_id),
            attributes={
                "Name": props.active_pset_template.name,
                "Description": props.active_pset_template.description,
                "TemplateType": props.active_pset_template.template_type,
                "ApplicableEntity": props.active_pset_template.applicable_entity,
            },
        )
        bpy.ops.bim.disable_editing_pset_template()
        IfcStore.pset_template_file.write(IfcStore.pset_template_path)
        bonsai.bim.handler.refresh_ui_data()
        bonsai.bim.schema.reload(tool.Ifc.get().schema)


class SavePsetTemplateFile(bpy.types.Operator):
    bl_idname = "bim.save_pset_template_file"
    bl_label = "Save Pset Template File"

    def execute(self, context):
        IfcStore.pset_template_file.write(IfcStore.pset_template_path)
        bonsai.bim.handler.refresh_ui_data()
        bonsai.bim.schema.reload(tool.Ifc.get().schema)
        return {"FINISHED"}


class RemovePsetTemplateFile(bpy.types.Operator):
    bl_idname = "bim.remove_pset_template_file"
    bl_label = "Remove Pset Template File"
    bl_description = "Remove pset template file from disk.\nWARNING. Be careful as this action is irreversible"

    def execute(self, context):
        try:
            os.remove(IfcStore.pset_template_path)
        except:
            pass
        bonsai.bim.handler.refresh_ui_data()
        bonsai.bim.schema.reload(tool.Ifc.get().schema)

        # Ensure enum is valid after deletion.
        self.props = tool.PsetTemplate.get_pset_template_props()
        if not tool.Blender.ensure_enum_is_valid(self.props, "pset_template_files"):
            self.update_template_files_prop(context)
        return {"FINISHED"}

    def update_template_files_prop(self, context: bpy.types.Context) -> None:
        import bonsai.bim.module.pset_template.prop

        bonsai.bim.module.pset_template.prop.updatePsetTemplateFiles(self.props, context)


class AddPropTemplate(bpy.types.Operator, tool.PsetTemplate.PsetTemplateOperator):
    bl_idname = "bim.add_prop_template"
    bl_label = "Add Prop Template"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.PsetTemplate.get_pset_template_props()
        pset_template_id = props.active_pset_template_id or int(props.pset_templates)
        prop_template = ifcopenshell.api.pset_template.add_prop_template(
            IfcStore.pset_template_file,
            pset_template=IfcStore.pset_template_file.by_id(pset_template_id),
        )
        bpy.ops.bim.disable_editing_prop_template()
        IfcStore.pset_template_file.write(IfcStore.pset_template_path)
        bonsai.bim.handler.refresh_ui_data()
        bonsai.bim.schema.reload(tool.Ifc.get().schema)
        tool.PsetTemplate.enable_editing_prop_template(prop_template)


class RemovePropTemplate(bpy.types.Operator, tool.PsetTemplate.PsetTemplateOperator):
    bl_idname = "bim.remove_prop_template"
    bl_label = "Remove Prop Template"
    bl_options = {"REGISTER", "UNDO"}
    prop_template: bpy.props.IntProperty()

    def _execute(self, context):
        ifcopenshell.api.pset_template.remove_prop_template(
            IfcStore.pset_template_file,
            prop_template=IfcStore.pset_template_file.by_id(self.prop_template),
        )
        IfcStore.pset_template_file.write(IfcStore.pset_template_path)
        bonsai.bim.handler.refresh_ui_data()
        bonsai.bim.schema.reload(tool.Ifc.get().schema)


class EditPropTemplate(bpy.types.Operator, tool.PsetTemplate.PsetTemplateOperator):
    bl_idname = "bim.edit_prop_template"
    bl_label = "Edit Prop Template"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        assert IfcStore.pset_template_file
        props = tool.PsetTemplate.get_pset_template_props()
        active_prop_template = props.active_prop_template
        if props.active_prop_template.template_type == "P_ENUMERATEDVALUE":
            data_type = props.active_prop_template.get_value_name()
            prop = props.active_prop_template
            enumerators = [getattr(ev, data_type) for ev in prop.enum_values]
        else:
            enumerators = None

        template_type = active_prop_template.template_type
        primary_measure_type = active_prop_template.primary_measure_type
        # Quantities don't use primary measure type.
        if primary_measure_type == "-" or template_type.startswith("Q_"):
            primary_measure_type = None

        ifcopenshell.api.pset_template.edit_prop_template(
            IfcStore.pset_template_file,
            prop_template=IfcStore.pset_template_file.by_id(props.active_prop_template_id),
            attributes={
                "Name": props.active_prop_template.name,
                "Description": props.active_prop_template.description,
                "PrimaryMeasureType": primary_measure_type,
                "TemplateType": template_type,
                "Enumerators": enumerators,
            },
        )
        bpy.ops.bim.disable_editing_prop_template()
        IfcStore.pset_template_file.write(IfcStore.pset_template_path)
        bonsai.bim.handler.refresh_ui_data()
        if tool.Ifc.get():
            bonsai.bim.schema.reload(tool.Ifc.get().schema)


class SelectPsetTemplatesInUI(bpy.types.Operator):
    bl_idname = "bim.pset_templates_ui_select"
    bl_label = "Select Pset Template in UI"
    bl_description = "Select pset template for the provided pset in Pset Template UI."
    bl_options = {"REGISTER", "UNDO"}
    pset_id: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.PsetTemplate.get_pset_template_props()
        ifc_file = tool.Ifc.get()
        pset = ifc_file.by_id(self.pset_id)

        pset_template_file: ifcopenshell.file
        pset_template = None
        path = None
        for path, _ in tool.PsetTemplate.get_pset_template_files():
            pset_template_file = ifcopenshell.open(path)
            for pset_template in pset_template_file.by_type("IfcPropertySetTemplate"):
                if pset_template.Name == pset.Name:
                    break

        if pset_template is None or path is None:
            self.report({"INFO"}, f"Couldn't find pset template for the provided pset: '{pset.Name}'.")
            return {"CANCELLED"}

        props.pset_template_files = str(path)
        props.pset_templates = str(pset_template.id())

        self.report(
            {"INFO"},
            f"Pset Template '{pset.Name}' is selected in Pset Templates UI. See Property Set Templates in Project tab.",
        )
        return {"FINISHED"}
