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

import bpy
import bonsai.tool as tool
from bonsai.bim.prop import StrProperty, Attribute
from bonsai.bim.module.style.data import StylesData
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)

import gettext
from typing import Literal, Union, TYPE_CHECKING, get_args


_ = gettext.gettext


def get_style_types(self: "BIMStylesProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not StylesData.is_loaded:
        StylesData.load()
    return StylesData.data["style_types"]


def get_reflectance_methods(self: "BIMStylesProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not StylesData.is_loaded:
        StylesData.load()
    return StylesData.data["reflectance_methods"]


def update_style_name(self: "Style", context: bpy.types.Context) -> None:
    style = tool.Ifc.get().by_id(self.ifc_definition_id)
    tool.Style.rename_style(style, self.name)


class Style(PropertyGroup):
    name: StringProperty(name="Name", update=update_style_name)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    total_elements: IntProperty(name="Total Elements")
    style_classes: CollectionProperty(name="Style Classes", type=StrProperty)
    has_surface_colour: BoolProperty(name="Has Surface Colour", default=False)
    surface_colour: bpy.props.FloatVectorProperty(
        name="Surface Colour", subtype="COLOR", default=(1, 1, 1), min=0.0, max=1.0, size=3
    )
    has_diffuse_colour: BoolProperty(name="Has Diffuse Colour", default=False)
    diffuse_colour: bpy.props.FloatVectorProperty(
        name="Diffuse Colour", subtype="COLOR", default=(1, 1, 1), min=0.0, max=1.0, size=3
    )
    blender_material: PointerProperty(
        description=(
            "Needed for UI to have style->blender material link that won't break on undo. "
            "Can be None if it's not a surface style"
        ),
        type=bpy.types.Material,
    )

    if TYPE_CHECKING:
        ifc_definition_id: int
        total_elements: int
        style_classes: bpy.types.bpy_prop_collection_idprop[StrProperty]
        has_surface_colour: bool
        surface_colour: tuple[float, float, float]
        has_diffuse_colour: bool
        diffuse_colour: tuple[float, float, float]
        blender_material: Union[bpy.types.Material, None]


STYLE_TYPES = [
    ("Shading", "Shading", ""),
    ("External", "External", ""),
]


def update_shading_styles(self: "BIMStylesProperties", context: bpy.types.Context) -> None:
    for mat in bpy.data.materials:
        if tool.Blender.get_ifc_definition_id(mat) == 0:
            continue
        tool.Style.change_current_style_type(mat, self.active_style_type)


def update_shader_graph(self: Union["Texture", "BIMStylesProperties"], context: bpy.types.Context) -> None:
    props = self.id_data.BIMStylesProperties if isinstance(self, Texture) else self

    if not props.update_graph:
        return
    style = tool.Ifc.get().by_id(props.is_editing_style)
    material = tool.Ifc.get_object(style)

    shading_data = tool.Style.get_shading_style_data_from_props()
    textures_data = tool.Style.get_texture_style_data_from_props()
    tool.Loader.create_surface_style_rendering(material, shading_data)
    tool.Loader.create_surface_style_with_textures(material, shading_data, textures_data)


UV_MODES = [
    ("UV", "UV", _("Actual UV data presented on the geometry")),
    ("Generated", "Generated", _("Automatically-generated UV from the vertex positions of the mesh")),
    ("Camera", "Camera", _("UV from position coordinate in camera space")),
]

TextureMapMode = Literal[
    "DIFFUSE", "NORMAL", "METALLICROUGHNESS", "SPECULAR", "SHININESS", "EMISSIVE", "OCCLUSION", "AMBIENT"
]
TEXTURE_MAPS_MODS = (
    ("DIFFUSE", "DIFFUSE", ""),
    ("NORMAL", "NORMAL", ""),
    ("METALLICROUGHNESS", "METALLICROUGHNESS", "Green Channel = Roughness,\nBlue Channel = Metallic"),
    ("SPECULAR", "SPECULAR", ""),
    ("SHININESS", "SHININESS", ""),
    ("EMISSIVE", "EMISSIVE", ""),
    ("OCCLUSION", "OCCLUSION", ""),
    ("AMBIENT", "AMBIENT", ""),
)


class Texture(PropertyGroup):
    mode: EnumProperty(name="Type Of Texture", items=TEXTURE_MAPS_MODS, update=update_shader_graph)
    # NOTE: subtype `FILE_PATH` is not used to avoid .blend relative paths
    path: StringProperty(name="Texture Path", update=update_shader_graph)

    if TYPE_CHECKING:
        mode: TextureMapMode
        path: str


class ColourRgb(PropertyGroup):
    name: StringProperty()
    color_value: FloatVectorProperty(size=3, subtype="COLOR", default=(1, 1, 1))
    # not exposed in the UI, here just to preserve the data
    color_name: StringProperty(name="Color Name")

    if TYPE_CHECKING:
        name: str
        color_value: tuple[float, float, float]
        color_name: str

    # to fit blender.bim.helper.export_attributes
    def get_value(self):
        return {
            "Name": self.color_name or None,
            "Red": self.color_value[0],
            "Green": self.color_value[1],
            "Blue": self.color_value[2],
        }

    # to fit blender.bim.helper.draw_attribute
    is_uri = False
    is_optional = False
    special_type = ""

    def get_value_name(self, *args, **kwargs):
        return "color_value"


SurfaceStyleClass = Literal[
    "IfcSurfaceStyleShading",
    "IfcSurfaceStyleRendering",
    "IfcSurfaceStyleWithTextures",
    "IfcSurfaceStyleLighting",
    "IfcSurfaceStyleRefraction",
    "IfcExternallyDefinedSurfaceStyle",
]
ColourClass = Literal["IfcColourRgb", "IfcNormalisedRatioMeasure"]


class BIMStylesProperties(PropertyGroup):
    is_adding: BoolProperty(name="Is Adding", description="Is adding new IfcPresentationStyle")
    is_editing: BoolProperty(name="Is Editing", description="Is editing IfcPresentationStyle")
    is_editing_style: IntProperty(name="Is Editing Style", description="Is editing new presentation item surface style")
    is_editing_class: StringProperty(
        name="Is Editing Class",
        description="Presentation item surface style class currently edited",
    )
    is_editing_existing_style: BoolProperty(name="Is Editing Existing", description="Is editing existing surface style")
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    external_style_attributes: CollectionProperty(name="External Style Attributes", type=Attribute)
    refraction_style_attributes: CollectionProperty(name="Refraction Style Attributes", type=Attribute)
    lighting_style_colours: CollectionProperty(name="Lighting Style Colours", type=ColourRgb)
    style_type: EnumProperty(items=get_style_types, default=2, name="Style Type")
    style_name: StringProperty(name="Style Name")
    surface_style_class: EnumProperty(
        items=[(x, x, "") for x in get_args(SurfaceStyleClass)],
        name="Surface Style Class",
        default="IfcSurfaceStyleShading",
    )
    update_graph: BoolProperty(
        name="Update Shade Graph on Prop Change",
        description="Update shader graph in real time\nas you update style properties",
        default=True,
    )

    # shading props
    surface_colour: bpy.props.FloatVectorProperty(
        name="Surface Colour", subtype="COLOR", default=(1, 1, 1), min=0.0, max=1.0, size=3, update=update_shader_graph
    )
    transparency: bpy.props.FloatProperty(
        name="Transparency", default=0.0, min=0.0, max=1.0, update=update_shader_graph
    )
    # TODO: do something on null?
    is_diffuse_colour_null: BoolProperty(name="Is Null")
    diffuse_colour_class: EnumProperty(
        items=[(x, x, "") for x in get_args(ColourClass)],
        name="Diffuse Colour Class",
        update=update_shader_graph,
    )
    diffuse_colour: bpy.props.FloatVectorProperty(
        name="Diffuse Colour", subtype="COLOR", default=(1, 1, 1), min=0.0, max=1.0, size=3, update=update_shader_graph
    )
    diffuse_colour_ratio: bpy.props.FloatProperty(
        name="Diffuse Ratio", default=0.0, min=0.0, max=1.0, update=update_shader_graph
    )
    is_specular_colour_null: BoolProperty(name="Is Null")
    specular_colour_class: EnumProperty(
        items=[(x, x, "") for x in get_args(ColourClass)],
        name="Specular Colour Class",
        update=update_shader_graph,
        default="IfcNormalisedRatioMeasure",
    )
    specular_colour: bpy.props.FloatVectorProperty(
        name="Specular Colour",
        subtype="COLOR",
        default=(1, 1, 1),
        min=0.0,
        max=1.0,
        size=3,
        update=update_shader_graph,
    )
    specular_colour_ratio: bpy.props.FloatProperty(
        name="Specular Ratio",
        description="Used as Metallic value in PHYSICAL Reflectance Method",
        default=0.0,
        min=0.0,
        max=1.0,
        update=update_shader_graph,
    )
    is_specular_highlight_null: BoolProperty(name="Is Null")
    specular_highlight: bpy.props.FloatProperty(
        name="Specular Highlight",
        description="Used as Roughness value in PHYSICAL Reflectance Method",
        default=0.0,
        min=0.0,
        max=1.0,
        update=update_shader_graph,
    )
    reflectance_method: EnumProperty(
        name="Reflectance Method",
        items=get_reflectance_methods,
        update=update_shader_graph,
    )

    # textures props
    textures: CollectionProperty(name="Textures", type=Texture)
    uv_mode: EnumProperty(
        name="UV Mode",
        description="Type of UV used for the textures",
        items=UV_MODES,
        default="UV",
        update=update_shader_graph,
    )

    styles: CollectionProperty(name="Styles", type=Style)
    active_style_index: IntProperty(name="Active Style Index")

    @property
    def active_style(self) -> Union[Style, None]:
        return tool.Blender.get_active_uilist_element(self.styles, self.active_style_index)

    active_style_type: EnumProperty(
        name="Active Style Type",
        description="Update current blender material to match style type for all objects in the scene",
        items=[(i, i, "") for i in get_args(tool.Style.StyleType)],
        default="Shading",
        update=update_shading_styles,
    )

    if TYPE_CHECKING:
        is_adding: bool
        is_editing: bool
        is_editing_style: int
        is_editing_class: str
        is_editing_existing_style: bool
        attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        external_style_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        refraction_style_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        lighting_style_colours: bpy.types.bpy_prop_collection_idprop[ColourRgb]
        style_type: str
        style_name: str
        surface_style_class: SurfaceStyleClass
        update_graph: bool

        # Shading props.
        surface_colour: tuple[float, float, float]
        transparency: float
        is_diffuse_colour_null: bool
        diffuse_colour_class: ColourClass
        diffuse_colour: tuple[float, float, float]
        diffuse_colour_ratio: float
        is_specular_colour_null: bool
        specular_colour_class: ColourClass
        specular_colour: tuple[float, float, float]
        specular_colour_ratio: float
        is_specular_highlight_null: bool
        specular_highlight: float
        reflectance_method: str

        # Texture props.
        textures: bpy.types.bpy_prop_collection_idprop[Texture]
        uv_mode: Literal["UV", "Generated", "Camera"]

        styles: bpy.types.bpy_prop_collection_idprop[Style]
        active_style_index: int
        active_style_type: tool.Style.StyleType


def update_shading_style(self: "BIMStyleProperties", context: bpy.types.Context) -> None:
    blender_material = self.id_data
    style_elements = tool.Style.get_style_elements(blender_material)
    if self.active_style_type == "External":
        if tool.Style.has_blender_external_style(style_elements):
            tool.Style.switch_shading(blender_material, self.active_style_type)
    elif self.active_style_type == "Shading":
        tool.Style.switch_shading(blender_material, self.active_style_type)


class BIMStyleProperties(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    active_style_type: EnumProperty(
        name="Active Style Type",
        description="Update current blender material to match style type",
        items=[(i, i, "") for i in get_args(tool.Style.StyleType)],
        default="Shading",
        update=update_shading_style,
    )
    is_renaming: BoolProperty(description="Used to prevent triggering handler callback.", default=False)

    if TYPE_CHECKING:
        ifc_definition_id: int
        active_style_type: tool.Style.StyleType
        is_renaming: bool
