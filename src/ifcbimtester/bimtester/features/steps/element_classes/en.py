import ifcopenshell.util.element as eleutils

from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('The element "{guid}" is an "{ifc_class}" only')
def step_impl(context, guid, ifc_class):
    element = util.assert_guid(IfcStore.file, guid)
    util.assert_type(element, ifc_class, is_exact=True)


@step('The element "{guid}" is an "{ifc_class}"')
def step_impl(context, guid, ifc_class):
    element = util.assert_guid(IfcStore.file, guid)
    util.assert_type(element, ifc_class)


@step('The element "{guid}" is further defined as a "{predefined_type}"')
def step_impl(context, guid, predefined_type):
    element = util.assert_guid(IfcStore.file, guid)
    if (
        hasattr(element, "PredefinedType")
        and element.PredefinedType == "USERDEFINED"
        and hasattr(element, "ObjectType")
    ):
        util.assert_attribute(element, "ObjectType", predefined_type)
    elif hasattr(element, "PredefinedType"):
        util.assert_attribute(element, "PredefinedType", predefined_type)
    else:
        assert False, _("The element {} does not have a PredefinedType or ObjectType attribute").format(element)


@step('The element "{guid}" should not exist because "{reason}"')
def step_impl(context, guid, reason):
    try:
        element = IfcStore.file.by_id(guid)
    except:
        return
    assert False, _("This element {} should be reevaluated.").format(element)


@step('There are exclusively "{ifc_class}" elements only')
def step_impl(context, ifc_classes):
    only_eleclasses(
        context,
        ifc_classes
    )


@step('There are no "{ifc_class}" elements')
def step_impl(context, ifc_class):
    no_eleclass(
        context,
        ifc_class
    )


@step('There are no "{ifc_class}" elements because "{reason}"')
def step_impl(context, ifc_class, reason):
    no_eleclass(
        context,
        ifc_class
    )


@step('All "{ifc_class}" elements class attributes have a value')
def step_impl(context, ifc_class):
    eleclass_have_class_attributes_with_a_value(
        context,
        ifc_class
    )


@step('All "{ifc_class}" elements have a name given')
def step_impl(context, ifc_class):
    eleclass_has_name_with_a_value(
        context,
        ifc_class
    )


@step('All "{ifc_class}" elements have a description given')
def step_impl(context, ifc_class):
    eleclass_has_description_with_a_value(
        context,
        ifc_class
    )


@step('All "{ifc_class}" elements have a name matching the pattern "{pattern}"')
def step_impl(context, ifc_class, pattern):
    import re

    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        if not re.search(pattern, element.Name):
            assert False


@step('There is an "{ifc_class}" element with a "{attribute_name}" attribute with a value of "{attribute_value}"')
def step_impl(context, ifc_class, attribute_name, attribute_value):
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        if hasattr(element, attribute_name) and getattr(element, attribute_name) == attribute_value:
            return
    assert False


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


@step('All "{ifc_class}" elements have a material assigned')
def step_impl(context, ifc_class):
    eleclass_has_material_assigned(
        context,
        ifc_class,
    )


@step('No "{ifc_class}" element has a material named "{material_name}"')
def step_impl(context, ifc_class, material_name):
    eleclass_has_not_material_with_name(
        context,
        ifc_class,
        material_name
    )


# ************************************************************************************************
# helper
def get_layer(element):
    the_layer = None
    if (
        hasattr(element, "Representation")
        and hasattr(element.Representation, "Representations")
        and len(element.Representation.Representations) > 0
    ):
        all_layer = element.Representation.Representations[0].LayerAssignments
        # print("")
        # print(element)
        # print("  {}".format(element.Representation))
        # print("  {}".format(element.Representation.Representations))
        # print("  {}".format(all_layer))
        if all_layer:
            the_layer = all_layer[0]
    return the_layer


def only_eleclasses(
    context, ifc_classes
):

    context.falseelems = []
    context.falseguids = []

    # get the list of ifc_classes
    target_ifc_classes = ifc_classes.replace(" ","").split(",")
    # ToDo test if they exist in ifc standard, should be possible with ifcos

    all_elements = IfcStore.file.by_type("IfcBuildingElement")
    context.elemcount = len(all_elements)

    false_elements = []
    for elem in all_elements:
        if elem.is_a() not in target_ifc_classes:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)

    out_falseelems = "\n"
    for e in context.falseelems:
        out_falseelems += e + "\n"
    context.falsecount = len(context.falseelems)
    # print(context.falsecount)
    # print(context.elemcount)

    if context.falsecount == 0:
        return  # Test OK, thus we can not use the assert_elements method ... really ?
    elif context.falsecount == context.elemcount:
        assert False, (
            _("All {elemcount} false elements in the file are {ifc_classes}.")
            .format(
                elemcount=context.elemcount,
                ifc_classes=ifc_classes
            )
        )
    elif context.falsecount > 0 and context.falsecount < context.elemcount:
        assert False, (
            _("{falsecount} of {elemcount} false_elements are {ifc_classes} false_elements: {falseelems}")
            .format(
                falsecount=context.falsecount,
                elemcount=context.elemcount,
                ifc_classes=ifc_classes,
                falseelems=out_falseelems,
            )
        )
    else:
        assert False, _("Error in falsecount, something went wrong.")


def no_eleclass(
    context, ifc_class
):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    context.elemcount = len(IfcStore.file.by_type("IfcBuildingElement"))
    for elem in elements:
        context.falseelems.append(str(elem))
        context.falseguids.append(elem.GlobalId)

    out_falseelems = "\n"
    for e in context.falseelems:
        out_falseelems += e + "\n"
    context.falsecount = len(context.falseelems)
    # print(context.falsecount)
    # print(context.elemcount)

    if context.falsecount == 0:
        return  # Test OK, thus we can not use the assert_elements method ... really ?
    elif context.falsecount == context.elemcount:
        assert False, (
            _("All {elemcount} elements in the file are {ifc_class}.")
            .format(
                elemcount=context.elemcount,
                ifc_class=ifc_class
            )
        )
    elif context.falsecount > 0 and context.falsecount < context.elemcount:
        assert False, (
            _("{falsecount} of {elemcount} elements are {ifc_class} elements: {falseelems}")
            .format(
                falsecount=context.falsecount,
                elemcount=context.elemcount,
                ifc_class=ifc_class,
                falseelems=out_falseelems,
            )
        )
    else:
        assert False, _("Error in falsecount, something went wrong.")


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
    for elem in elements:
        failed_attribs = []
        elem_failed = False
        for cl_attrib in class_attributes:
            attrib_value = getattr(elem, cl_attrib)
            if not attrib_value:
                elem_failed = True
                failed_attribs.append(cl_attrib)
                # print(attrib_value)
        if elem_failed is True:
            context.falseelems.append(str(elem))
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


def eleclass_has_name_with_a_value(context, ifc_class):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        # print(elem.Name)
        if not elem.Name:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
 
    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The name of all {elemcount} {elemcount} elements is not set."),
        message_some_falseelems=_("The name of {falsecount} out of {elemcount} {ifc_class} elements is not set: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )


def eleclass_has_description_with_a_value(
    context, ifc_class
):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        # print(elem.Description)
        if not elem.Description:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
 
    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The description of all {elemcount} {elemcount} elements is not set."),
        message_some_falseelems=_("The description of {falsecount} out of {elemcount} {ifc_class} elements is not set: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )


def eleclass_has_layer_assigned(context, ifc_class):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        # the_layer = None
        # all_layer = eleutils.get_layers(elem, IfcStore.file)
        # print(elem)
        # print(IfcStore.file)
        # print(all_layer)
        # if len(all_layer) > 0:
        #     the_layer = all_layer[0]
        the_layer = get_layer(elem)
        if the_layer is None:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("No layer has been assigned to all {elemcount} {elemcount} elements."),
        message_some_falseelems=_("No layer has been assigned to {falsecount} out of {elemcount} {ifc_class} elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )


def eleclass_has_not_layer_with_name(context, ifc_class, target_layer_name):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        # layer = eleutils.get_layer(elem)
        layer = get_layer(elem)
        if layer.Name == target_layer_name:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {elemcount} element have assigned this layer."),
        message_some_falseelems=_("{falsecount} out of {elemcount} {ifc_class} elements have assigned this layer: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )


def eleclass_has_material_assigned(context, ifc_class):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        material = eleutils.get_material(elem)
        # file mit material layer, material ist kein IfcMaterial und hat daher kein Attribut Name
        if material is None or not hasattr(material, "Name"):
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("No material has been assigned to all {elemcount} {elemcount} elements."),
        message_some_falseelems=_("No material has been assigned to {falsecount} out of {elemcount} {ifc_class} elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )


def eleclass_has_not_material_with_name(context, ifc_class, target_material_name):

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        material = eleutils.get_material(elem)
        # file mit material layer, material ist kein IfcMaterial und hat daher kein Attribut Name
        if hasattr(material, "Name") and material.Name == target_material_name:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {elemcount} element have assigned this material."),
        message_some_falseelems=_("{falsecount} out of {elemcount} {ifc_class} elements have assigned this material: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )
