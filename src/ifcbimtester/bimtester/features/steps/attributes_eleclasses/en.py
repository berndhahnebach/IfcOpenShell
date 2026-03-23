# BIMTester - OpenBIM Auditing Tool
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BIMTester.
#
# BIMTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BIMTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BIMTester.  If not, see <http://www.gnu.org/licenses/>.

from behave import step
from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('All "{ifcos_query}" objects do have a valid value assigned for the attribut Name')
def step_impl(context, ifcos_query):
    name_attribut_has_valid_value(
        context,
        ifcos_query,
    )


@step('All "{ifcos_query}" objects do have a valid value assigned for the attribut Description')
def step_impl(context, ifcos_query):
    description_attribut_has_valid_value(
        context,
        ifcos_query,
    )


@step('There are "{ifcos_query}" elements only inside all "{ifc_entity_class}" elements')
def step_impl(context, ifcos_query, ifc_entity_class):
    entityclass_only(
        context,
        ifcos_query,
        ifc_entity_class,
    )


@step('There are no "{ifcos_query}" elements inside all "{ifc_entity_class}" elements')
def step_impl(context, ifcos_query, ifc_entity_class):
    no_eleclass(
        context,
        ifcos_query,
        ifc_entity_class,
    )


@step('There are precisely "{count_exact}" "{ifcos_query}" objects')
def step_impl(context, count_exact, ifcos_query):
    entityclass_count_exact(
        context,
        ifcos_query,
        count_exact,
    )


@step('There are between "{count_min}" and "{count_max}" "{ifcos_query}" objects')
def step_impl(context, count_min, count_max, ifcos_query):
    entityclass_count_range(
        context,
        ifcos_query,
        count_min,
        count_max,
    )


@step('There are no "{ifcos_query}" elements because "{reason}"')
def step_impl(context, ifcos_query, reason):
    no_eleclass(
        context,
        ifcos_query,
    )


@step('All "{ifcos_query}" elements class attributes have a value')
def step_impl(context, ifcos_query):
    eleclass_have_class_attributes_with_a_value(
        context,
        ifcos_query,
    )


@step('All "{ifcos_query}" elements have a Name matching the pattern "{pattern}"')
def step_impl(context, ifcos_query, pattern):
    eleclass_has_name_matching_pattern(
        context,
        ifcos_query,
        pattern,
    )


@step('All "{ifcos_query}" elements have a Description matching the pattern "{pattern}"')
def step_impl(context, ifcos_query, pattern):
    eleclass_has_description_matching_pattern(
        context,
        ifcos_query,
        pattern,
    )


@step('All "{ifcos_query}" elements have one of these names "{valuerange}"')
def step_impl(context, ifcos_query, valuerange):
    eleclass_has_name_valuerange_of(
        context,
        ifcos_query,
        valuerange,
    )


# ************************************************************************************************
# helper
def eleclass_has_name_matching_pattern(
    context, target_ifcos_query, target_pattern
):
    import re

    context.falseelems = []
    context.falseguids = []

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        if not re.search(target_pattern, elem.Name):
            context.falseelems.append(util.get_false_elem_string(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)

    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements in the file elements do not have a Name matching {parameter}"),
        message_some_falseelems=_("{falsecount} of {elemcount} {ifc_class} do not have a Name matching {parameter}: {falseelems}"),
        parameter=target_pattern
    )


def eleclass_has_description_matching_pattern(
    context, target_ifcos_query, target_pattern
):
    import re

    context.falseelems = []
    context.falseguids = []

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        if not re.search(target_pattern, elem.Description):
            context.falseelems.append(util.get_false_elem_string(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)

    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements in the file elements do not have a Description matching {parameter}"),
        message_some_falseelems=_("{falsecount} of {elemcount} {ifc_class} do not have a Description matching {parameter}: {falseelems}"),
        parameter=target_pattern
    )


def eleclass_has_name_valuerange_of(
    context, target_ifcos_query, target_valuerange_str
):
    from ast import literal_eval
    target_valuerange_obj = literal_eval(target_valuerange_str)

    context.falseelems = []
    context.falseguids = []

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        if elem.Name not in target_valuerange_obj:
            context.falseelems.append(util.get_false_elem_string(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    if context.falsecount > 0:
        # -- SKIP: Remaining steps in current feature.
        context.feature.skip(_("Error in eleclass_has_name_valuerange_of"))

    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements in the file elements do not have a name out of {parameter}"),
        message_some_falseelems=_("{falsecount} of {elemcount} {ifc_class} do not have a name out of {parameter}: {falseelems}"),
        parameter=target_valuerange_obj
    )


def entityclass_count_exact(
    context, target_ifcos_query, count_exact_str
):

    try:
        count_exact = int(count_exact_str)
    except:
        assert False, (_("Can not convert {} into a integer value.".format(count_exact_str)))

    len_target_elements = len(util.get_elems(IfcStore.file, target_ifcos_query))

    if count_exact != len_target_elements:
        assert False, (_(
            "There are precisely {} {} objects, which ist not equal {}."
            .format(len_target_elements, target_ifcos_query, count_exact)
        ))


def entityclass_count_range(
    context, target_ifcos_query, count_min_str, count_max_str,
):

    try:
        count_min = int(count_min_str)
    except:
        assert False, (_("Can not convert {} into a integer value.".format(count_exact_str)))
    try:
        count_max = int(count_max_str)
    except:
        assert False, (_("Can not convert {} into a integer value.".format(count_exact_str)))

    len_target_elements = len(util.get_elems(IfcStore.file, target_ifcos_query))

    if not (count_min <= len_target_elements <= count_max):
        assert False, (_(
            "There are precisely {} {} objects, which ist not between {} and {}."
            .format(len_target_elements, target_ifcos_query, count_min, count_max)
        ))


def no_eleclass(
    context, target_ifcos_query, target_ifc_entity_class
):

    context.falseelems = []
    context.falseguids = []

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    all_elements = IfcStore.file.by_type(target_ifc_entity_class)
    for elem in target_elements:
        context.falseelems.append(util.get_false_elem_string(elem))
        context.falseguids.append(elem.GlobalId)

    context.elemcount = len(all_elements)
    context.falsecount = len(context.falseelems)
    if context.falsecount > 0:
        # -- SKIP: Remaining steps in current feature.
        context.feature.skip(_("Error in no_eleclass"))

    # be careful somehow the opposite of most other tests is tested
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {parameter} elements in the file are {ifc_class} elements."),
        message_some_falseelems=_("{falsecount} of {elemcount} {parameter} false_elements are {ifc_class} elements: {falseelems}"),
        parameter=target_ifc_entity_class
    )


def entityclass_only(
    context, target_ifcos_query, target_ifc_entity_group
):

    context.falseelems = []
    context.falseguids = []

    # target_entity_group_elements ... example all IfcBuildingElements
    # target_ifcos_query_elements ... example all (IfcWall, IfcColumn, IfcSlab)
    # all IfcBuildingElements minus all (IfcWall, IfcColumn, IfcSlab) shluld be 0
    # if there is some rest, there are inside IfcBuildingElement other than (IfcWall, IfcColumn, IfcSlab)

    # https://standards.buildingsmart.org/IFC/DEV/IFC4_2/FINAL/HTML/schema/ifckernel/lexical/ifcproduct.htm
    target_entity_group_elements = IfcStore.file.by_type(target_ifc_entity_group)
    target_ifcos_query_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    false_elements = list(set(target_entity_group_elements) - set(target_ifcos_query_elements))

    # In IFC2x3 IfcReinforcingBar is IfcBuildingElement in IFC4 not

    for elem in false_elements:
        context.falseelems.append(util.get_false_elem_string(elem))
        context.falseguids.append(elem.GlobalId)

    context.elemcount = len(target_entity_group_elements)
    context.falsecount = len(context.falseelems)
    if context.falsecount > 0:
        # -- SKIP: Remaining steps in current feature.
        context.feature.skip(_("Error in entityclass_only"))

    # be careful somehow the opposite of most other tests is tested
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {parameter} objects in the file are not {ifc_class} inside {parameter} objects."),
        message_some_falseelems=_("{falsecount} of {elemcount} {parameter} false_objects are not {ifc_class} inside {parameter} objects: {falseelems}"),
        parameter=target_ifc_entity_group
    )


def name_attribut_has_valid_value(
    context, target_ifcos_query
):

    context.falseelems = []
    context.falseguids = []

    # None ist nicht gueltig
    # ist ein Leerzeichen ein gueltiger Wert?
    # ist ein Name mit einem Leerzeichen ein gueltiger Wert, " ", " Beton", oder "Beton "
    # meines Erachtes sind das alles keine gueltigen Werte

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    # print(len(target_elements))
    for elem in target_elements:
        # print(elem.Name)
        if elem.Name is None:
            context.falseelems.append("{}, {}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]), elem.Name))
            context.falseguids.append(elem.GlobalId)
        elif (
            elem.Name.isspace() is True  # in Allplan erzeugt ein leerer Name ein Leerzeichen als attributwert, analog Material
            or len(elem.Name) - len(elem.Name.strip()) > 0
            # https://stackoverflow.com/a/13649013 all white space character like newline, not only spaces
        ):
            # print("xxxxx{}xxxxx".format(elem.Name))
            context.falseelems.append("{}, xxxxx{}xxxxx".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]), elem.Name))
            context.falseguids.append(elem.GlobalId)
        else:
            # valid value
            pass

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The attribut Name of all {elemcount} elements is not proper set."),
        message_some_falseelems=_("The attribut Name of {falsecount} out of {elemcount} {ifc_class} elements is not proper set: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )


def description_attribut_has_valid_value(
    context, target_ifcos_query
):

    context.falseelems = []
    context.falseguids = []

    # None ist nicht gueltig
    # ist ein Leerzeichen ein gueltiger Wert?
    # ist ein Name mit einem Leerzeichen ein gueltiger Wert, " ", " Beton", oder "Beton "
    # meines Erachtes sind das alles keine gueltigen Werte

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    # print(len(target_elements))
    for elem in target_elements:
        # print(elem.Description)
        if elem.Description is None:
            context.falseelems.append("{}, {}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]), elem.Description))
            context.falseguids.append(elem.GlobalId)
        elif (
            elem.Description.isspace() is True
            or len(elem.Description) - len(elem.Description.strip()) > 0
            # https://stackoverflow.com/a/13649013 all white space character like newline, not only spaces
        ):
            # print("xxxxx{}xxxxx".format(elem.Description))
            context.falseelems.append("{}, xxxxx{}xxxxx".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]), elem.Description))
            context.falseguids.append(elem.GlobalId)
        else:
            # valid value
            pass

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The attribut Name of all {elemcount} elements is not proper set."),
        message_some_falseelems=_("The attribut Name of {falsecount} out of {elemcount} {ifc_class} elements is not proper set: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )
