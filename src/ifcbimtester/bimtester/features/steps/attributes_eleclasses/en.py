import ifcopenshell.util.element as eleutils

from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


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


@step('In the model are precisely "{count_exact}" "{ifc_entity_class}" objects available')
def step_impl(context, count_exact, ifc_entity_class):
    entityclass_count_exact(
        context,
        ifc_entity_class,
        count_exact,
    )


@step('In the model are between "{count_min}" and "{count_max}" "{ifc_entity_class}" objects available')
def step_impl(context, count_min, count_max, ifc_entity_class):
    entityclass_count_range(
        context,
        ifc_entity_class,
        count_min,
        count_max,
    )


@step('All "{ifcos_query}" elements have one of these names "{valuerange}"')
def step_impl(context, ifcos_query, valuerange):
    eleclass_has_name_valuerange_of(
        context,
        ifcos_query,
        valuerange,
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


@step('All "{ifcos_query}" elements have a name given')
def step_impl(context, ifcos_query):
    eleclass_has_name_with_a_value(
        context,
        ifcos_query,
    )


@step('All "{ifcos_query}" elements have a description given')
def step_impl(context, ifcos_query):
    eleclass_has_description_with_a_value(
        context,
        ifcos_query,
    )

@step('All "{ifcos_query}" elements have a name matching the pattern "{pattern}"')
def step_impl(context, ifcos_query, pattern):
    eleclass_has_name_matching_pattern(
        context,
        ifcos_query,
        pattern,
    )


@step('There is an "{ifc_class}" element with a "{attribute_name}" attribute with a value of "{attribute_value}"')
def step_impl(context, ifc_class, attribute_name, attribute_value):
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        if hasattr(element, attribute_name) and getattr(element, attribute_name) == attribute_value:
            return
    assert False


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
        message_all_falseelems=_("All {elemcount} {ifc_class} elements in the file elements do not have a name matching {parameter}"),
        message_some_falseelems=_("{falsecount} of {elemcount} {ifc_class} do not have a name matching {parameter}: {falseelems}"),
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


def eleclass_have_class_attributes_with_a_value(
    context, ifc_class
):

    from ifcopenshell.ifcopenshell_wrapper import schema_by_name
    # schema = schema_by_name("IFC2X3")
    schema = schema_by_name(IfcStore.file.schema)
    class_attributes = []
    for cl_attrib in schema.declaration_by_name(ifc_class).all_attributes():
        class_attributes.append(cl_attrib.name())
    # print(class_attributes)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcStore.file.by_type(ifc_class)
    failed_attribs = []
    for elem in elements:
        elem_failed = False
        for cl_attrib in class_attributes:
            attrib_value = getattr(elem, cl_attrib)
            if not attrib_value:
                elem_failed = True
                failed_attribs.append(cl_attrib)
                # print(attrib_value)
        if elem_failed is True:
            context.falseelems.append(util.get_false_elem_string(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = failed_attribs

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("For all {elemcount} {ifc_class} elements at least one of these class attributes {parameter} has no value."),
        message_some_falseelems=_("For the following {falsecount} out of {elemcount} {ifc_class} elements at least one of these class attributes {parameter} has no value: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=failed_attribs
    )


def eleclass_has_name_with_a_value(context, target_ifcos_query):

    context.falseelems = []
    context.falseguids = []

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        # print(elem.Name)
        if not elem.Name or elem.Name == " ":  # leerer Name in Allplan erzeugt ein Leerzeichen, TODO siehe Material
            context.falseelems.append(util.get_false_elem_string(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    if context.falsecount > 0:
        # -- SKIP: Remaining steps in current feature.
        context.feature.skip(_("Error in eleclass_has_name_with_a_value"))

    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The name of all {elemcount} elements is not set."),
        message_some_falseelems=_("The name of {falsecount} out of {elemcount} {ifc_class} elements is not set: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )


def eleclass_has_description_with_a_value(
    context, target_ifcos_query
):

    context.falseelems = []
    context.falseguids = []

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        # print(elem.Description)
        if not elem.Description:
            context.falseelems.append(util.get_false_elem_string(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The description of all {elemcount} elements is not set."),
        message_some_falseelems=_("The description of {falsecount} out of {elemcount} {ifc_class} elements is not set: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
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
            "In the model are precisely {} {} objects available, which ist not equal {}."
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
            "In the model are precisely {} {} objects available, which ist not between {} and {}."
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
