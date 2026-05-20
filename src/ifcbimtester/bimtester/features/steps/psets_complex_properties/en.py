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
from behave import use_step_matcher

from bimtester import helpertools
from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('At least one "{ifcos_query}" element is a "{geom_typ}" and has no "{prop_typ}" (element layer properties)')
def step_impl(context, ifcos_query, geom_typ, prop_typ):
    one_ifcosquery_ele_has_no_complex_property(
        context,
        ifcos_query,
        geom_typ,
        prop_typ,
    )

@step('All "{ifcos_query}" elements have no element layer properties (IfcComplexProperty)')
def step_impl(context, ifcos_query):
    eleclass_has_no_complex_property(
        context,
        ifcos_query,
    )


# ************************************************************************************************
# helper

def is_geom_type(elem, geom_type):
    
    # especially for TRW ifc exported from allplan and modelled by FBJ
    # may be move to FreeCAD somewhere to make it available all the time

    if not elem.Representation:
        return False
    if not elem.Representation.Representations:
        return False
    # print(elem.Representation.Representations[0])
    # mapped items will be ignored here
    # 95% der waende sind "SweptSolid" --> IfcExtrudedAreaSolid
    # es gibt noch "Brep" --> IfcFacetedBrep und "Clipping" --> IfcBooleanClippingResult
    if not elem.Representation.Representations[0].Items:
        print("No items")
        print(elem.Representation.Representations[0])
        return False
    actual_geom_typ = elem.Representation.Representations[0].Items[0]
    if not actual_geom_typ.is_a() == geom_type:
        print("No {}, but: {}".format(geom_type, actual_geom_typ.is_a()))
        # print(actual_geom_typ)
        return False
    # found a geom_type
    return True


def one_ifcosquery_ele_has_no_complex_property(
    context, target_ifcos_query, target_geom_typ, target_prop_typ,
):

    #* Mindestens ein "IfcWall" Bauteil ist ein "IfcExtrudedAreaSolid" und hat keine "IfcComplexProperty" (Bauteilschichtattribute) angehängt
    #
    # eine Wand die kein brep ist und keine Complex Attriubte hat ... gibt es nur wenn Einstellung richtig ... dann test ok
    # wenn im modell keine wand, oder alle waende breps sind, dann ist test auch ok

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    context.elemcount = len(target_elements)

    found_a_elem_to_test = False
    for elem in target_elements:
        if is_geom_type(elem, target_geom_typ) is False:  # mainly IfcExtrudedAreaSolid
            continue
        found_a_elem_to_test = True
        # first found geom_type :-)
        # if the first geom_type has NO complex attribts --> test is passed
        if has_elem_complex_props(elem) is False:
            break
    else:
        if found_a_elem_to_test is False:
            # if there is no elem in target_elements or if there is non of the geom_type
            # Test is True
            # means if there is no element to test, the test should not fail, thus return
            return
        assert False, (_(
            "None of all {} {} {} geom elements and has NO {} (element layer properties)"
            .format(context.elemcount, target_ifcos_query, target_geom_typ, target_prop_typ)
        ))


def eleclass_has_no_complex_property(
    context, target_ifcos_query
):
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        if has_elem_complex_props(elem) is True:
            context.falseelems.append("{}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()])))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)

    if context.falsecount > 0:
        # -- SKIP: Remaining steps in current feature.
        context.feature.skip(_("Objects with material layer are not allowed. Split these material layer."))

    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements have complex properties."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements have complex properties: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )


def eleclass_without_complexlayerattributes_has_property(
    context, target_ifcos_query, target_pset, target_property
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get elements without complex layer properties in all psets
    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    elements = []
    for elem in target_elements:
        if has_elem_complex_props(elem) is False:
            elements.append(elem)

    # check if they have the attribute
    for elem in elements:
        ele_allpsets = IfcStore.psets[elem.id()]
        actual_pset = ele_allpsets[target_pset]  # was wenn pset nicht vorhanden dann error
        if target_property not in actual_pset:
            context.falseelems.append("{}".format(util.get_false_elem_string(elem, ele_allpsets)))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(ele_allpsets)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements without complex layer attributes are missing the property {parameter} in the pset."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements without complex layer attributes are missing the property {parameter} in the pset: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements without complex properties in the IFC file."),
        parameter=target_property
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_with_complexlayerattributes_has_property(
    context, target_ifcos_query, target_pset, target_property
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get elements with complex layer properties in all psets
    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    elements = []
    for elem in target_elements:
        if has_elem_complex_props(elem) is True:
            elements.append(elem)

    # check if they have the attribute
    for elem in elements:
        ele_allpsets = IfcStore.psets[elem.id()]
        actual_pset = ele_allpsets[target_pset]  # was wenn pset nicht vorhanden dann error
        if target_property not in actual_pset:
            context.falseelems.append("{}".format(util.get_false_elem_string(elem, ele_allpsets)))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(ele_allpsets)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements with complex layer attributes are missing the property {parameter} in the pset."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements with complex layer attributes are missing the property {parameter} in the pset: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements with complex properties in the IFC file."),
        parameter=target_property
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_with_complexlayerattributes_has_property_in_all_layer(
    context, target_ifcos_query, target_pset, target_property
):
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get elements with complex layer properties in at least one psets
    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    elements = []
    for elem in target_elements:
        if has_elem_complex_props(elem) is True:
            elements.append(elem)

    # check if they have the property in each complex layer
    for elem in elements:
        ele_allpsets = IfcStore.psets[elem.id()]
        actual_pset = ele_allpsets[target_pset]  # was wenn pset nicht vorhanden dann error
        complex_props = get_complex_props(actual_pset)
        # check if the target_pset has complex properties
        if len(complex_props) == 0:
            context.falseelems.append("{}".format(util.get_false_elem_string(elem, ele_allpsets)))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(ele_allpsets)
        #for complex_prop in complex_props

    """
        **********************!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        property should be in ALL complex layer
        if target_property in actual_pset:
            context.falseelems.append("{}".format(util.get_false_elem_string(elem, ele_allpsets)))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(ele_allpsets)
    """

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements with complex layer attributes are missing the property {parameter} in the pset and in the complex layer."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements with complex layer attributes are missing the property {parameter} in the pset and in the complex layer: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements with complex properties in the IFC file."),
        parameter=target_property
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


# ***************************************************************************************
# helper, may be move into separate module
# ***************************************************************************************
def has_elem_complex_props(elem):
    # if one pset (no matter which) has complex props True will be returned
    ele_allpsets = IfcStore.psets[elem.id()]
    for pset in ele_allpsets:
        for key in ele_allpsets[pset].keys():
            if is_complex_prop(key):
                return True
    return False


def is_complex_prop(attribkey):
    # TODO in all methods use this method to find complex props
    # if the key once changes it will be easy to adapt the code
    if 'Object Layer Attributes' in attribkey:
        return True
    return False


def get_complex_props(pset):
    # TODO in all methods use this method to get complex props
    # if the key once changes it will be easy to adapt the code
    complex_props = []
    for key in pset.keys():
        if is_complex_prop(key):
            complex_props.append(pset[key]["properties"])
    return complex_props




# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************
# evtl. ungueltig, nicht funktinierend, veraltet
# ***************************************************************************************
# ***************************************************************************************
def eleclass_has_property_directly_in_pset(
    context, ifc_class, target_pset, target_property
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        found, actual_value, actual_datatype = find_property_directly(elem, target_pset, target_property)
        if found is False:
            context.falseelems.append("{}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()])))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements are missing the property {parameter} in the pset."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements are missing the property {parameter} in the pset: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_property
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_has_not_property_directly_in_pset(
    context, ifc_class, target_pset, target_property
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        found, actual_value, actual_datatype = find_property_directly(elem, target_pset, target_property)
        if found is True:
            context.falseelems.append("{}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()])))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements diretly have the property {parameter} in the pset."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements diretly have the property {parameter} in the pset: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_property
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_has_property_in_layer_in_pset(
    context, ifc_class, target_pset, target_property
):

    # property has to be in the layer not directly at the element

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        found, actual_value, actual_datatype = find_property_elemlayer(elem, target_pset, target_property)
        if found is False:
            context.falseelems.append("{}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()])))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements are missing the property {parameter} in the pset."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements are missing the property {parameter} in the pset: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_property
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def find_property_both(aelem, target_pset, target_property):
    """
    return True if the property is directly attached to the element
    or if the property is attached to a element layer by complex property
    (True or False, value, value data type)
    we need to return True or False because None is a valid property value
    """
    # it could be on Gsamtwand and each Wandlayer
    # returned will be the value on the first found Wandlayer
    # the gesamtwand attrib value will be overwritten
    # idee: tuple mit allen attibuten wird zurueckgegeben
    # auch an jeder Schicht und Gesamtwand koennte ein identisches Attribut doppelt sein
    # dies dann mit identischen oder auch unterschiedlichen attributwerten
    # das koennte mit einem tupel auch gefunden und zurueckgegeben werden

    # wenn pset zweimal vorhanden ist, oder wenn attribut zweimal in einer schicht oder direkt ist wird das nicht gefunden
    # wobei das waere meines erachtens ein fehler weil doppelattribut, eigener test

    # heisst attribut kann direkt und aber auch in jeder schicht vorkommen, dann doch sehr viele male

    props = []
    found = False  # actual_value could be None in ifc
    actual_value = None
    actual_propertytype = None
    ele_allpsets = IfcStore.psets[elem.id()]
    if target_pset in ele_allpsets:
        actual_pset = ele_allpsets[target_pset]
        if target_property in actual_pset:
            found = True  # do not use continue, pset could not exist
            actual_value = actual_pset[target_property]
            actual_propertytype = helpertools.get_value_type(actual_value)
            props.append((actual_value, actual_propertytype))
        for key, val in actual_pset.items():
            if 'Object Layer Attributes' in key:
                if 'properties' in val:
                    if target_property in val['properties']:
                        found = True
                        actual_value = val['properties'][target_property]
                        actual_propertytype = helpertools.get_value_type(actual_value)
                        props.append((actual_value, actual_propertytype))
    # TODO and FIXME, get the data type from ifc data directly
    # gib das erste property zurueck
    return found, props[0][0], props[0][1]
    #return props


def find_property_directly(aelem, target_pset, target_property):
    """
    return True if the property is directly attached to the element
    (True or False, value, value data type)
    we need to return True or False because None is a valid property value
    """
    # sofort bei ersten finden return
    found = False
    actual_value = None
    actual_propertytype = None
    ele_allpsets = IfcStore.psets[elem.id()]
    if target_pset in ele_allpsets:
        actual_pset = ele_allpsets[target_pset]
        if target_property in actual_pset:
            found = True
            actual_value = actual_pset[target_property]
            actual_propertytype = helpertools.get_value_type(actual_value)
            return (found, actual_value, actual_propertytype)
    return (found, actual_value, actual_propertytype)


def find_property_elemlayer(aelem, target_pset, target_property):
    """
    return True if the property is attached to a element layer by complex property
    (True or False, value, value data type)
    we need to return True or False because None is a valid property value
    """
    # it could be on each Wandlayer
    # returned will be the value on the first found Wandlayer
    # FIXME see find_property_directly
    # Attribut muss in jeder Schicht vorkommen!
    actual_value = None
    found = False
    ele_allpsets = IfcStore.psets[elem.id()]
    if target_pset in ele_allpsets:
        actual_pset = ele_allpsets[target_pset]
        for key, val in actual_pset.items():
            if 'Object Layer Attributes' in key:
                if 'properties' in val:
                    if target_property in val['properties']:
                        actual_value = val['properties'][target_property]
                        found = True
                        break
    actual_propertytype = helpertools.get_value_type(actual_value)
    # TODO and FIXME, get the data type from ifc data directly
    return (found, actual_value, actual_propertytype)


def eleclass_matlayer_has_property_in_pset(
    context, ifc_class, target_pset, target_property
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        found, actual_value, actual_datatype = find_property_directly(elem, target_pset, target_property)
        if found is True:
            context.falseelems.append("{}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()])))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements diretly have the property {parameter} in the pset."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements diretly have the property {parameter} in the pset: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_property
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name
