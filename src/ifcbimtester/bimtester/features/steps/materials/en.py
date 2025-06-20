import ifcopenshell.util.element as eleutils

from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('All "{ifc_class}" elements which have a material assigned use one of these material names "{valuerange}"')
def step_impl(context, ifc_class, valuerange):
    eleclass_has_material_valuerange_of(
        context,
        ifc_class,
        valuerange   
    )


@step('All "{ifc_class}" elements have one material assigned')
def step_impl(context, ifc_class):
    eleclass_has_one_material_assigned(
        context,
        ifc_class,
    )


@step('No "{ifc_class}" element has a material named "{material_name}"')
def step_impl(context, ifc_class, material_name):
    eleclass_has_not_a_material_with_name(
        context,
        ifc_class,
        material_name
    )


# ************************************************************************************************
# helper
def eleclass_has_material_valuerange_of(
    context, target_ifc_class, target_valuerange_str
):
    from ast import literal_eval
    target_valuerange_obj = literal_eval(target_valuerange_str)

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(target_ifc_class)
    for elem in elements:
        actual_material = eleutils.get_material(elem)
        # has to be after material test, to be sure every obj has a material name see eleclass_has_one_material_assigned
        if actual_material is None or not hasattr(actual_material, "Name"):
            continue
        elif actual_material.Name not in target_valuerange_obj:
            context.falseelems.append("{}, material name: {}".format(util.get_false_elem_string(elem), actual_material.Name))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    if context.falsecount > 0:
        # -- SKIP: Remaining steps in current feature.
        context.feature.skip(_("Error in eleclass_has_material_valuerange_of"))

    # use target_ifc_class in method parameter but ifc_class in string parameter
    util.assert_elements(
        target_ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements in the file elements do not have a material out of {parameter}"),
        message_some_falseelems=_("{falsecount} of {elemcount} {ifc_class} do not have a material out of {parameter}: {falseelems}"),
        parameter=target_valuerange_obj
    )


def eleclass_has_one_material_assigned(context, ifc_class):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        actual_material = eleutils.get_material(elem)
        # if material layer are assigned to the element the test is failed
        # the material does not have a Name attribut than
        # thus test is failed for either material is None or not hasattr
        if actual_material is None or not hasattr(actual_material, "Name"):
            context.falseelems.append(util.get_false_elem_string(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("No material has been assigned to all {elemcount} {ifc_class} elements."),
        message_some_falseelems=_("No material has been assigned to {falsecount} out of {elemcount} {ifc_class} elements: {falseelems}"),
    )


def eleclass_has_not_a_material_with_name(context, ifc_class, target_material_name):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        actual_material = eleutils.get_material(elem)
        # if there is no material the test is ok
        # if material layer are assigned to the element the test is failed
        # the material does not have a Name attribut than
        if actual_material is not None:
            if (
                not hasattr(actual_material, "Name")
                or actual_material.Name == target_material_name
            ):
                context.falseelems.append(util.get_false_elem_string(elem))
                context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements have this material name."),
        message_some_falseelems=_("{falsecount} out of {elemcount} {ifc_class} elements have this material name: {falseelems}"),
    )
