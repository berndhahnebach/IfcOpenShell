# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import pytest
import traceback
import webbrowser
import numpy as np
import test.bim.stub
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.representation
import bonsai.tool as tool
import bonsai.bim.handler
from bonsai.bim.ifc import IfcStore
from bonsai.tool.brick import BrickStore
from bonsai.bim.module.model.data import AuthoringData
from pytest_bdd import scenarios, given, when, then, parsers
from inspect import signature
from mathutils import Vector
from math import radians
from pathlib import Path
from typing import Union, Any

scenarios("feature")

variables = {
    "cwd": Path.cwd().as_posix(),
    "ifc_dir": os.path.join(Path.cwd().as_posix(), "test", "files", "temp"),
    "ifc": "tool.Ifc.get()",
    "pset_ifc": "IfcStore.pset_template_file",
    "classification_ifc": "IfcStore.classification_file",
}

# Monkey-patch webbrowser opening since we want to test headlessly
webbrowser.open = lambda x: True


tool.Bsdd.client = test.bim.stub.bSDDClientStub()


class PanelSpy:
    def __init__(self, panel: type[bpy.types.Panel]):
        self.is_spy_dirty = True
        self.panel = panel

    def refresh_spy(self):
        if self.is_spy_dirty:
            self.is_spy_dirty = False
            self.spied_attr: Union[str, None] = None
            self.spied_labels: list[str] = []
            self.spied_props: list[dict[str, Any]] = []
            self.spied_operators: list[dict[str, Any]] = []
            self.spied_lists: list[dict[str, Any]] = []
            self.panel.draw(self, bpy.context)

    def __getattr__(self, attr):
        self.spied_attr = attr
        if annotation := self.panel.__annotations__.get(attr, None):
            return annotation.keywords.get("default", None)  # An operator property
        if attr == "layout":
            return self
        if hasattr(self.panel, attr) and not callable(getattr(self.panel, attr)):
            return getattr(self.panel, attr)
        return self

    def __call__(self, *args, **kwargs):
        if self.spied_attr in ("row", "column", "box", "separator", "menu", "operator_menu_enum", "split"):
            return self
        elif self.spied_attr == "template_list":
            listtype_name, list_id, dataptr, propname, active_dataptr, active_propname = args
            spied_data = {
                "listtype_name": listtype_name,
                "list_id": list_id,
                "dataptr": dataptr,
                "propname": propname,
                "active_dataptr": active_dataptr,
                "active_propname": active_propname,
            }
            template_list = TemplateListSpy(getattr(bpy.types, listtype_name), spied_data)
            self.spied_lists.append(template_list)
            return template_list
        elif self.spied_attr == "context_pointer_set":
            return lambda *args, **kwargs: None
        elif self.spied_attr == "label":
            self.spied_labels.append(kwargs["text"])
            return self
        elif self.spied_attr == "prop":
            props, name = args
            props: bpy.types.bpy_struct
            text = kwargs.get("text", props.bl_rna.properties[name].name)
            icon = kwargs.get("icon", None)
            prop_type = props.bl_rna.properties[name].type
            enum_items = []
            if prop_type == "ENUM":
                prop_keywords = props.__annotations__[name].keywords
                items = prop_keywords.get("items")
                if items is not None:
                    if isinstance(items, (list, tuple)):
                        enum_items = items
                    else:
                        # items are retrieved through a callback, not a static list / tuple :
                        enum_items = items(props, bpy.context)
            value = getattr(props, name)
            if text:
                self.spied_labels.append(text)
            spied_prop = {
                "props": props,
                "name": name,
                "text": text,
                "icon": icon,
                "value": value,
                "prop_type": prop_type,
                "enum_items": enum_items,
            }
            self.spied_props.append(spied_prop)
        elif self.spied_attr == "operator":
            operator = args[0]
            prefix, op_name = operator.split(".")
            operator = getattr(getattr(bpy.ops, prefix), op_name)
            bl_idname = operator.idname()
            try:
                bl_label = getattr(bpy.types, bl_idname).bl_label
            except:  # Doesn't work on built-ins, I don't know what to do
                bl_label = bl_idname
            text = kwargs.get("text", bl_label)
            icon = kwargs.get("icon", None)
            if text:
                self.spied_labels.append(text)
            after = ""
            if self.spied_labels:
                after = self.spied_labels[-1]
            spied_operator = {"operator": operator, "icon": icon, "text": text, "kwargs": {}, "after": after}
            self.spied_operators.append(spied_operator)
            return OperatorSpy(spied_operator)
        else:
            getattr(self.panel, self.spied_attr)(self, *args, **kwargs)


class OperatorSpy:
    def __init__(self, spied_data):
        self.spied_data = spied_data

    def __setattr__(self, name, value):
        if name == "spied_data":
            # Allow direct setting of spied_data only during initialization
            super().__setattr__(name, value)
        else:
            self.spied_data["kwargs"][name] = value


class TemplateListSpy(PanelSpy):
    def __init__(self, template_list: type[bpy.types.UIList], spied_data: dict) -> None:
        self.spied_data = spied_data
        self.items = getattr(self.spied_data["dataptr"], self.spied_data["propname"])
        self.active_index = getattr(self.spied_data["active_dataptr"], self.spied_data["active_propname"])
        try:
            self.active_item = self.items[self.active_index]
        except:
            self.active_item = None
        self.panel = template_list

        self.rows = []
        for item in self.items:
            self.rows.append(TemplateListItemSpy(self, item))

    def set_active_index(self, index: int) -> None:
        self.active_index = index
        setattr(self.spied_data["active_dataptr"], self.spied_data["active_propname"], self.active_index)
        try:
            self.active_item = self.items[self.active_index]
        except:
            assert False, f"Could not set active index {index}"


class TemplateListItemSpy(PanelSpy):
    def __init__(self, parent: TemplateListSpy, item):
        self.panel = parent.panel
        self.spied_attr: Union[str, None] = None
        self.spied_labels: list[str] = []
        self.spied_props: list[dict[str, Any]] = []
        self.spied_operators: list[dict[str, Any]] = []
        if len(signature(parent.panel.draw_item).parameters) == 8:
            parent.panel.draw_item(
                self,
                bpy.context,
                self,
                parent.spied_data["dataptr"],
                item,
                "",
                parent.spied_data["active_dataptr"],
                parent.spied_data["active_propname"],
            )
        else:
            parent.panel.draw_item(
                self,
                bpy.context,
                self,
                parent.spied_data["dataptr"],
                item,
                "",
                parent.spied_data["active_dataptr"],
                parent.spied_data["active_propname"],
                0,  # Index?
                None,
            )


ui_name_cache = {}
panel_spy: Union[PanelSpy, None] = None


def create_ui_name_cache():
    global ui_name_cache
    if ui_name_cache:
        return
    for bl_idname in dir(bpy.types):
        try:
            panel_type = getattr(bpy.types, bl_idname)
            if panel_type.bl_rna.base.name == "Panel":
                ui_name_cache[panel_type.bl_label] = panel_type.bl_idname
            elif panel_type.bl_rna.base.name == "Operator":
                ui_name_cache[panel_type.bl_label] = bl_idname
            elif panel_type.bl_rna.base.name == "Menu":
                if panel_type.bl_label == "Add" and bl_idname != "VIEW3D_MT_add":
                    continue  # Non-unique, but "VIEW3D_MT_add" is the one we care about
                ui_name_cache[panel_type.bl_label] = bl_idname
            elif panel_type.bl_rna.base.name == "UIList":
                ui_name_cache[panel_type.bl_rna.name] = bl_idname
        except:
            pass


def replace_variables(value):
    for key, new_value in variables.items():
        value = value.replace("{" + key + "}", str(new_value))
    return value


def is_x(number, x):
    return abs(number - x) < 1e-5


def vectors_are_equal(v1, v2):
    assert len(v1) == len(v2), f"Compared vectors are not equal length: {v1}, {v2}"
    return all(is_x(v1[i], v2[i]) for i in range(len(v1)))


@given("an untestable scenario")
def an_untestable_scenario():
    pass


@given("an empty Blender session")
@when("an empty Blender session is started")
def an_empty_blender_session():
    IfcStore.purge()
    bpy.ops.wm.read_homefile(app_template="")
    if len(bpy.data.objects) > 0:
        bpy.data.batch_remove(bpy.data.objects)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    if len(bpy.data.materials) > 0:
        bpy.data.batch_remove(bpy.data.materials)

    # default project settings
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
    props = tool.Project.get_project_props()
    props.template_file = "0"
    tool.Blender.get_addon_preferences().should_play_chaching_sound = False


@given("an empty IFC project")
def an_empty_ifc_project():
    an_empty_blender_session()
    bpy.ops.bim.create_project()


@given("an empty IFC2X3 project")
def an_empty_ifc_2x3_project():
    an_empty_blender_session()
    props = tool.Project.get_project_props()
    props.export_schema = "IFC2X3"
    bpy.ops.bim.create_project()


@given("the Brickschema is stubbed")
def the_brickschema_is_stubbed():
    # This makes things run faster since we don't need to load the entire brick schema
    cwd = os.path.dirname(os.path.realpath(__file__))
    BrickStore.schema = os.path.join(cwd, "..", "files", "BrickStub.ttl")


@given(parsers.parse('I look at the "{panel}" panel'))
@when(parsers.parse('I look at the "{panel}" panel'))
@then(parsers.parse('I look at the "{panel}" panel'))
def i_look_at_the_panel_panel(panel):
    global ui_name_cache
    global panel_spy
    create_ui_name_cache()
    if panel not in ui_name_cache:
        assert False, f"Panel {panel} not found in {ui_name_cache}"
    panel_spy = PanelSpy(getattr(bpy.types, ui_name_cache[panel]))
    panel_spy.refresh_spy()


@given(parsers.parse('I open the "{name}" menu'))
@when(parsers.parse('I open the "{name}" menu'))
@then(parsers.parse('I open the "{name}" menu'))
def i_open_the_name_menu(name):
    global ui_name_cache
    global panel_spy
    create_ui_name_cache()
    if name not in ui_name_cache:
        assert False, f"Menu {name} not found in {ui_name_cache}"
    panel_spy = PanelSpy(getattr(bpy.types, ui_name_cache[name]))
    panel_spy.refresh_spy()


@given(parsers.parse('I trigger "{operator}"'))
@when(parsers.parse('I trigger "{operator}"'))
@then(parsers.parse('I trigger "{operator}"'))
def i_trigger_operator(operator):
    global ui_name_cache
    global panel_spy
    create_ui_name_cache()
    if operator not in ui_name_cache:
        assert False, f"Operator {operator} not found in {ui_name_cache}"
    panel_spy = PanelSpy(getattr(bpy.types, ui_name_cache[operator]))
    panel_spy.refresh_spy()


@given(parsers.parse('I see "{text}"'))
@when(parsers.parse('I see "{text}"'))
@then(parsers.parse('I see "{text}"'))
def i_see_text(text):
    assert panel_spy
    panel_spy.refresh_spy()
    assert [l for l in panel_spy.spied_labels if text in l], f"Text {text} not found in {panel_spy.spied_labels}"


@given(parsers.parse('there are "{n}" lists'))
@when(parsers.parse('there are "{n}" lists'))
@then(parsers.parse('there are "{n}" lists'))
def there_are_n_lists(n):
    assert panel_spy
    panel_spy.refresh_spy()
    if len(panel_spy.spied_lists) != int(n):
        assert False, f"Actual number of lists {len(panel_spy.spied_lists)} not {n}"


@given(parsers.parse('I see "{text}" in the "{nth}" list'))
@when(parsers.parse('I see "{text}" in the "{nth}" list'))
@then(parsers.parse('I see "{text}" in the "{nth}" list'))
def i_see_text_in_the_nth_list(text, nth):
    assert panel_spy
    panel_spy.refresh_spy()
    nth = int("".join([c for c in nth if c.isnumeric()]))
    if len(panel_spy.spied_lists) < nth:
        assert False, f"{nth} list does not exist. Actual number of lists: {len(panel_spy.spied_lists)}"
    debug = []
    for i, template_list in enumerate(panel_spy.spied_lists):
        if i + 1 != nth:
            continue
        for row in template_list.rows:
            for p in row.spied_props:
                debug.append(str(p))
                if isinstance(p["value"], str) and text in p["value"]:
                    return True
            for l in row.spied_labels:
                debug.append(l)
                if text in l:
                    return True
    debug = "\n".join(debug)
    assert False, f"Could not see '{text}' in any list. We saw:\n{debug}"


@given(parsers.parse('I don\'t see "{text}" in the "{nth}" list'))
@when(parsers.parse('I don\'t see "{text}" in the "{nth}" list'))
@then(parsers.parse('I don\'t see "{text}" in the "{nth}" list'))
def i_dont_see_text_in_the_nth_list(text, nth):
    assert panel_spy
    panel_spy.refresh_spy()
    nth = int("".join([c for c in nth if c.isnumeric()]))
    if len(panel_spy.spied_lists) < nth:
        assert False, f"{nth} list does not exist. Actual number of lists: {len(panel_spy.spied_lists)}"
    debug = []
    for i, template_list in enumerate(panel_spy.spied_lists):
        if i + 1 != nth:
            continue
        for row in template_list.rows:
            for l in row.spied_labels:
                debug.append(l)
                if text in l:
                    debug = "\n".join(debug)
                    assert False, f"We see saw '{text}' in the {nth} list but should not have. We saw:\n{debug}"


@given(parsers.parse('I click "{button}" in the row where I see "{text}" in the "{nth}" list'))
@when(parsers.parse('I click "{button}" in the row where I see "{text}" in the "{nth}" list'))
@then(parsers.parse('I click "{button}" in the row where I see "{text}" in the "{nth}" list'))
def i_click_button_in_the_row_where_i_see_text_in_the_nth_list(button, text, nth):
    """
    :param button: The text or icon of the button to click.
    """
    assert panel_spy
    panel_spy.refresh_spy()
    nth = int("".join([c for c in nth if c.isnumeric()]))
    if len(panel_spy.spied_lists) < nth:
        assert False, f"{nth} list does not exist. Actual number of lists: {len(panel_spy.spied_lists)}"
    debug = []
    for i, template_list in enumerate(panel_spy.spied_lists):
        if i + 1 != nth:
            continue
        for row in template_list.rows:
            is_row = False
            for l in row.spied_labels:
                debug.append(l)
                if text in l:
                    is_row = True
            for p in row.spied_props:
                debug.append(str(p))
                if isinstance(p["value"], str) and text in p["value"]:
                    is_row = True
            if is_row:
                _i_click_button_on_panel(button, row)
                return True
    debug = "\n".join(debug)
    assert False, f"Could not see '{text}' in any list. We saw:\n{debug}"


@given(parsers.parse('I select the row where I see "{text}" in the "{nth}" list'))
@when(parsers.parse('I select the row where I see "{text}" in the "{nth}" list'))
@then(parsers.parse('I select the row where I see "{text}" in the "{nth}" list'))
def i_select_the_row_where_i_see_text_in_the_nth_list(text, nth):
    assert panel_spy
    panel_spy.refresh_spy()
    nth = int("".join([c for c in nth if c.isnumeric()]))
    if len(panel_spy.spied_lists) < nth:
        assert False, f"{nth} list does not exist. Actual number of lists: {len(panel_spy.spied_lists)}"
    debug = []
    for i, template_list in enumerate(panel_spy.spied_lists):
        if i + 1 != nth:
            continue
        for i, row in enumerate(template_list.rows):
            is_row = False
            for p in row.spied_props:
                debug.append(str(p))
                if isinstance(p["value"], str) and text in p["value"]:
                    is_row = True
            for l in row.spied_labels:
                debug.append(l)
                if text in l:
                    is_row = True
            if is_row:
                template_list.set_active_index(i)
                panel_spy.is_spy_dirty = True
                return True
    debug = "\n".join(debug)
    assert False, f"Could not see '{text}' in any list. We saw:\n{debug}"


@given(parsers.parse('I don\'t see "{text}"'))
@when(parsers.parse('I don\'t see "{text}"'))
@then(parsers.parse('I don\'t see "{text}"'))
def i_dont_see_text(text):
    assert panel_spy
    panel_spy.refresh_spy()
    assert not [l for l in panel_spy.spied_labels if text in l], f"Text {text} found in {panel_spy.spied_labels}"


@given(parsers.parse('I don\'t see the "{name}" list'))
@when(parsers.parse('I don\'t see the "{name}" list'))
@then(parsers.parse('I don\'t see the "{name}" list'))
def i_dont_see_the_name_list(name):
    assert panel_spy
    panel_spy.refresh_spy()
    assert name not in [l.spied_data["listtype_name"] for l in panel_spy.spied_lists]


@given(parsers.parse('I see the "{prop}" property'))
@when(parsers.parse('I see the "{prop}" property'))
@then(parsers.parse('I see the "{prop}" property'))
def i_see_the_prop_property(prop):
    assert panel_spy
    panel_spy.refresh_spy()
    assert [
        p for p in panel_spy.spied_props if prop in (p["name"], p["text"], p["icon"])
    ], f"Property {prop} not found in {panel_spy.spied_props}"


@given(parsers.parse('I don\'t see the "{prop}" property'))
@when(parsers.parse('I don\'t see the "{prop}" property'))
@then(parsers.parse('I don\'t see the "{prop}" property'))
def i_dont_see_the_prop_property(prop):
    assert panel_spy
    panel_spy.refresh_spy()
    assert not [
        p for p in panel_spy.spied_props if prop in (p["name"], p["text"], p["icon"])
    ], f"Property {prop} not found in {panel_spy.spied_props}"


@given(parsers.parse('I see the "{prop}" property is "{value}"'))
@when(parsers.parse('I see the "{prop}" property is "{value}"'))
@then(parsers.parse('I see the "{prop}" property is "{value}"'))
def i_see_the_prop_property_is_value(prop, value):
    assert panel_spy
    panel_spy.refresh_spy()
    for spied_prop in panel_spy.spied_props:
        if prop in (spied_prop["name"], spied_prop["text"], spied_prop["icon"]):
            assert (
                spied_prop["value"] == value
            ), f"Property {prop} value is not {value} - it is actually {spied_prop['value']}"
            return
    assert False, f"Property {prop} not found in {panel_spy.spied_props}"


@given(parsers.parse('I set the "{prop}" property to "{value}"'))
@when(parsers.parse('I set the "{prop}" property to "{value}"'))
@then(parsers.parse('I set the "{prop}" property to "{value}"'))
def i_set_the_prop_property_to_value(prop: str, value: str):
    """
    :param prop: Could be either property name, property text, property icon
        or property index (e.g. "1st", "2nd", "5th").
    """
    value = value.strip()
    assert panel_spy
    panel_spy.refresh_spy()
    is_nth = False
    if prop[0].isnumeric() and (prop.endswith("st") or prop.endswith("nd") or prop.endswith("th")):
        is_nth = True
    for nth, spied_prop in enumerate(panel_spy.spied_props):
        if is_nth and nth != int(prop[:-2]) - 1:
            continue
        if not is_nth and prop not in (spied_prop["name"], spied_prop["text"], spied_prop["icon"]):
            continue
        if spied_prop["prop_type"] == "BOOLEAN":
            if value == "TRUE":
                setattr(spied_prop["props"], spied_prop["name"], True)
            elif value == "FALSE":
                setattr(spied_prop["props"], spied_prop["name"], False)
        elif spied_prop["prop_type"] == "FLOAT":
            setattr(spied_prop["props"], spied_prop["name"], float(value))
        elif spied_prop["prop_type"] == "INT":
            setattr(spied_prop["props"], spied_prop["name"], int(value))
        elif spied_prop["prop_type"] == "ENUM":
            enum_identifier = [i for i in spied_prop["enum_items"] if i is not None and i[1] == value]
            if not enum_identifier:
                assert False, f"Could not find value {value} in enum {spied_prop['enum_items']}"
            setattr(spied_prop["props"], spied_prop["name"], enum_identifier[0][0])
        elif spied_prop["prop_type"] == "POINTER":
            setattr(spied_prop["props"], spied_prop["name"], bpy.data.objects.get(value))
        else:
            setattr(spied_prop["props"], spied_prop["name"], value)
        panel_spy.is_spy_dirty = True
        return
    debug = "\n".join([f"{i} {v}" for i, v in enumerate(panel_spy.spied_props)])
    assert False, f"Property {prop} not found in:\n{debug}"


@then(parsers.parse('The "{name}" list has {total} items'))
def the_name_list_has_total_items(name, total):
    total = int(total)
    assert panel_spy
    panel_spy.refresh_spy()
    for template_list in panel_spy.spied_lists:
        if name == template_list.spied_data["listtype_name"]:
            actual_total = len(template_list.items)
            assert actual_total == total, f"The actual number of items in {name} is {actual_total} not {total}"
            return
    assert False, f"List {name} not found in {panel_spy.spied_lists}"


@given(parsers.parse('I select the "{item_name}" item in the "{list_name}" list'))
@when(parsers.parse('I select the "{item_name}" item in the "{list_name}" list'))
@then(parsers.parse('I can select the "{item_name}" item in the "{list_name}" list'))
def i_select_the_item_name_item_in_the_list_name_list(item_name, list_name):
    assert panel_spy
    panel_spy.refresh_spy()
    for template_list in panel_spy.spied_lists:
        if list_name == template_list.spied_data["listtype_name"]:
            item_names = []
            for i, item in enumerate(template_list.items):
                item_names.append(item.name)
                if item.name == item_name:
                    template_list.set_active_index(i)
                    panel_spy.is_spy_dirty = True
                    return
            assert False, f"Could not find item {item_name} in {item_names}"
    assert False, f"List {list_name} not found in {panel_spy.spied_lists}"


@when("I load a new pset template file")
def i_load_a_new_pset_template_file():
    props = tool.PsetTemplate.get_pset_template_props()
    IfcStore.pset_template_path = props.pset_template_files
    IfcStore.pset_template_file = ifcopenshell.open(IfcStore.pset_template_path)


@given("I create default MEP types")
def i_create_default_mep_types():
    model_props = tool.Model.get_model_props()

    # add couple segments types
    i_trigger_operator("Add Element")
    i_set_the_prop_property_to_value("Name", "RECT1")
    i_set_the_prop_property_to_value("Class", "IfcDuctSegmentType")
    i_set_the_prop_property_to_value("Representation", "Rectangular Distribution Segment")
    i_click_button("OK")

    i_trigger_operator("Add Element")
    i_set_the_prop_property_to_value("Name", "CIRCLE1")
    i_set_the_prop_property_to_value("Class", "IfcDuctSegmentType")
    i_set_the_prop_property_to_value("Representation", "Circular Distribution Segment")
    i_click_button("OK")

    # add an actuator type
    i_trigger_operator("Add Element")
    i_set_the_prop_property_to_value("Name", "ACTUATOR")
    i_set_the_prop_property_to_value("Class", "IfcActuatorType")
    i_set_the_prop_property_to_value("Representation", "Custom Tessellation")
    i_click_button("OK")

    with bpy.context.temp_override(active_object=bpy.data.objects["IfcActuatorType/ACTUATOR"]):
        bpy.ops.bim.add_port()
        # port at cube's left side
        bpy.data.objects["IfcDistributionPort/Port"].location = (-0.5, 0, 0)
        bpy.ops.bim.hide_ports()


@given("I add a cube")
@when("I add a cube")
def i_add_a_cube():
    bpy.ops.mesh.primitive_cube_add()


@given("I add an empty")
@when("I add an empty")
def i_add_an_empty():
    bpy.ops.object.empty_add()


@given("I add a sun")
@when("I add a sun")
def i_add_a_sun():
    bpy.ops.object.light_add(type="SUN")


@given("I add a material")
@when("I add a material")
def i_add_a_material():
    bpy.context.active_object.active_material = bpy.data.materials.new("Material")


@given(parsers.parse('I add a new item to "{collection}"'))
@when(parsers.parse('I add a new item to "{collection}"'))
def i_add_a_new_collection_item(collection):
    try:
        eval(f"bpy.context.{collection}.add()")
    except:
        assert False, "Collection does not exist"


@given(parsers.parse('I make the collection "{name}" visible'))
@when(parsers.parse('I make the collection "{name}" visible'))
def i_make_the_collection_name_visible(name):
    tool.Blender.get_layer_collection(bpy.data.collections.get(name)).hide_viewport = False


@given(parsers.parse('the material "{name}" colour is set to "{colour}"'))
@when(parsers.parse('the material "{name}" colour is set to "{colour}"'))
def the_material_name_colour_is_set_to_colour(name, colour):
    obj = the_material_name_exists(name)
    obj.diffuse_color = [float(c) for c in colour.split(",")]


@given("I add an array modifier")
def i_add_an_array_modifier():
    bpy.ops.object.modifier_add(type="ARRAY")


@given(parsers.parse('I add a cube of size "{size}" at "{location}"'))
@when(parsers.parse('I add a cube of size "{size}" at "{location}"'))
def i_add_a_cube_of_size_size_at_location(size, location):
    bpy.ops.mesh.primitive_cube_add(size=float(size), location=[float(co) for co in location.split(",")])


@given(parsers.parse('I add a plane of size "{size}" at "{location}"'))
@when(parsers.parse('I add a plane of size "{size}" at "{location}"'))
def i_add_a_plane_of_size_size_at_location(size, location):
    bpy.ops.mesh.primitive_plane_add(size=float(size), location=[float(co) for co in location.split(",")])


@then(parsers.parse('I expect an error "{error_msg}" when "{function}"'))
def i_expect_an_error_msg_when_function(error_msg, function):
    try:
        exec(function)
    except Exception as e:
        actual_error_msg = str(e).strip()
        if str(e).strip() != error_msg:
            traceback.print_exc()
            msg = f"Got different exception running {function} - '{actual_error_msg}' instead of '{error_msg}'"
            assert False, msg
        return
    assert False, f"Function {function} ran without exception '{error_msg}'"


@then(parsers.parse('I press "{operator}" and expect error "{error_msg}"'))
def i_press_operator_and_expect_error(operator, error_msg):
    operator = replace_variables(operator)
    try:
        if "(" in operator:
            exec(f"bpy.ops.{operator}")
        else:
            exec(f"bpy.ops.{operator}()")
    except Exception as e:
        actual_error_msg = str(e).strip()
        if str(e).strip() != error_msg:
            traceback.print_exc()
            msg = f"Got different exception running bpy.ops.{operator} - '{actual_error_msg}' instead of '{error_msg}'"
            assert False, msg
        return
    assert False, f"Operator bpy.ops.{operator} ran without exception '{error_msg}'"


@given(parsers.parse('I press "{operator}"'))
@when(parsers.parse('I press "{operator}"'))
def i_press_operator(operator):
    operator = replace_variables(operator)
    try:
        if "(" in operator:
            exec(f"bpy.ops.{operator}")
        else:
            exec(f"bpy.ops.{operator}()")
    except Exception as e:
        traceback.print_exc()
        assert False, f"Failed to run operator bpy.ops.{operator} because of {e}"


def _i_click_button_on_panel(button, panel_spy):
    for spied_operator in panel_spy.spied_operators:
        if spied_operator["text"] == button or spied_operator["icon"] == button:
            spied_operator["operator"]("INVOKE_DEFAULT", **spied_operator["kwargs"])
            panel_spy.is_spy_dirty = True
            return
    # Users can also "click" on booleans to toggle them
    for spied_prop in panel_spy.spied_props:
        if button in (spied_prop["name"], spied_prop["text"], spied_prop["icon"]):
            val = getattr(spied_prop["props"], spied_prop["name"])
            setattr(spied_prop["props"], spied_prop["name"], not bool(val))
            panel_spy.is_spy_dirty = True
            return
    if button == "OK" and panel_spy.panel.bl_rna.base.name == "Operator":
        # Clicked confirm on an operator's draw dialog
        return i_press_operator(panel_spy.panel.bl_idname)
    debug = "\n".join([f"{i} {v}" for i, v in enumerate(panel_spy.spied_operators)])
    debug += f"\nHere is the text we see:\n{panel_spy.spied_labels}\n... and props:\n {panel_spy.spied_props}"
    assert False, f"Could not find {button}:\n{debug}"


@given(parsers.parse('I click "{button}"'))
@when(parsers.parse('I click "{button}"'))
@then(parsers.parse('I click "{button}"'))
def i_click_button(button):
    """
    :param button: The text or icon of the button to click.
    """
    assert panel_spy
    panel_spy.refresh_spy()
    _i_click_button_on_panel(button, panel_spy)


@given(parsers.parse('I click the "{button}" after the text "{text}"'))
@when(parsers.parse('I click the "{button}" after the text "{text}"'))
@then(parsers.parse('I click the "{button}" after the text "{text}"'))
def i_click_the_button_after_the_text_text(button, text):
    assert panel_spy
    panel_spy.refresh_spy()
    for spied_operator in panel_spy.spied_operators:
        if spied_operator["after"] == text:
            if spied_operator["text"] == button or spied_operator["icon"] == button:
                spied_operator["operator"]("INVOKE_DEFAULT", **spied_operator["kwargs"])
                panel_spy.is_spy_dirty = True
                return
    debug = "\n".join([f"{i} {v}" for i, v in enumerate(panel_spy.spied_operators)])
    debug += f"\nHere is the text we see: {panel_spy.spied_labels}"
    assert False, f"Could not find {button}:\n{debug}"


@given(parsers.parse('I click "{button}" and expect error "{error_msg}"'))
@when(parsers.parse('I click "{button}" and expect error "{error_msg}"'))
def i_click_button_and_expect_error_error_msg(button, error_msg):
    try:
        i_click_button(button)
    except Exception as e:
        actual_error_msg = str(e).strip()
        if str(e).strip() != error_msg:
            traceback.print_exc()
            msg = f"Got different exception clickign {button} - '{actual_error_msg}' instead of '{error_msg}'"
            assert False, msg
        return
    assert False, f"No error message {error_msg} raised when I pressed {button}"


@given(parsers.parse('I evaluate expression "{expression}"'))
@when(parsers.parse('I evaluate expression "{expression}"'))
def i_evaluate_expression(expression):
    expression = replace_variables(expression)
    exec(expression)


@given("I duplicate the selected objects")
@when("I duplicate the selected objects")
def i_duplicate_the_selected_objects():
    bpy.ops.bim.override_object_duplicate_move()
    bonsai.bim.handler.active_object_callback()


@when("I duplicate linked aggregate the selected objects")
def i_duplicate_linked_aggregate_the_selected_objects():
    bpy.ops.bim.object_duplicate_move_linked_aggregate()
    bonsai.bim.handler.active_object_callback()


@when("I refresh linked aggregate the selected object")
def i_refresh_the_selected_objects():
    bpy.ops.bim.refresh_linked_aggregate()
    bonsai.bim.handler.active_object_callback()


@given("I deselect all objects")
@when("I deselect all objects")
def i_deselect_all_objects():
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action="DESELECT")


@given(parsers.parse('the object "{name}" is selected'))
@when(parsers.parse('the object "{name}" is selected'))
@given(parsers.parse('I select the object "{name}"'))
@when(parsers.parse('I select the object "{name}"'))
def the_object_name_is_selected(name):
    i_deselect_all_objects()
    additionally_the_object_name_is_selected(name)


@then(parsers.parse('the object "{name}" is selected'))
def then_the_object_name_is_selected(name):
    obj = the_object_name_exists(name)
    assert obj in bpy.context.selected_objects


@then(parsers.parse('the object "{name}" is not selected'))
def then_the_object_name_is_not_selected(name):
    obj = the_object_name_exists(name)
    assert obj not in bpy.context.selected_objects


@given(parsers.parse('the object "{name}" is rotated by "{rotation_deg}" deg'))
@when(parsers.parse('the object "{name}" is rotated by "{rotation_deg}" deg'))
def the_object_name_is_rotated_by(name, rotation_deg):
    rotation_deg = [radians(float(rot)) for rot in rotation_deg.split(",")]
    obj = the_object_name_exists(name)
    obj.rotation_euler[0] += rotation_deg[0]
    obj.rotation_euler[1] += rotation_deg[1]
    obj.rotation_euler[2] += rotation_deg[2]
    bpy.context.view_layer.update()  # make sure matrix is updated


@given(parsers.parse('the object "{name}" is moved to "{location}"'))
@when(parsers.parse('the object "{name}" is moved to "{location}"'))
def the_object_name_is_moved_to_location(name, location):
    location = [float(co) for co in location.split(",")]
    obj = the_object_name_exists(name)
    obj.matrix_world.translation = location


@given(parsers.parse('the object "{name}" is scaled to "{scale}"'))
@when(parsers.parse('the object "{name}" is scaled to "{scale}"'))
def the_object_name_is_scaled_to_scale(name, scale):
    the_object_name_exists(name).scale *= float(scale)


@given(parsers.parse('the object "{name}" is placed in the collection "{collection}"'))
@when(parsers.parse('the object "{name}" is placed in the collection "{collection}"'))
def the_object_name_is_placed_in_the_collection_collection(name: str, collection: str) -> None:
    obj = the_object_name_exists(name)
    [c.objects.unlink(obj) for c in obj.users_collection]
    bpy.data.collections.get(collection).objects.link(obj)


@then(parsers.parse('the object "{name}" is placed in the collection "{collection}"'))
def then_the_object_name_is_placed_in_the_collection_collection(name: str, collection: str) -> None:
    obj = the_object_name_exists(name)
    assert obj in bpy.data.collections.get(collection).objects[:]


@given(parsers.parse('additionally the object "{name}" is selected'))
@when(parsers.parse('additionally the object "{name}" is selected'))
def additionally_the_object_name_is_selected(name):
    obj = bpy.context.scene.objects.get(name)
    if not obj:
        total = len(bpy.context.scene.objects)
        debug = "\n".join([o.name for o in bpy.context.scene.objects])
        assert False, f'The object "{name}" could not be selected. Available objects ({total} total):\n{debug}'
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


@given(parsers.parse('I rename the object "{name1}" to "{name2}"'))
@when(parsers.parse('I rename the object "{name1}" to "{name2}"'))
def i_rename_the_object_name1_to_name2(name1, name2):
    the_object_name_exists(name1).name = name2


@given(parsers.parse('I set "{prop}" to "{value}"'))
@when(parsers.parse('I set "{prop}" to "{value}"'))
def i_set_prop_to_value(prop: str, value: str) -> None:
    value = replace_variables(value)
    try:
        eval(f"bpy.context.{prop}")
    except:
        assert False, f"Property {prop} does not exist when trying to set to value {value}"
    try:
        exec(f'bpy.context.{prop} = r"{value}"')
    except:
        exec(f"bpy.context.{prop} = {value}")


@given(parsers.parse('I set "{prop}" to ""'))
@when(parsers.parse('I set "{prop}" to ""'))
def i_set_prop_to_empty_string(prop):
    try:
        eval(f"bpy.context.{prop}")
    except:
        assert False, f"Property {prop} does not exist"
    try:
        exec(f'bpy.context.{prop} = r""')
    except:
        pass


@when(parsers.parse('I am on frame "{number}"'))
def i_am_on_frame_number(number):
    bpy.context.scene.frame_set(int(number))


@given("I delete the selected objects")
@when("I delete the selected objects")
def i_delete_the_selected_objects():
    bpy.ops.bim.override_object_delete()


@given(parsers.parse('the variable "{key}" is "{value}"'))
@when(parsers.parse('the variable "{key}" is "{value}"'))
@then(parsers.parse('the variable "{key}" is "{value}"'))
def the_variable_key_is_value(key, value):
    variables[key] = eval(replace_variables(value))


@then("nothing happens")
def nothing_happens():
    pass


@given(parsers.parse('the object "{name}" exists'))
@when(parsers.parse('the object "{name}" exists'))
@then(parsers.parse('the object "{name}" exists'))
def the_object_name_exists(name: str) -> bpy.types.Object:
    # Some objects from linked collections may share the same name. This disambiguates them.
    if name.startswith("Col:"):
        _, collection_name, name = name.split(":")
        obj = bpy.data.collections.get(collection_name).objects.get(name)
    else:
        obj = bpy.data.objects.get(name)
    if not obj:
        debug = "\n".join([o.name for o in bpy.data.objects])
        assert False, f'The object "{name}" does not exist:\n{debug}'
    return obj


@then(parsers.parse('the object "{name}" does not exist'))
def the_object_name_does_not_exist(name) -> bpy.types.Object:
    obj = bpy.data.objects.get(name)
    if not obj:
        assert True, f'The object "{name}" exists'
    return obj


@given(parsers.parse('the collection "{name}" exists'))
@when(parsers.parse('the collection "{name}" exists'))
@then(parsers.parse('the collection "{name}" exists'))
def the_collection_name_exists(name) -> bpy.types.Collection:
    obj = bpy.data.collections.get(name)
    if not obj:
        assert False, f'The collection "{name}" does not exist'
    return obj


@then(parsers.parse('the collection "{name}" is selectable'))
def the_collection_name_is_selectable(name: str) -> None:
    col = the_collection_name_exists(name)
    assert col.hide_select == False


@then(parsers.parse('the collection "{name}" is unselectable'))
def the_collection_name_is_unselectable(name: str) -> None:
    col = the_collection_name_exists(name)
    assert col.hide_select == True


@then(parsers.parse('the collection "{name}" exists in viewlayer'))
def the_collection_exists_in_viewlayer(name: str) -> bpy.types.LayerCollection:
    col = the_collection_name_exists(name)
    results = tool.Blender.get_layer_collections_mapping([col])
    if not (layer_collection := results.get(col, None)):
        assert False, f'The collection "{name}" is not present in the current viewlayer'
    return layer_collection


@then(parsers.parse('the collection "{name}" exclude status is "{exclude}"'))
def the_collection_exclude_status_is(name: str, exclude: str) -> None:
    layer = the_collection_exists_in_viewlayer(name)
    assert layer.exclude == (exclude == "True")


@then(parsers.parse('the object "{name1}" and "{name2}" are different elements'))
def the_object_name1_and_name2_are_different_elements(name1, name2):
    ifc = an_ifc_file_exists()
    element1 = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name1)))
    element2 = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name2)))
    assert element1 != element2, f"Objects {name1} and {name2} have same elements {element1} and {element2}"


@then(parsers.parse('the object "{name}" has a body of "{value}"'))
def the_object_name_has_a_body_of_value(name, value):
    assert the_object_name_exists(name).data.body == value


@given(parsers.parse('the object "{name}" has a "{type}" representation of "{context}"'))
@then(parsers.parse('the object "{name}" has a "{type}" representation of "{context}"'))
def the_object_name_has_a_representation_type_of_context(name, type, context):
    ifc = an_ifc_file_exists()
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name)))
    context, subcontext, target_view = context.split("/")
    rep = ifcopenshell.util.representation.get_representation(element, context, subcontext or None, target_view or None)
    assert rep
    assert rep.RepresentationType == type, f"The object {name} does not have a {type} representation"


@given(parsers.parse('the object "{name}" data is a "{type}" representation of "{context}"'))
@then(parsers.parse('the object "{name}" data is a "{type}" representation of "{context}"'))
def the_object_name_data_is_a_type_representation_of_context(name, type, context):
    ifc = an_ifc_file_exists()
    context, subcontext, target_view = context.split("/")
    rep = ifc.by_id(tool.Geometry.get_mesh_props(the_object_name_exists(name).data).ifc_definition_id)
    assert rep
    assert rep.RepresentationType == type, f"The object {name} is not a {type} representation"
    assert rep.ContextOfItems.ContextType == context
    assert rep.ContextOfItems.ContextIdentifier == subcontext
    assert rep.ContextOfItems.TargetView == target_view


@then(parsers.parse('the material "{name}" exists'))
def the_material_name_exists(name: str) -> bpy.types.Material:
    obj = bpy.data.materials.get(name)
    if not obj:
        assert False, f'The material "{name}" does not exist'
    return obj


@then(parsers.parse('the material "{name}" does not exist'))
def the_material_name_does_not_exist(name):
    assert bpy.data.materials.get(name) is None, "Material exists"


def get_ifc_material_by_name(name: str) -> Union[ifcopenshell.entity_instance, None]:
    ifc_file = tool.Ifc.get()
    material = next((m for m in ifc_file.by_type("IfcMaterial") if m.Name == name), None)
    return material


@then(parsers.parse('the IFC material "{name}" exists'))
def the_ifc_material_name_exists(name: str) -> ifcopenshell.entity_instance:
    material = get_ifc_material_by_name(name)
    if not material:
        assert False, f'The IFC material "{name}" does not exist'
    return material


@then(parsers.parse('the material "{name}" does not exist'))
def the_ifc_material_name_does_not_exist(name):
    assert get_ifc_material_by_name(name) is None, "IFC Material exists"


@then("an IFC file does not exist")
def an_ifc_file_does_not_exist():
    ifc = tool.Ifc.get()
    if ifc:
        assert False, "An IFC is available"


@then("an IFC file exists")
def an_ifc_file_exists():
    ifc = tool.Ifc.get()
    if not ifc:
        assert False, "No IFC file is available"
    return ifc


@then(parsers.parse('the object "{name}" should display as "{mode}"'))
def the_object_name_should_display_as_mode(name, mode):
    obj = the_object_name_exists(name)
    assert obj.display_type == mode


@then(parsers.parse('the object "{name}" is voided by "{void}"'))
def the_object_name_is_voided_by_void(name, void):
    ifc = tool.Ifc.get()
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name)))
    assert any(rel for rel in element.HasOpenings if rel.RelatedOpeningElement.Name == void), "No void found"


@then(parsers.parse('the object "{name}" is not voided by "{void}"'))
def the_object_name_is_not_voided_by_void(name, void):
    try:
        the_object_name_is_voided_by_void(name, void)
    except AssertionError:
        return
    assert False, "A void was found"


@then(parsers.parse('the object "{name}" is not voided'))
def the_object_name_is_not_voided(name):
    ifc = tool.Ifc.get()
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name)))
    assert not element.HasOpenings, "A void was found"


@then(parsers.parse('the object "{name}" is a void'))
def the_object_name_is_a_void(name):
    ifc = tool.Ifc.get()
    obj = the_object_name_exists(name)
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(obj))
    assert any(element.VoidsElements), "No void was found"


@then(parsers.parse('the object "{name}" is not a void'))
def the_object_name_is_not_a_void(name):
    try:
        the_object_name_is_a_void(name)
    except AssertionError:
        return
    assert False, "A void was found"


@given(parsers.parse('the object "{name}" is visible'))
def given_the_object_name_is_visible(name):
    obj = the_object_name_exists(name)
    obj.hide_set(False)


@given(parsers.parse('the object "{name}" is not visible'))
def given_the_object_name_is_not_visible(name):
    obj = the_object_name_exists(name)
    obj.hide_set(True)


@then(parsers.parse('the object "{name}" is visible'))
def the_object_name_is_visible(name):
    obj = the_object_name_exists(name)
    assert obj.hide_get() == False


@then(parsers.parse('the object "{name}" is not visible'))
def the_object_name_is_not_visible(name):
    obj = the_object_name_exists(name)
    assert obj.hide_get() == True


@then(parsers.parse('the object "{name}" is an "{ifc_class}"'))
def the_object_name_is_an_ifc_class(name, ifc_class):
    ifc = an_ifc_file_exists()
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name)))
    assert element.is_a(ifc_class), f'Object "{name}" is an {element.is_a()}'


@then(parsers.parse('the object "{name}" is not an IFC element'))
def the_object_name_is_not_an_ifc_element(name):
    obj = the_object_name_exists(name)
    ifc_definition_id = tool.Blender.get_ifc_definition_id(obj)
    assert ifc_definition_id == 0, f"The object {obj} has an ID of {ifc_definition_id}"


@then(parsers.parse('the object "{name}" has no data'))
def the_object_name_has_no_data(name):
    assert the_object_name_exists(name).data is None


@then(parsers.parse('the object "{name}" has data which is an IFC representation'))
def the_object_name_has_ifc_representation_data(name):
    id = tool.Geometry.get_mesh_props(the_object_name_exists(name).data).ifc_definition_id
    assert id != 0, f"The ID is {id}"


@then(parsers.parse('the material "{name}" is an IFC material'))
def the_material_name_is_an_ifc_material(name):
    obj = the_material_name_exists(name)
    ifc_definition_id = tool.Blender.get_ifc_definition_id(obj)
    assert ifc_definition_id != 0, f"The material {obj} has no ID: {ifc_definition_id}"


@then(parsers.parse('the material "{name}" is not an IFC material'))
def the_material_name_is_not_an_ifc_material(name):
    obj = the_material_name_exists(name)
    ifc_definition_id = tool.Blender.get_ifc_definition_id(obj)
    assert ifc_definition_id == 0, f"The material {obj} has an ID of {ifc_definition_id}"


@then(parsers.parse('the material "{name}" is an IFC style'))
def the_material_name_is_an_ifc_style(name):
    obj = the_material_name_exists(name)
    ifc_definition_id = tool.Blender.get_ifc_definition_id(obj)
    assert ifc_definition_id != 0, f"The material {obj} has a style ID of {ifc_definition_id}"


@then(parsers.parse('the material "{name}" is not an IFC style'))
def the_material_name_is_not_an_ifc_style(name):
    obj = the_material_name_exists(name)
    ifc_definition_id = tool.Blender.get_ifc_definition_id(obj)
    assert ifc_definition_id == 0, f"The material {obj} has a style ID of {ifc_definition_id}"


@then(parsers.parse('the material "{name}" colour is "{colour}"'))
def then_the_material_name_colour_is_set_to_colour(name, colour):
    diffuse_color = list(the_material_name_exists(name).diffuse_color)
    assert diffuse_color == [float(c) for c in colour.split(",")], f"The colour is {diffuse_color}"


@then(parsers.parse('the object "{name}" has "{number}" vertices'))
def the_object_name_has_number_vertices(name, number):
    total = len(the_object_name_exists(name).data.vertices)
    assert total == int(number), f"We found {total} vertices"


@then(parsers.parse('the object "{name}" is filled by "{name2}"'))
def the_object_name_is_filled_by_filling(name, name2):
    ifc = tool.Ifc.get()
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name)))
    debug = {}
    for rel in ifcopenshell.util.element.get_openings(element):
        filling = None
        opening = rel.RelatedOpeningElement
        for rel2 in opening.HasFillings or []:
            filling = rel2.RelatedBuildingElement
            break
        debug[opening] = filling
        filling_obj = tool.Ifc.get_object(filling)
        if filling_obj and filling_obj.name == name2:
            return True
    debug = "\n".join([f"{k} filled by {v}" for k, v in debug.items()])
    assert False, f"Object {name} is not filled by {name2}.\n{debug}"


@then(parsers.parse('the void "{name}" is filled by "{filling}"'))
def the_void_name_is_filled_by_filling(name, filling):
    ifc = tool.Ifc.get()
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name)))
    assert any(rel.RelatedBuildingElement.Name == filling for rel in element.HasFillings), "No filling found"


@then(parsers.parse('the void "{name}" is not filled by "{filling}"'))
def the_void_name_is_not_filled_by_filling(name, filling):
    try:
        the_void_name_is_filled_by_filling(name, filling)
    except AssertionError:
        return
    assert False, "A filling was found"


@when(parsers.parse('the object "{name}" is not a filling'))
@then(parsers.parse('the object "{name}" is not a filling'))
def the_object_name_is_not_a_filling(name):
    ifc = tool.Ifc.get()
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name)))
    assert not any(element.FillsVoids), "A filling was found"


@then(parsers.parse('"{prop}" is "{value}"'))
def prop_is_value(prop, value):
    prop = replace_variables(prop)
    value = replace_variables(value)
    is_value = False
    try:
        exec(f'assert bpy.context.{prop} == "{value}"')
        is_value = True
    except:
        try:
            exec(f"assert bpy.context.{prop} == {value}")
            is_value = True
        except:
            try:
                exec(f"assert list(bpy.context.{prop}) == {value}")
                is_value = True
            except:
                try:
                    exec(f"assert vectors_are_equal(bpy.context.{prop}, {value})")
                    is_value = True
                except:
                    pass
    if not is_value:
        print(f"bpy.context.{prop}")
        actual_value = eval(f"bpy.context.{prop}")
        assert False, f"Value is {actual_value}"


@then(parsers.parse('"{prop}" is roughly "{value}"'))
def prop_is_roughly_value(prop, value):
    prop = replace_variables(prop)
    value = replace_variables(value)
    is_value = False
    try:
        exec(f'assert round(bpy.context.{prop}, 3) == "{value}"')
        is_value = True
    except:
        try:
            exec(f"assert round(bpy.context.{prop}, 3) == {value}")
            is_value = True
        except:
            pass
    if not is_value:
        print(f"bpy.context.{prop}")
        actual_value = round(eval(f"bpy.context.{prop}"), 3)
        assert False, f"Value is {actual_value}"


@then(parsers.parse('the object "{name}" has a cartesian point offset of "{offset}"'))
def the_object_name_has_a_cartesian_point_offset_of_offset(name: str, offset: str) -> None:
    offset = replace_variables(offset)
    obj = the_object_name_exists(name)
    props = tool.Blender.get_object_bim_props(obj)
    assert props.blender_offset_type == "CARTESIAN_POINT"
    obj_offset = np.array(tuple(map(float, props.cartesian_point_offset.split(","))))
    offset = np.array(tuple(map(float, offset.split(","))))
    assert np.allclose(obj_offset, offset)


@then(parsers.parse('the object "{name}" has the material "{material}"'))
def the_object_name_has_the_material_material(name: str, material: str) -> None:
    assert material in [ms.material.name for ms in the_object_name_exists(name).material_slots if ms.material]


@then(parsers.parse('the object "{name}" has the IFC material "{material_name}"'))
def the_object_name_has_the_ifc_material_material_name(name: str, material_name: str):
    element = tool.Ifc.get_entity(the_object_name_exists(name))
    material = ifcopenshell.util.element.get_material(element)
    assert material and material.Name == material_name


@then(
    parsers.parse(
        'the object "{name}" has a "{thickness}" thick layered material containing the material "{material_name}"'
    )
)
def the_object_name_has_a_thickness_thick_layered_material_containing_the_material_material(
    name, thickness, material_name
):
    element = tool.Ifc.get_entity(the_object_name_exists(name))
    material = ifcopenshell.util.element.get_material(element)
    assert material and "LayerSet" in material.is_a()
    if material.is_a("IfcMaterialLayerSetUsage"):
        material = material.ForLayerSet
    total_thickness = 0
    material_names = []
    for layer in material.MaterialLayers or []:
        total_thickness += layer.LayerThickness
        material_names.append(layer.Material.Name)
    assert is_x(total_thickness, float(thickness))
    assert material_name in material_names


@then(parsers.parse('the object "{name}" has no IFC materials'))
def the_object_has_no_ifc_materials(name: str) -> None:
    element = tool.Ifc.get_entity(the_object_name_exists(name))
    material = ifcopenshell.util.element.get_material(element)
    assert material is None


@then(
    parsers.parse(
        'the object "{name}" has a profiled material containing the material "{material_name}" and profile "{profile_name}"'
    )
)
def the_object_name_has_a_profiled_material_containing_the_material_material_and_profile_profile(
    name, material_name, profile_name
):
    element = tool.Ifc.get_entity(the_object_name_exists(name))
    material = ifcopenshell.util.element.get_material(element)
    assert material and "ProfileSet" in material.is_a()
    if material.is_a("IfcMaterialProfileSetUsage"):
        material = material.ForProfileSet
    material_names = []
    profile_names = []
    for profile in material.MaterialProfiles or []:
        material_names.append(profile.Material.Name)
        profile_names.append(profile.Profile.ProfileName)
    assert material_name in material_names, f"No material {material_name} found in profiled materials: {material_names}"
    assert profile_name in profile_names, f"No profile {profile_name} found in material profiles: {profile_names}"


@then(parsers.parse('the object "{name}" does not have the material "{material}"'))
def the_object_name_does_not_have_the_material_material(name, material):
    assert material not in [ms.material.name for ms in the_object_name_exists(name).material_slots]


@then(parsers.parse('the object "{name}" is in the collection "{collection}"'))
def the_object_name_is_in_the_collection_collection(name, collection):
    assert collection in [c.name for c in the_object_name_exists(name).users_collection]


@then(parsers.parse('the collection "{name1}" is in the collection "{name2}"'))
def the_collection_name1_is_in_the_collection_name2(name1, name2):
    assert bpy.data.collections.get(name2).children.get(name1)


@then(parsers.parse('the collection "{name}" does not exist'))
def the_collection_name_does_not_exist(name):
    obj = bpy.data.collections.get(name)
    assert obj is None, f"Collection {name} exists"


@then(parsers.parse('objects starting with "{name}" do not exist'))
def objects_not_exist_starting_with(name):
    objs = [obj for obj in bpy.data.objects if obj.name.startswith(name) and len(obj.users_collection) > 0]
    if len(objs) > 0:
        assert False, f'{len(objs)} objects starting with "{name}" exist'
    assert True


@then(parsers.parse('the object "{name}" is at "{location}"'))
def the_object_name_is_at_location(name, location):
    obj_location = the_object_name_exists(name).location
    assert (
        obj_location - Vector([float(co) for co in location.split(",")])
    ).length < 0.05, f"Object is at {obj_location} instead of {location}"


@then(parsers.parse('the object "{name}" has a vertex at "{location}"'))
def the_object_name_has_a_vertex_at_location(name, location):
    obj = the_object_name_exists(name)
    is_pass = False
    target = Vector([float(co) for co in location.split(",")])
    verts = []
    for v in obj.data.vertices:
        verts.append(obj.matrix_world @ v.co)
        if (verts[-1] - target).length < 0.001:
            is_pass = True
    assert is_pass, f"No verts found at {location}: {verts}"


@then(parsers.parse('the object "{name}" has no scale'))
def the_object_name_has_no_scale(name):
    assert the_object_name_exists(name).scale == Vector(
        (
            1.0,
            1.0,
            1.0,
        )
    )


@then(parsers.parse('the object "{name}" dimensions are "{dimensions}"'))
def the_object_name_dimensions_are_dimensions(name, dimensions):
    actual_dimensions = list(the_object_name_exists(name).dimensions)
    expected_dimensions = [float(co) for co in dimensions.split(",")]
    for i, number in enumerate(actual_dimensions):
        assert is_x(number, expected_dimensions[i]), f"Expected {expected_dimensions} but got {actual_dimensions}"


@then(parsers.parse('the object "{name}" top right corner is at "{location}"'))
def the_object_name_top_right_corner_is_at_location(name, location):
    obj = the_object_name_exists(name)
    obj_corner = obj.matrix_world @ Vector(obj.bound_box[6])
    assert (
        obj_corner - Vector([float(co) for co in location.split(",")])
    ).length < 0.05, f"Object has top right corner {obj_corner} instead of {location}"


@then(parsers.parse('the object "{name}" bottom left corner is at "{location}"'))
def the_object_name_bottom_left_corner_is_at_location(name, location):
    obj = the_object_name_exists(name)
    obj_corner = obj.matrix_world @ Vector(obj.bound_box[0])
    assert (
        obj_corner - Vector([float(co) for co in location.split(",")])
    ).length < 0.05, f"Object has bottom left corner {obj_corner} instead of {location}"


@then(parsers.parse('the object "{name}" is contained in "{container_name}"'))
def the_object_name_is_contained_in_container_name(name, container_name):
    ifc = an_ifc_file_exists()
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name)))
    container = ifcopenshell.util.element.get_container(element)
    if not container:
        assert False, f'Object "{name}" is not in any container'
    assert container.Name == container_name, f'Object "{name}" is in {container}'


@then(parsers.parse('the object "{name}" is contained in object "{container_name}"'))
def the_object_name_is_contained_in_object_container_name(name: str, container_name: str) -> None:
    ifc = an_ifc_file_exists()
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name)))
    container = ifcopenshell.util.element.get_container(element)
    if not container:
        assert False, f'Object "{name}" is not in any container'
    container_obj = tool.Ifc.get_object(container)
    assert container_obj.name == container_name, f'Object "{name}" is in {container_obj}'


@then(parsers.parse('the object "{name}" is aggregated by object "{aggregate_name}"'))
def the_object_name_is_aggregated_by_object_aggregate_name(name: str, aggregate_name: str) -> None:
    ifc = an_ifc_file_exists()
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name)))
    aggregate = ifcopenshell.util.element.get_aggregate(element)
    if not aggregate:
        assert False, f'Object "{name}" is not aggregated by any element'
    aggregate_obj = tool.Ifc.get_object(aggregate)
    assert aggregate_obj.name == aggregate_name, f'Object "{name}" is aggregated by {aggregate_obj}'


@then(parsers.parse('the object "{name}" has no aggregate'))
def the_object_name_has_no_aggregate(name: str) -> None:
    ifc = an_ifc_file_exists()
    element = ifc.by_id(tool.Blender.get_ifc_definition_id(the_object_name_exists(name)))
    aggregate = ifcopenshell.util.element.get_aggregate(element)
    if aggregate:
        assert False, f'Object "{name}" is aggregated by element "{aggregate}"'


@then(parsers.parse('the file "{name}" should contain "{value}"'))
def the_file_name_should_contain_value(name, value):
    name = replace_variables(name)
    with open(name, "r") as f:
        content = f.read()
        assert value in content, f"File {name} does not contain {value}:\n{content}"


@then(parsers.parse('the file "{name}" should not contain "{value}"'))
def the_file_name_should_contain_value(name, value):
    name = replace_variables(name)
    with open(name, "r") as f:
        content = f.read()
        assert value not in content, f"File {name} contains {value}:\n{content}"


@then(parsers.parse('the object "{name}" has no modifiers'))
def the_object_name_has_no_modifiers(name):
    assert len(the_object_name_exists(name).modifiers) == 0


@given(parsers.parse('I load the IFC test file "{filepath}"'))
def i_load_the_ifc_test_file(filepath):
    filepath = f"{variables['cwd']}{filepath}"
    bpy.ops.bim.load_project(filepath=filepath)


@given("I load the demo construction library")
@when("I load the demo construction library")
def i_add_a_construction_library():
    lib_path = "./bonsai/bim/data/libraries/IFC4 Demo Library.ifc"
    bpy.ops.bim.select_library_file(filepath=lib_path, append_all=True)


@given(parsers.parse('the cursor is at "{location}"'))
@when(parsers.parse('the cursor is at "{location}"'))
def the_cursor_is_at_location(location):
    bpy.context.scene.cursor.location = [float(co) for co in location.split(",")]


@given("I display the construction type browser")
@when("I display the construction type browser")
def i_display_the_construction_type_browser():
    bpy.ops.bim.display_constr_types("INVOKE_DEFAULT")


@given("I add the construction type")
@when("I add the construction type")
def i_add_the_active_construction_type():
    props = tool.Model.get_model_props()
    bpy.ops.bim.add_occurrence(relating_type_id=int(props.relating_type_id))


@then(parsers.parse("construction type is {relating_type_name}"))
def construction_type(relating_type_name):
    props = tool.Model.get_model_props()
    relating_type = AuthoringData.relating_type_name_by_id(props.ifc_class, props.relating_type_id)
    assert relating_type == relating_type_name, f"Construction Type is a {relating_type}, not a {relating_type_name}"


@given("I toggle edit mode")
@when("I toggle edit mode")
@then("I toggle edit mode")
def i_toggle_edit_mode():
    props = tool.Geometry.get_geometry_props()
    print(f"Toggling from {bpy.context.mode} / {props.mode} ...")
    print("Selected items:", bpy.context.active_object, bpy.context.selected_objects)
    if bpy.context.mode == "OBJECT":
        bpy.ops.bim.override_mode_set_edit()
    else:
        bpy.ops.bim.override_mode_set_object()
    print(f"... mode is now {bpy.context.mode} / {props.mode}")


@when("I move the cursor to the bottom left corner")
def move_cursor_bottom_left():
    bpy.context.window.cursor_warp(10, 10)


@given(parsers.parse("I prepare to undo"))
@when(parsers.parse("I prepare to undo"))
@then(parsers.parse("I prepare to undo"))
def prepare_undo():
    bpy.ops.ed.undo_push(message="UNDO STEP")


@given(parsers.parse("I undo"))
@when(parsers.parse("I undo"))
@then(parsers.parse("I undo"))
def hit_undo():
    bpy.ops.ed.undo_push(message="UNDO STEP")
    bpy.ops.ed.undo()
    # override = tool.Blender.get_viewport_context()
    # with bpy.context.temp_override(**override):
    #     bpy.ops.ed.undo()


@then(parsers.parse('the object "{obj_name1}" has a connection with "{obj_name2}"'))
def the_obj1_has_a_connection_with_obj2(obj_name1, obj_name2):
    element1 = replace_variables(obj_name1)
    element1 = tool.Ifc.get_entity(the_object_name_exists(element1))
    element2 = replace_variables(obj_name2)
    element2 = tool.Ifc.get_entity(the_object_name_exists(element2))
    connections = []
    if hasattr(element1, "ConnectedTo") and element1.ConnectedTo:
        connections = [connection for connection in element1.ConnectedTo]
    elif hasattr(element1, "ConnectedFrom") and element1.ConnectedFrom:
        connections = [connection for connection in element1.ConnectedFrom]
    else:
        assert False, f'Object "{obj_name1}" has no connections'

    relationships = {}
    for conn in connections:
        relationships[conn.RelatedElement] = conn.RelatingElement

    for key, value in relationships.items():
        assert (key.id() == element1.id() and value.id() == element2.id()) or (
            key.id() == element2.id() and value.id() == element1.id()
        ), f"The object {obj_name1} is connected to {obj_name2}"


@then(parsers.parse('the object "{obj_name1}" and "{obj_name2}" belong to the same Linked Aggregate Group'))
def the_obj1_and_obj2_belong_the_same_linked_aggregate_group(obj_name1, obj_name2):
    element1 = replace_variables(obj_name1)
    element1 = tool.Ifc.get_entity(the_object_name_exists(element1))
    element2 = replace_variables(obj_name2)
    element2 = tool.Ifc.get_entity(the_object_name_exists(element2))

    elements = [element1, element2]
    groups = []
    for element in elements:
        product_linked_agg_group = [
            r.RelatingGroup
            for r in getattr(element, "HasAssignments", []) or []
            if r.is_a("IfcRelAssignsToGroup")
            if "BBIM_Linked_Aggregate" in r.RelatingGroup.Name
        ]
        try:
            groups.append(product_linked_agg_group[0].id())
        except:
            assert False, "Object is not part of a Linked Aggregate."

    assert groups[0] == groups[1], "Objects do not belong to the same Linked Aggregate group"


@when(parsers.parse('the object layer length is set to "{value}"'))
def the_obj_layer_length_is_set_to(value):
    value = float(value)
    try:
        eval("bpy.context.scene.BIMModelProperties.length")
    except:
        assert False, f"Property BIMModelProperties.length does not exist when trying to set to value {value}"
    props = tool.Model.get_model_props()
    props.length = value
    bpy.ops.bim.change_layer_length(length=value)


# These definitions are not to be used in tests but simply in debugging failing tests


@given(parsers.parse("I run test code"))
@when(parsers.parse("I run test code"))
@then(parsers.parse("I run test code"))
def run_test_code():
    pass


@given(parsers.parse("I fail"))
@when(parsers.parse("I fail"))
@then(parsers.parse("I fail"))
def i_fail():
    assert False


@given(parsers.parse("I save sample test files"))
@when(parsers.parse("I save sample test files"))
@then(parsers.parse("I save sample test files"))
def saving_sample_test_files(and_open_in_blender=None):
    filepath = f"{variables['cwd']}/test/files/temp/sample_test_file"
    print(f"Saved to {filepath}")
    bpy.ops.bim.save_project(filepath=f"{filepath}.ifc", should_save_as=True)
    bpy.ops.wm.save_as_mainfile(filepath=f"{filepath}.blend")


@given(parsers.parse("I load test blend file"))
@when(parsers.parse("I load test blend file"))
@then(parsers.parse("I load test blend file"))
def opening_sample_test_files_in_blender():
    filepath = f"{variables['cwd']}/test/files/temp/sample_test_file.blend"
    bpy.ops.wm.open_mainfile(filepath=filepath, display_file_selector=False)


# TODO: merge to single fixture with `saving_sample_test_files`; add "and wait"
@given(parsers.parse("I save sample test files and open in blender"))
@when(parsers.parse("I save sample test files and open in blender"))
@then(parsers.parse("I save sample test files and open in blender"))
def saving_sample_test_files_and_open_in_blender():
    saving_sample_test_files()
    filepath = f"{variables['cwd']}/test/files/temp/sample_test_file.blend"
    import subprocess

    subprocess.Popen([bpy.app.binary_path, f"{filepath}"])


@given(parsers.parse("I run pdb"))
@when(parsers.parse("I run pdb"))
@then(parsers.parse("I run pdb"))
def run_pdb():
    import pdb

    pdb.set_trace()
