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

from __future__ import annotations
import bpy
import os
import bonsai.bim
import bonsai.tool as tool
from bonsai.bim.helper import prop_with_search, draw_attributes
from bpy.types import Panel, Menu, UIList
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.project.data import ProjectData, LinksData
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.project.prop import LibraryElement, BIMProjectProperties, FilterCategory, Link


def file_import_menu(self, context):
    op = self.layout.operator("bim.load_project", text="IFC (Geometry Only) (.ifc/.ifczip/.ifcxml)")
    op.import_without_ifc_data = True
    op.should_start_fresh_session = False


def refresh():
    UIData.is_loaded = False


class UIData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"menu_item_icon_color_mode": cls.icon_color_mode("user_interface.wcol_menu_item.text")}
        cls.is_loaded = True

    @classmethod
    def icon_color_mode(cls, color_path):
        return tool.Blender.detect_icon_color_mode(color_path)


class BIM_MT_project(Menu):
    bl_idname = "BIM_MT_project"
    bl_label = "New IFC Project"

    def draw(self, context):
        self.layout.operator("bim.new_project", text="New Metric (m) Project").preset = "metric_m"
        self.layout.operator("bim.new_project", text="New Metric (mm) Project").preset = "metric_mm"
        self.layout.operator("bim.new_project", text="New Imperial (ft) Project").preset = "imperial_ft"
        self.layout.operator("bim.new_project", text="New Demo Project").preset = "demo"
        self.layout.operator("bim.new_project", text="New Project Wizard").preset = "wizard"


class BIM_MT_recent_projects(Menu):
    bl_idname = "BIM_MT_recent_projects"
    bl_label = "Open Recent IFC Project"

    def draw(self, context):
        if not UIData.is_loaded:
            UIData.load()
        ifc_icon = f"{UIData.data['menu_item_icon_color_mode']}_ifc"
        layout = self.layout
        paths = tool.Project.get_recent_ifc_projects()
        if not paths:
            self.layout.label(text="No Recent IFC Projects")
            return

        for path in paths:
            row = layout.row()
            op = row.operator("bim.load_project", text=path.name, icon_value=bonsai.bim.icons[ifc_icon].icon_id)
            op.filepath = str(path)
            op.should_start_fresh_session = True
            op.use_detailed_tooltip = True
            row.enabled = path.is_file()

        self.layout.separator()
        self.layout.operator("bim.clear_recent_ifc_projects", icon="TRASH")


class BIM_MT_new_project(Menu):
    bl_idname = "BIM_MT_new_project"
    bl_label = "New Project"

    def draw(self, context):
        self.layout.operator_context = "INVOKE_DEFAULT"
        op = self.layout.operator("bim.load_project", text="Open IFC Project", icon="FILEBROWSER")
        op.should_start_fresh_session = True
        self.layout.menu("BIM_MT_recent_projects", icon="NONE")
        # Do we need to set it back to exec default?
        # self.layout.operator_context = "EXEC_DEFAULT"
        self.layout.separator()
        self.layout.label(text="New IFC Project", icon_value=bonsai.bim.icons["IFC"].icon_id)
        self.layout.operator("bim.new_project", text="Metric (m) Project").preset = "metric_m"
        self.layout.operator("bim.new_project", text="Metric (mm) Project").preset = "metric_mm"
        self.layout.operator("bim.new_project", text="Imperial (ft) Project").preset = "imperial_ft"
        self.layout.operator("bim.new_project", text="Demo Project").preset = "demo"
        self.layout.operator("bim.new_project", text="Project Wizard").preset = "wizard"
        self.layout.separator()
        self.layout.label(text="New Blender Project", icon="BLENDER")
        # In theory we can dynamically grab the list from list(bpy.utils.app_template_paths())
        self.layout.operator("wm.read_homefile", text="General Project").app_template = ""
        self.layout.operator("wm.read_homefile", text="2D Animation Project").app_template = "2D_Animation"
        self.layout.operator("wm.read_homefile", text="Sculpting Project").app_template = "Sculpting"
        self.layout.operator("wm.read_homefile", text="VFX Project").app_template = "VFX"
        self.layout.operator("wm.read_homefile", text="Video Editing Project").app_template = "Video_Editing"


def file_menu(self, context):
    self.layout.menu("BIM_MT_project", icon="COLLECTION_NEW")
    op = self.layout.operator("bim.load_project", text="Open IFC Project", icon="FILEBROWSER")
    op.should_start_fresh_session = True
    self.layout.menu("BIM_MT_recent_projects", icon="NONE")
    self.layout.separator()
    op = self.layout.operator("bim.save_project", icon="FILE_TICK", text="Save IFC Project")
    op.should_save_as = False
    op = self.layout.operator("bim.save_project", text="Save IFC Project As...")
    op.should_save_as = True
    self.layout.separator()
    self.layout.operator("bim.revert_project")
    self.layout.separator()


class BIM_PT_project(Panel):
    bl_label = "Current Project"
    bl_idname = "BIM_PT_project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"HIDE_HEADER"}
    bl_parent_id = "BIM_PT_tab_project_info"

    def draw(self, context):
        if not ProjectData.is_loaded:
            ProjectData.load()

        self.layout.use_property_decorate = False
        self.layout.use_property_split = True
        props = tool.Blender.get_bim_props()
        pprops = self.props = tool.Project.get_project_props()
        self.file = tool.Ifc.get()
        if pprops.is_loading:
            self.draw_advanced_loading_ui(context)
        elif self.file or props.ifc_file:
            if props.has_blend_warning:
                box = self.layout.box()
                box.alert = True
                row = box.row(align=True)
                row.label(text="Your Model May Be Outdated", icon="ERROR")
                op = row.operator("bim.open_uri", text="", icon="QUESTION")
                op.uri = "https://docs.bonsaibim.org/guides/troubleshooting.html#saving-and-loading-blend-files"
                row.operator("bim.close_blend_warning", text="", icon="CANCEL")

            if props.ifc_file:
                self.draw_loaded_project_ui(context)
            else:
                self.draw_unsaved_project_ui(context)

    def draw_advanced_loading_ui(self, context):
        pprops = self.props
        prop_with_search(self.layout, pprops, "filter_mode")
        if pprops.filter_mode in ["DECOMPOSITION", "IFC_CLASS", "IFC_TYPE"]:
            row = self.layout.row(align=True)
            row.label(text=f"Total: {pprops.total_elements}")
            row.operator("bim.toggle_filter_categories", text="", icon="CHECKBOX_HLT").should_select = True
            row.operator("bim.toggle_filter_categories", text="", icon="CHECKBOX_DEHLT").should_select = False
            self.layout.template_list(
                "BIM_UL_filter_categories",
                "",
                pprops,
                "filter_categories",
                pprops,
                "active_filter_category_index",
            )
        elif pprops.filter_mode in ["WHITELIST", "BLACKLIST"]:
            row = self.layout.row()
            row.prop(pprops, "filter_query")
        if pprops.filter_mode != "NONE":
            row = self.layout.row()
            row.prop(pprops, "should_filter_spatial_elements")
        row = self.layout.row()
        row.prop(pprops, "should_use_cpu_multiprocessing")
        row = self.layout.row()
        row.prop(pprops, "should_clean_mesh")
        row = self.layout.row()
        row.prop(pprops, "should_cache")
        row = self.layout.row()
        row.prop(pprops, "should_load_geometry")
        row = self.layout.row()
        row.prop(pprops, "should_merge_materials_by_colour")
        self.layout.prop(pprops, "load_indexed_maps")
        row = self.layout.row()
        row.prop(pprops, "geometry_library")
        row = self.layout.row()
        row.prop(pprops, "deflection_tolerance")
        row = self.layout.row()
        row.prop(pprops, "angular_tolerance")
        row = self.layout.row()
        row.prop(pprops, "void_limit")
        row = self.layout.row()
        row.prop(pprops, "style_limit")
        row = self.layout.row()
        row.prop(pprops, "distance_limit")
        row = self.layout.row()
        row.prop(pprops, "false_origin_mode")
        if pprops.false_origin_mode == "MANUAL":
            row = self.layout.row()
            row.prop(pprops, "false_origin")
            row = self.layout.row()
            row.prop(pprops, "project_north")

        if ProjectData.data["total_elements"] > 30000:
            box = self.layout.box()
            box.alert = True
            row = box.row()
            row.alignment = "CENTER"
            row.label(text=f"Large Model ({ProjectData.data['total_elements']} Elements)", icon="ERROR")
            row = box.row()
            row.alignment = "CENTER"
            row.label(text="Large models may slow down Bonsai")

        row = self.layout.row()
        row.prop(pprops, "element_limit_mode")

        if pprops.element_limit_mode == "RANGE":
            row = self.layout.row()
            row.label(text="Element Range")
            row = self.layout.row(align=True)
            row.prop(pprops, "element_offset", text="")
            row.prop(pprops, "element_limit", text="")

        row = self.layout.row(align=True)
        row.operator("bim.load_project_elements")

    def draw_editing_buttons(self, context, row):
        pprops = self.props
        if tool.Ifc.get():
            if pprops.is_editing:
                row.operator("bim.edit_header", icon="CHECKMARK", text="")
                row.operator("bim.disable_editing_header", icon="CANCEL", text="")
            else:
                row.operator("bim.enable_editing_header", icon="GREASEPENCIL", text="")

    def draw_editable_file_info(self, context):
        pprops = self.props

        if tool.Ifc.get():
            row = self.layout.row(align=True)
            row.label(text="IFC Schema", icon="FILE_CACHE")
            row.label(text=tool.Ifc.get().schema)

            if pprops.is_editing:
                row = self.layout.row(align=True)
                row.prop(pprops, "mvd")

                row = self.layout.row(align=True)
                row.prop(pprops, "author_name")
                row = self.layout.row(align=True)
                row.prop(pprops, "author_email")

                row = self.layout.row(align=True)
                row.prop(pprops, "organisation_name")
                row = self.layout.row(align=True)
                row.prop(pprops, "organisation_email")

                row = self.layout.row(align=True)
                row.prop(pprops, "authorisation")
            else:
                row = self.layout.row(align=True)
                row.label(text="IFC MVD", icon="FILE_HIDDEN")
                mvd = "".join(tool.Ifc.get().wrapped_data.header.file_description.description)
                if "[" in mvd:
                    mvd = mvd.split("[")[1][0:-1]
                row.label(text=mvd)

        else:
            row = self.layout.row(align=True)
            row.label(text="File Not Loaded", icon="ERROR")

    def draw_unsaved_project_ui(self, context):
        # file name row
        file_name_row = self.layout.row(align=True)
        file_name_row.label(text="No File Found", icon="FILE")
        self.draw_editing_buttons(context, file_name_row)

        # main section
        self.draw_editable_file_info(context)

        # file path row and actions section
        row = self.layout.row()
        row.label(text="File Not Saved", icon="ERROR")

    def draw_loaded_project_ui(self, context):
        # file name row
        props = tool.Blender.get_bim_props()
        file_name_row = self.layout.row(align=True)
        file_name_row.label(text=os.path.basename(props.ifc_file), icon="FILE")
        self.draw_editing_buttons(context, file_name_row)

        # main section
        self.draw_editable_file_info(context)

        # file path row and actions section
        row = self.layout.row(align=True)
        if props.is_dirty:
            row.label(text="Saved*", icon="EXPORT")
        else:
            row.label(text="Saved", icon="EXPORT")
        row.label(text=ProjectData.data["last_saved"])

        row = self.layout.row(align=True)
        col = row.column()
        col.enabled = False
        col.prop(props, "ifc_file", text="")
        row.operator("bim.select_ifc_file", icon="FILE_FOLDER", text="")


class BIM_PT_new_project_wizard(Panel):
    bl_label = "New Project Wizard"
    bl_idname = "BIM_PT_new_project_wizard"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"HIDE_HEADER"}
    bl_parent_id = "BIM_PT_tab_new_project_wizard"

    def draw(self, context):
        self.layout.use_property_decorate = False
        self.layout.use_property_split = True

        props = tool.Blender.get_bim_props()
        pprops = tool.Project.get_project_props()
        prop_with_search(self.layout, pprops, "export_schema")
        row = self.layout.row()
        row.prop(context.scene.unit_settings, "system")
        row = self.layout.row()
        row.prop(context.scene.unit_settings, "length_unit")
        row = self.layout.row()
        row.prop(props, "area_unit", text="Area Unit")
        row = self.layout.row()
        row.prop(props, "volume_unit", text="Volume Unit")
        prop_with_search(self.layout, pprops, "template_file", text="Template")

        row = self.layout.row()
        row.operator("bim.create_project")


class BIM_PT_project_library(Panel):
    bl_label = "Project Library"
    bl_idname = "BIM_PT_project_library"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_project_setup"

    def draw(self, context):
        self.layout.use_property_decorate = False
        self.layout.use_property_split = True
        self.props = tool.Project.get_project_props()
        row = self.layout.row(align=True)
        row.prop(self.props, "library_file", text="")
        if self.props.library_file == "0":
            row.operator("bim.select_library_file", icon="FILE_FOLDER", text="")
        row = self.layout.row(align=True)
        if IfcStore.library_file:
            row.label(
                text=os.path.splitext(os.path.basename(IfcStore.library_path))[0]
                + f" - {IfcStore.library_file.schema}",
                icon="ASSET_MANAGER",
            )
            row.operator("bim.append_library_element_by_query", text="", icon="APPEND_BLEND")
            row.operator("bim.save_library_file", text="", icon="EXPORT")
            self.draw_library_ul()
        else:
            row.label(text="No Library Loaded", icon="ASSET_MANAGER")

    def draw_library_ul(self):
        layout = self.layout
        props = self.props

        library_file = IfcStore.library_file
        assert library_file
        library_is_selected = props.selected_project_library != "-"

        row = layout.row(align=True)
        row.prop(self.props, "selected_project_library", text="")

        if library_file.schema != "IFC2X3":
            row.operator("bim.add_project_library", text="", icon="ADD")

        if library_is_selected and not props.is_editing_project_library:
            row.prop(props, "is_editing_project_library", text="", icon="GREASEPENCIL")

        row.prop(self.props, "show_library_tree", text="", icon="OUTLINER")

        if props.is_editing_project_library:
            row = layout.row(align=True)
            row.operator("bim.edit_project_library", text="Save Attributes", icon="GREASEPENCIL")
            row.prop(props, "is_editing_project_library", text="", icon="CANCEL")
            draw_attributes(props.project_library_attributes, layout)
            row = layout.row()
            row.prop(props, "parent_library", text="Parent Library")
            layout.separator()

        if not self.props.library_elements:
            row = self.layout.row()
            row.label(text="No Assets Found", icon="ERROR")
            return

        row = self.layout.row(align=True)
        active_library_element = self.props.get_active_library_breadcrumb()
        row.label(text=(active_library_element.name if active_library_element else "Top Level Assets"))
        if active_library_element:
            row.operator("bim.rewind_library", icon="FRAME_PREV", text="")
        row.operator("bim.refresh_library", icon="FILE_REFRESH", text="")
        self.layout.template_list(
            "BIM_UL_library",
            "",
            self.props,
            "library_elements",
            self.props,
            "active_library_element_index",
        )


class BIM_PT_links(Panel):
    bl_label = "Links"
    bl_idname = "BIM_PT_links"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_project_setup"

    def draw(self, context):
        self.props = tool.Project.get_project_props()
        row = self.layout.row(align=True)
        row.operator("bim.link_ifc")
        if self.props.links:
            self.layout.template_list(
                "BIM_UL_links",
                "",
                self.props,
                "links",
                self.props,
                "active_link_index",
            )

        if LinksData.enable_culling:
            row = self.layout.row(align=True)
            row.label(text="Object Culling Enabled", icon="MOD_TRIANGULATE")

        if not LinksData.linked_data or not self.props.links:
            if self.props.links:
                row = self.layout.row(align=True)
                row.label(text="No Object Queried with Explore Tool", icon="QUESTION")
            return

        row = self.layout.row(align=True)
        row.label(text="")
        row.operator("bim.append_inspected_linked_element", icon="APPEND_BLEND", text="")

        for name, value in LinksData.linked_data["attributes"].items():
            row = self.layout.row(align=True)
            row.label(text=name)
            row.label(text=value)

        for pset in LinksData.linked_data["properties"]:
            box = self.layout.box()
            row = box.row(align=True)
            row.label(text=pset[0], icon="COPY_ID")
            for name, value in pset[1].items():
                row = box.row(align=True)
                row.label(text=name)
                row.label(text=value)

        if LinksData.linked_data["type_properties"]:
            row = self.layout.row()
            row.label(icon="LINKED", text="Type Properties")
            for pset in LinksData.linked_data["type_properties"]:
                box = self.layout.box()
                row = box.row(align=True)
                row.label(text=pset[0], icon="COPY_ID")
                for name, value in pset[1].items():
                    row = box.row(align=True)
                    row.label(text=name)
                    row.label(text=value)


class BIM_UL_library(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMProjectProperties,
        item: LibraryElement,
        icon,
        active_data,
        active_propname,
    ):
        if item:
            row = layout.row(align=True)
            if item.element_type != "ASSET" and (item.asset_count > 0 or item.has_sublibraries):
                op = row.operator("bim.change_library_element", text="", icon="DISCLOSURE_TRI_RIGHT", emboss=False)
                op.element_name = item.name
                op.breadcrumb_type = item.element_type
                op.library_id = item.ifc_definition_id
            if item.ifc_definition_id:
                row.prop(item, "name", text="", emboss=False)
            else:
                row.label(text=item.name)
            if item.ifc_definition_id and item.is_declarable:
                if item.is_declared:
                    op = row.operator("bim.unassign_library_declaration", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.definition = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_library_declaration", text="", icon="KEYFRAME", emboss=False)
                    op.definition = item.ifc_definition_id
            if item.element_type == "ASSET":
                if item.is_appended:
                    row.label(text="", icon="CHECKMARK")
                else:
                    op = row.operator("bim.append_library_element", text="", icon="APPEND_BLEND")
                    op.definition = item.ifc_definition_id
                    op.prop_index = data.get_library_element_index(item)
            else:
                row_ = row.row()
                row_.alignment = "RIGHT"
                row_.label(text=str(item.asset_count))


class BIM_UL_filter_categories(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMProjectProperties,
        item: FilterCategory,
        icon,
        active_data,
        active_propname,
    ):
        if item:
            row = layout.row(align=True)
            row.label(text=f"{item.name} ({item.total_elements})")
            row.prop(
                item,
                "is_selected",
                icon="CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT",
                text="",
                emboss=False,
            )


class BIM_UL_links(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMProjectProperties,
        item: Link,
        icon,
        active_data,
        active_propname,
        index,
    ):
        if item:
            row = layout.row(align=True)
            if item.is_loaded:
                row.label(text=item.name)
                op = row.operator(
                    "bim.toggle_link_selectability",
                    text="",
                    icon="RESTRICT_SELECT_OFF" if item.is_selectable else "RESTRICT_SELECT_ON",
                    emboss=False,
                )
                op.link = item.name
                op = row.operator(
                    "bim.toggle_link_visibility",
                    text="",
                    icon="CUBE" if item.is_wireframe else "MESH_CUBE",
                    emboss=False,
                )
                op.link = item.name
                op.mode = "WIREFRAME"
                op = row.operator(
                    "bim.toggle_link_visibility",
                    text="",
                    icon="HIDE_ON" if item.is_hidden else "HIDE_OFF",
                    emboss=False,
                )
                op.link = item.name
                op.mode = "VISIBLE"
                op = row.operator("bim.select_link_handle", text="", icon="OBJECT_DATA")
                op.index = index
                op = row.operator("bim.unload_link", text="", icon="UNLINKED")
                op.filepath = item.name
                op = row.operator("bim.reload_link", text="", icon="FILE_REFRESH")
                op.filepath = item.name
            else:
                row.prop(item, "name", text="")
                op = row.operator("bim.load_link", text="", icon="LINKED")
                op.filepath = item.name
                op = row.operator("bim.unlink_ifc", text="", icon="X")
                op.filepath = item.name


class BIM_PT_purge(Panel):
    bl_label = "Purge Data"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_quality_control"

    def draw(self, context):
        layout = self.layout
        layout.operator("bim.purge_unused_objects", text="Purge Unused Profiles").object_type = "PROFILE"
        layout.operator("bim.purge_unused_objects", text="Purge Unused Types").object_type = "TYPE"
        layout.operator("bim.purge_unused_openings", text="Purge Unused Openings in Selected Objects")

        MERGEABLE_OBJECT_TYPES = ("MATERIAL", "STYLE", "ORGANIZATION", "APPLICATION")

        for object_type in MERGEABLE_OBJECT_TYPES:
            row = layout.row(align=True)
            row.label(text=f"{object_type.capitalize()}:")
            row.operator("bim.purge_unused_objects", text="Purge Unused").object_type = object_type
            row.operator("bim.merge_identical_objects", text="Merge Identical").object_type = object_type
