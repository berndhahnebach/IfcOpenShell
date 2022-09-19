import ifcopenshell.util.element as eleutils

from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('All "{ifc_class}" elements which have a layer assigned use one of these layer names "{valuerange}"')
def step_impl(context, ifc_class, valuerange):
    eleclass_has_layer_valuerange_of(
        context,
        ifc_class,
        valuerange   
    )


@step('All "{ifc_class}" elements have an layer assigned')
def step_impl(context, ifc_class):
    eleclass_has_layer_assigned(
        context,
        ifc_class,
    )


@step('No "{ifc_class}" element has a layer named "{layer_name}"')
def step_impl(context, ifc_class, layer_name):
    eleclass_has_not_layer_with_name(
        context,
        ifc_class,
        layer_name
    )


# ************************************************************************************************
# helper
def get_layer(elem):
    all_layer = eleutils.get_layers(IfcStore.file, elem)
    if len(all_layer) > 0:
        the_layer = all_layer[0]
    else:
        the_layer = None
    return the_layer


def eleclass_has_layer_valuerange_of(
    context, target_ifc_class, target_valuerange_str
):
    from ast import literal_eval
    target_valuerange_obj = literal_eval(target_valuerange_str)

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(target_ifc_class)
    for elem in elements:
        actual_layer = get_layer(elem)
        if actual_layer is None:
            continue
        elif actual_layer.Name not in target_valuerange_obj:
            context.falseelems.append("{}, layer name: {}".format(str(elem), actual_layer.Name))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    if context.falsecount > 0:
        # -- SKIP: Remaining steps in current feature.
        context.feature.skip(_("Error in eleclass_has_layer_valuerange_of"))

    # use target_ifc_class in method parameter but ifc_class in string parameter
    util.assert_elements(
        target_ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements in the file elements do not have a layer out of {parameter}"),
        message_some_falseelems=_("{falsecount} of {elemcount} {ifc_class} do not have a layer out of {parameter}: {falseelems}"),
        parameter=target_valuerange_obj
    )


def eleclass_has_layer_assigned(context, ifc_class):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        actual_layer = get_layer(elem)
        if actual_layer is None:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("No layer has been assigned to all {elemcount} {ifc_class} elements."),
        message_some_falseelems=_("No layer has been assigned to {falsecount} out of {elemcount} {ifc_class} elements: {falseelems}"),
    )


def eleclass_has_not_layer_with_name(context, ifc_class, target_layer_name):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        actual_layer = get_layer(elem)
        # if there is no layer the test is ok
        # if there is a layer it has to have a Name, no hasattr needed
        if actual_layer is not None and actual_layer.Name == target_layer_name:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements have this layer name."),
        message_some_falseelems=_("{falsecount} out of {elemcount} {ifc_class} elements have this layer name: {falseelems}"),
    )
