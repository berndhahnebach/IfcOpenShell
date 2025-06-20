import ifcopenshell.util.element as eleutils

from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('All "{ifcos_query}" elements must have at least one volume quantity attached.')
def step_impl(context, ifcos_query):
    eleclass_has_volume_quantity_attached(
        context,
        ifcos_query
    )


@step('At least one "{ifcos_query}" element does have a quantity in a QSet (export setting for quantities)')
def step_impl(context, ifcos_query):
    one_ele_has_aquantity_in_aqset(
        context,
        ifcos_query,
    )


@step('All "{ifcos_query}" elements have at least one quantity in a quantity pset (all elements do have quantities exported)')
def step_impl(context, ifcos_query):
    eleclass_has_at_least_one_quantity(
        context,
        ifcos_query,
    )


@step('All "{ifcos_query}" elements do only have non-zero quantity values')
def step_impl(context, ifcos_query):
    eleclass_only_has_non_zero_quantity_values(
        context,
        ifcos_query,
    )


@step('All "{ifcos_query}" elements have a "{aqset}.{aquantity}" quantity')
def step_impl(context, ifcos_query, aqset, aquantity):
    eleclass_has_quantity_in_qset(
        context,
        ifcos_query,
        aqset,
        aquantity
    )


# pruefung from pset.property, die sollten doch gleich lauten, soweit das behave akzeptiert
# @step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" have a value range of "{valuerange}"')
# obiger wird fuer quantities so uebernommen, wenn behave das akzeptiert, ansonsten leicht abgewandelt
# aktuell brauche ich den garnicht, weiss auch grad kein use case


@step('All "{ifcos_query}" elements with "{aqset}.{aquantity}" attached do only use the value range of "{valuerange}"')
def step_impl(context, ifcos_query, aqset, aquantity, valuerange):
    eleclass_has_quantity_valuerange_of(
        context,
        ifcos_query,
        aqset,
        aquantity,
        valuerange
    )


# ************************************************************************************************
# methods
def eleclass_has_volume_quantity_attached(
    context,
    target_ifcos_query
):

    # @step('All "{ifcos_query}" elements must have at least one volume quantity attached.')
    # @step('Alle "{ifcos_query}" Bauteile haben mindestens ein Quantity Volumen angehängt.')

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    target_elements = util.minus_elems_without_quantities(target_elements)
    target_elements = util.minus_elems_without_volume(target_elements)

    for elem in target_elements:
        allqsets = IfcStore.qsets[elem.id()]
        for qset in allqsets:
            if (
                qset.endswith("Quantities")
                # and qset.startswith("Qto_")  # "MemberQuantities" hat kein "Qto_" am Anfang
            ):
                if (
                    "Nettovolumen" in allqsets[qset]
                    or "Bruttovolumen" in allqsets[qset]
                    or "GrossVolume" in allqsets[qset]
                ):
                    break
                else:
                    # Quantities in qsets, but no volumen found ... Why?
                    # print(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]))
                    # print(allqsets[qset].keys())
                    # print("Nettovolumen" in allqsets[qset])
                    pass
        else:
            context.falseelems.append(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(allqsets)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        # TODO: Translate these messages into other languages
        message_all_falseelems=_("All {elemcount} {ifc_class} elements are missing a volume quantity."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements are missing a volume quantity: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=None
    )
    # the pset name is missing in the failing message, but it is in the step test name


def one_ele_has_aquantity_in_aqset(
    context,
    target_ifcos_query,
):

    # to test CAD export options
    # @step('At least one "{ifcos_query}" element does have a quantity in a QSet (export setting for quantities)')
    # there are no false elems, not really
    # if there is no quantity at all test is False
    # if there is just one quantity in one element of all elems test is True

    def has_elem_a_qset_quantity(elem):
        qsets = IfcStore.qsets[elem.id()]
        if not qsets:
            return False
        for qset_name, qset_data in qsets.items():
            if len(qset_data) < 2:
                # qset should have at least two items, because one is the ifcid of the qset entity
                continue
            for qkey, qval in qset_data.items():
                if qkey != "id" and len(qkey) > 0:
                    print(elem)
                    print(qset_name, qkey, qval)
                    return True
        else:
            return False

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    new_target_elements = util.minus_elems_without_quantities(target_elements)
    context.elemcount = len(new_target_elements)
    if context.elemcount == 0:
        # if there is no element, test is True
        return

    for elem in new_target_elements:
        if has_elem_a_qset_quantity(elem) is True:
            break
    else:
        assert False, (_(
            "None of all {} {} elements does have at least one QSet.Quantity"
            .format(context.elemcount, target_ifcos_query)
        ))


def eleclass_has_at_least_one_quantity(
    context, target_ifcos_query
):

    # @step('All "{ifcos_query}" elements have at least one quantity in a quantity pset (all elements do have quantities exported)')

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    new_target_elements = util.minus_elems_without_quantities(target_elements)
    context.elemcount = len(new_target_elements)
    if context.elemcount == 0:
        # if there is no element, test is True
        return

    for elem in new_target_elements:
        qsets = IfcStore.qsets[elem.id()]
        if not qsets:
            context.falseelems.append(util.get_false_elem_string(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(qsets)
        else:
            pass
            # print(qsets)

    context.elemcount = len(new_target_elements)
    context.falsecount = len(context.falseguids)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} do not have at least one quantity in a QSet."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements  do not have at least one quantity in a QSet. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )
    # improve output, the qset name is missing in the failing message, but it is in the step test name


def eleclass_has_quantity_in_qset(
    context, target_ifcos_query, target_qset, target_quantity
):
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # das ist supercool mit query, bitte auch bei psets und properties !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    the_query = "{}, {}.{}>=0".format(target_ifcos_query, target_qset, target_quantity)
    quantity_elements = util.get_elems(IfcStore.file, the_query)

    for elem in list(set(target_elements) - set(quantity_elements)):
        context.falseelems.append(util.get_false_elem_string(elem))
        context.falseguids.append(elem.GlobalId)
        context.falseprops[elem.id()] = str(IfcStore.qsets[elem.id()])

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements are missing the quantity {parameter} in the QSet."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements are missing the quantity {parameter} in the QSet: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_quantity
    )
    # improve output, the qset name is missing in the failing message, but it is in the step test name


def eleclass_only_has_non_zero_quantity_values(
    context, target_ifcos_query
):

    # @step('All "{ifcos_query}" elements do only have non-zero quantity values')
    # @step('Alle "{ifcos_query}" Bauteile haben ausschliesslich Quantitywerte ungleich 0.0')

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # because of two nested loops use a function to break
    def get_zero_quantity_values(qsets):
        for qset_name, qset_data in qsets.items():
            for quantity, value in qset_data.items():
                if value == 0.0:
                    return (qset_name, quantity)
        return False
    # TODO: in obiger methode spezifische ignorieren mgl

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    # keine quantities ist kein abruch, daher keine minusobjekte
    # wenn flaechen volumen = 0 haben, sollten sie aber flaeche > 0 haben ... das pruefen ist TODO

    for elem in target_elements:
        qsets = IfcStore.qsets[elem.id()]
        is_zero_quantity = get_zero_quantity_values(qsets)
        if is_zero_quantity is not False:  # not False muss es sein, bei True werden die falschen qs zurueckgegeben
            # Workarounds ... 
            # WA1 ... Allplan exportiert runde stuetzen mit einigen zero quantities
            if (
                # U M L A U T E ...
                # habe die datei nach utf8 konvertiert, mal sehen ob sie wieder als iso kommt
                elem.is_a("IfcColumn")
                and "AllplanQuantities" in qsets
                and "Qto_ColumnBaseQuantities" in qsets
                and "ColumnQuantities" in qsets
                #
                and "Dicke" in qsets["AllplanQuantities"]
                and qsets["AllplanQuantities"]["Dicke"] == 0.0
                and "Länge" in qsets["Qto_ColumnBaseQuantities"]
                and qsets["Qto_ColumnBaseQuantities"]["Länge"] == 0.0
                #
                and "OuterSurfaceArea" in qsets["ColumnQuantities"]
                and qsets["ColumnQuantities"]["OuterSurfaceArea"] != 0.0
                and "Höhe" in qsets["AllplanQuantities"]
                and qsets["AllplanQuantities"]["Höhe"] != 0.0
                #
                and "Nettovolumen" in qsets["Qto_ColumnBaseQuantities"]
                and qsets["Qto_ColumnBaseQuantities"]["Nettovolumen"] != 0.0
                and "Bruttovolumen" in qsets["Qto_ColumnBaseQuantities"]
                and qsets["Qto_ColumnBaseQuantities"]["Bruttovolumen"] != 0.0
                and "Mantelfläche" in qsets["Qto_ColumnBaseQuantities"]
                and qsets["Qto_ColumnBaseQuantities"]["Mantelfläche"] != 0.0
                and "Querschnittsfläche" in qsets["Qto_ColumnBaseQuantities"]
                and qsets["Qto_ColumnBaseQuantities"]["Querschnittsfläche"] != 0.0
            ):
                    print("Gemaess Quantities Allplan ist ist das wohl eine runde Stuetze ... kein Fehler.")
                    print(elem)
                    continue
                    # kontrolle waere gut mit radius qs-flaeche ausrechnen
            # WA2 ... Flaechenobjekte haben Volumen 0.0 und das wird leider auch aus Allplan exportiert
            flaechenobj = False
            for no_vol_name in util.get_ele_nameparts_without_volume():
                if no_vol_name in elem.Name:
                    flaechenobj = True
                    break
            if flaechenobj is True:
                print("Gemaess Bauteilname ein Flaechenobjekt ... kein Fehler.")
                print(elem)
                # TODO: pruefe die nicht volumenquantities der flaechen
                # explit die quantities pruefen, mit rueckgabewert von is_zero_quantity
                continue
            # WA3 ... # schoeck anschluss als ifc von inet schoeck hat quantities, aber diese sind 0.0 ... 20159
            if elem.Name == "Kragplattenanschluss":
                print("Kragplattenanschluss Schoeck hat perse Nullquantities ... kein Fehler.")
                print(elem)
                # TODO: besser loesen, evtl. explit die quantities pruefen, mit rueckgabewert von is_zero_quantity
                continue
            # Alle WA End
            context.falseelems.append("{}, Zero quantity: {}.{}".format(
                util.get_false_elem_string(elem, IfcStore.psets[elem.id()]),
                is_zero_quantity[0],  # qset
                is_zero_quantity[1],  # quantity
            ))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(qsets)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseguids)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do have zero quantity values."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do have zero quantity values. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=None
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_has_quantity_valuerange_of(
    context, target_ifcos_query, target_qset, target_quantity, target_valuerange
):

    # prueft nur den wertebereich, nicht das vorhandensein
    # wenn quantity fehlt ist pruefung bestanden
    
    from ast import literal_eval
    target_py_valuerange = literal_eval(target_valuerange)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    the_query = "{}, {}.{}>=0".format(target_ifcos_query, target_qset, target_quantity)
    target_elements = util.get_elems(IfcStore.file, the_query)

    for elem in target_elements:
        qsets = IfcStore.qsets[elem.id()]
        actual_value = qsets[target_qset][target_quantity]
        # print(actual_value)

        if actual_value and (actual_value not in target_py_valuerange):
            # print("{} not in {}".format(actual_value, target_py_valuerange))
            context.falseelems.append(
                "{}, {} = {}".format(
                    util.get_false_elem_string(elem),
                    target_quantity,
                    actual_value,
                )
            )
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(actual_value)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseguids)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do not have a geometry value out of: {parameter}."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do not have the geometry value out of: {parameter}. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_py_valuerange
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name

