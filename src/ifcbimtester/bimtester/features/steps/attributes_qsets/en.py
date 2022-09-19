import ifcopenshell.util.element as eleutils

from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('All "{ifc_class}" elements have a "{aqset}.{aquantity}" quantity')
def step_impl(context, ifc_class, aqset, aquantity):
    eleclass_has_quantity_in_qset(
        context,
        ifc_class,
        aqset,
        aquantity
    )
"""
# TODO: use get_psets from ifcopenshell.util.element, oder besser noch IfcStore
@step('All "{ifc_class}" elements have a "{qto_name}.{quantity_name}" quantity')
def step_impl(context, ifc_class, qto_name, quantity_name):
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        is_successful = False
        if not element.IsDefinedBy:
            assert False
        for relationship in element.IsDefinedBy:
            if relationship.RelatingPropertyDefinition.Name == qto_name:
                for quantity in relationship.RelatingPropertyDefinition.Quantities:
                    if quantity.Name == quantity_name:
                        is_successful = True
        if not is_successful:
            assert False
"""


@step('All "{ifc_class}" elements made from material "{material}" do only have the "{geometryproperty}" value range "{valuerange}" meter')
def step_impl(context, ifc_class, material, geometryproperty, valuerange):
    eleclass_material_has_quantity_valuerange_of(
        context,
        ifc_class,
        material,
        geometryproperty,
        valuerange
    )


@step('All "{ifc_classes_string}" elements have at least one quantity in a quantity pset exported (IFC-export with quantities)')
def step_impl(context, ifc_classes_string):
    eleclass_has_at_least_one_quantity(
        context,
        ifc_classes_string,
    )


# ************************************************************************************************
# helper
def eleclass_material_has_quantity_valuerange_of(
    context, ifc_class, material, target_quantity, target_valuerange
):

    # TODO vorher test auf quantitybase set und dickenattribut

    # waende backstein nur 12.5, 15, 17.5, 20 cm dick
    # wanddicke koennte auch aus geometrie kommen und nicht aus quantity

    from ast import literal_eval
    target_py_valuerange = literal_eval(target_valuerange)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # evtl. Ausgabe Anzahl elem und Anzahl elem die das attribut ueberhaupt angehaengt haben
    # Anzahl attrib macht keinen sinn wegen schichtattribute

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:

        # file mit material layer, material ist kein IfcMaterial und hat daher kein Attribut Name
        # continue wenn material kein name attribut, das muss woanders aufgefangen werden
        mat = eleutils.get_material(elem)
        if not hasattr(mat, "Name") or mat.Name != material:
            continue

        actual_value = None
        qsets = IfcStore.qsets[elem.id()]
        for qset_name, qset_data in qsets.items():
            if "Base" not in qset_name:
                continue
            for quantity, value in qset_data.items():
                if quantity == target_quantity:
                    actual_value = value
                    break
            else:
                print("{} missing for Bauteil: {}".format(target_quantity, elem))
        # print(actual_value)

        if actual_value and (actual_value not in target_py_valuerange):
            # print("{} not in {}".format(actual_value, target_py_valuerange))
            context.falseelems.append(
                "{}, {}, {} = {}, targetrange eval = {}"
                .format(elem, material, target_quantity, actual_value, target_py_valuerange)
            )
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(actual_value)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseguids)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do not have a geometry value out of: {parameter}."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do not have the geometry value out of: {parameter}. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_py_valuerange
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_has_at_least_one_quantity(
    context, ifc_classes_string
):

    ifc_classes_list = util.extract_ifc_classes(context, ifc_classes_string)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    all_elements = []
    for a_ifc_class in ifc_classes_list:
        class_elements = IfcStore.file.by_type(a_ifc_class)
        all_elements += class_elements
        for elem in class_elements:
            qsets = IfcStore.qsets[elem.id()]
            if not qsets:
                context.falseelems.append(str(elem))
                context.falseguids.append(elem.GlobalId)
                context.falseprops[elem.id()] = str(qsets)
            else:
                pass
                # print(qsets)

    context.elemcount = len(all_elements)
    context.falsecount = len(context.falseguids)
    util.assert_elements(
        ifc_classes_string,  # ifc_classes_string, but in strinngs should be ifc_class !
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} do not have at least one quantity in a QSet."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements  do not have at least one quantity in a QSet. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )
    # improve output, the qset name is missing in the failing message, but it is in the step test name


def eleclass_has_quantity_in_qset(
    context, ifc_class, target_qset, target_quantity
):
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        allqsets = IfcStore.qsets[elem.id()]
        if target_qset not in allqsets:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(allqsets)
            continue
        actual_qset = allqsets[target_qset]
        if target_quantity not in actual_qset:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(allqsets)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements are missing the quantity {parameter} in the QSet."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements are missing the quantity {parameter} in the QSet: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_quantity
    )
    # improve output, the qset name is missing in the failing message, but it is in the step test name
