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

import ifcopenshell.util.element as eleutils

from behave import step
from behave import use_step_matcher

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('All "{ifcos_query}" elements have exactly "{attribut_count}" in the pset "{pset}"')
def step_impl(context, ifcos_query, attribut_count, pset):
    eleclass_has_propertycount_in_pset(
        context,
        ifcos_query,
        attribut_count,
        pset
    )


@step('All "{ifcos_query}" elements have an "{aproperty}" property in the "{pset}" pset')
def step_impl(context, ifcos_query, pset, aproperty):
    eleclass_has_property_in_pset(
        context,
        ifcos_query,
        pset,
        aproperty
    )


@step('All "{ifcos_query}" elements have a "{pset}.{aproperty}" property')
def step_impl(context, ifcos_query, pset, aproperty):
    eleclass_minus_has_property_in_pset(
        context,
        ifcos_query,
        pset,
        aproperty
    )


@step('All "{ifcos_query}" elements have not a "{pset}.{aproperty}" property')
def step_impl(context, ifcos_query, pset, aproperty):
    eleclass_minus_has_not_property_in_pset(
        context,
        ifcos_query,
        pset,
        aproperty
    )


@step('All "{ifcos_querye}" elements have a property "{aproperty}" in the Common pset')
def step_impl(context, ifcos_querye, aproperty):
    eleclass_has_property_in_common_pset(
        context,
        ifcos_query,
        aproperty,
    )


@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" are of type "{propertytyp}"')
def step_impl(context, ifcos_query, pset, aproperty, propertytyp):
    eleclass_has_propertytype_of(
        context,
        ifcos_query,
        pset,
        aproperty,
        propertytyp
    )


@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" have a value of "{propertyvalue}"')
def step_impl(context, ifcos_query, pset, aproperty, propertyvalue):
    eleclass_has_propertyvalue_of(
        context,
        ifcos_query,
        pset,
        aproperty,
        propertyvalue
    )


@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" do not have a value of "{propertyvalue}"')
def step_impl(context, ifcos_query, pset, aproperty, propertyvalue):
    eleclass_not_has_propertyvalue_of(
        context,
        ifcos_query,
        pset,
        aproperty,
        propertyvalue 
    )


@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" have a value range of "{valuerange}"')
def step_impl(context, ifcos_query, pset, aproperty, valuerange):
    eleclass_has_property_valuerange_of(
        context,
        ifcos_query,
        pset,
        aproperty,
        valuerange
    )


@step('All "{ifcos_query}" elements  with a "{pset}.{aproperty}" have a value matching the pattern "{pattern}"')
def step_impl(context, ifcos_query, pset, aproperty, pattern):
    eleclass_has_property_value_matching_pattern(
        context,
        ifcos_query,
        pset,
        aproperty,
        pattern,
    )


@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" have a attribute value out of value range. All items of value range have been used "{valuerange}"')
def step_impl(context, ifcos_query, pset, aproperty, valuerange):
    eleclass_has_property_valuerange_of(
        context,
        ifcos_query,
        pset,
        aproperty,
        valuerange,
        all_valuerangeitems_must_be_used=True
    )


@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" have the chars "{some_chars}" not in the property value"')
def step_impl(context, ifcos_query, pset, aproperty, some_chars):
    eleclass_hasnot_chars_in_property_value(
        context,
        ifcos_query,
        pset,
        aproperty,
        some_chars
    )


@step('The attribute value of "{pset1}.{aproperty1}" equals the attribute value of "{pset2}.{aproperty2}" if both are given')
def step_impl(context, pset1, aproperty1, pset2, aproperty2):
    propertyvalue1_equals_propertyvalue2(
        context,
        pset1,
        aproperty1,
        pset2,
        aproperty2
    )


@step('The attribute value of "{pset}.{aproperty}" equals the class attribute Name')
def step_impl(context, pset, aproperty):
    propertyvalue1_equals_elementclassname(
        context,
        pset,
        aproperty
    )


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


# attributs dependend from material
# do not use anymore, use ifcos filter instead
@step('All "{ifcos_query}" elements with the material named "{material}" have a "{pset}.{property}" property')
def step_impl(context, ifcos_query, material, pset, property):
    eleclass_with_material_has_property_in_pset(
        context,
        ifcos_query,
        material,
        pset,
        property
    )


@step('All "{ifcos_query}" elements which do not have a material named "{material}" have not a "{pset}.{property}" property')
def step_impl(context, ifcos_query, material, pset, property):
    eleclass_with_not_material_has_not_property_in_pset(
        context,
        ifcos_query,
        material,
        pset,
        property
    )


"""
# elseclass properties, see other module ... 
@step('All "{ifc_class}" elements with the property "{pset}.{aproperty}" should have the value of "{value}"')
def step_impl(context, ifc_class, pset, aproperty, value):
    eleclass_has_property_value_of(
        context,
        ifc_class,
        pset,
        aproperty,
        value
    )


@step('All "{ifc_class}" elements with the property "{pset}.{aproperty}" should have the value type of "{valuetype}"')
def step_impl(context, ifc_class, pset, aproperty, valuetype):
    eleclass_has_property_valuetype_of(
        context,
        ifc_class,
        pset,
        aproperty,
        valuetype
    )
"""


# ------------------------------------------------------------------------
# STEPS with Regular Expression Matcher ("re")
# ------------------------------------------------------------------------
use_step_matcher("re")


@step("all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property")
def step_impl(context, ifc_class, property_path):
    pset_name, property_name = property_path.split(".")
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        if not IfcStore.get_property(element, pset_name, property_name):
            assert False


@step(
    'all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property value matching the pattern "(?P<pattern>.*)"'
)
def step_impl(context, ifc_class, property_path, pattern):
    import re

    pset_name, property_name = property_path.split(".")
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        prop = IfcStore.get_property(element, pset_name, property_name)
        if not prop:
            assert False
        # For now, we only check single values
        if prop.is_a("IfcPropertySingleValue"):
            if not (prop.NominalValue and re.search(pattern, prop.NominalValue.wrappedValue)):
                assert False



# ************************************************************************************************
# helper

def eleclass_has_property_value_matching_pattern(
    context, target_ifcos_query, target_pset, target_property, target_pattern
):

    import re

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        propvaltyps = get_prop_values_and_types(elem, target_pset, target_property)
        # print("")
        # print(elem)
        # print(propvaltyps)
        if len(propvaltyps) == 0:
            print("Either prop or pset or value not found, which is not a failing test.")
            continue
        elif len(propvaltyps) > 1:
            print("Property more than once. Not handled case.")
            context.falseelems.append("{}, prop more than once on elem: {}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]), propvaltyps))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])
            continue
        elif len(propvaltyps) == 1:
            # print("Found one property value with type :-)")
            actual_value, actual_propertytype = propvaltyps[0]
        # print(actual_value)
        # print(actual_propertytype)
        # print(target_pattern, flush=True)
        if not re.search(target_pattern, actual_value):
            context.falseelems.append("{}, {}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]), actual_value))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseguids)

    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do not have the property value pattern: {parameter}."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do not have the property value pattern: {parameter}. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_pattern
    )


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
            context.falseelems.append(str(elem))
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


def eleclass_minus_has_property_in_pset(
    context, target_ifcos_query, target_pset, target_property, minus_ifc_class=""
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get the elements
    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    elements = []
    if minus_ifc_class == "":
        elements = target_elements
    else:
        minus_elements = IfcStore.file.by_type(minus_ifc_class)
        for elem in target_elements:
            if elem not in minus_elements:
                 elements.append(elem)

    # check if they have the attribute
    for elem in elements:
        allpsets = IfcStore.psets[elem.id()]
        if target_pset not in allpsets:
            context.falseelems.append(util.get_false_elem_string(elem, allpsets))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(allpsets)
            continue
        actual_pset = allpsets[target_pset]
        if target_property not in actual_pset:
            context.falseelems.append(util.get_false_elem_string(elem, allpsets))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(allpsets)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements are missing the property {parameter} in the PSet."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements are missing the property {parameter} in the PSet: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_property
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_minus_has_not_property_in_pset(
    context, target_ifcos_query, target_pset, target_property, minus_ifc_class=""
):
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get the elements
    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    elements = []
    if minus_ifc_class == "":
        elements = target_elements
    else:
        minus_elements = IfcStore.file.by_type(minus_ifc_class)
        for elem in target_elements:
            if elem not in minus_elements:
                 elements.append(elem)

    # check if they have not the attribute
    for elem in elements:
        allpsets = IfcStore.psets[elem.id()]
        if target_pset not in allpsets:
            continue
        actual_pset = allpsets[target_pset]
        if target_property in actual_pset:
            context.falseelems.append(util.get_false_elem_string(elem, allpsets))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(allpsets)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements have the property {parameter} in the PSet."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements have the property {parameter} in the PSet: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_property
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_has_property_in_common_pset(
    context, target_ifcos_query, target_property
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        psets = IfcStore.psets[elem.id()]
        target_pset_name = util.get_common_pset_name(a_ifc_class)
        if target_pset_name not in psets:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(psets)
            continue
        actual_pset = psets[target_pset_name]
        if target_property not in actual_pset:
            context.falseelems.append(util.get_false_elem_string(elem, psets))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(psets)
        # print(psets[target_pset_name][target_property])

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements are missing the property {parameter} in the Common pset."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements are missing the property {parameter} in the Common pset: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_property
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name



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
        psets = IfcStore.psets[elem.id()]
        actual_pset = psets[target_pset]  # was wenn pset nicht vorhanden dann error
        if target_property not in actual_pset:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(psets)

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
        psets = IfcStore.psets[elem.id()]
        actual_pset = psets[target_pset]  # was wenn pset nicht vorhanden dann error
        if target_property not in actual_pset:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(psets)

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
        psets = IfcStore.psets[elem.id()]
        actual_pset = psets[target_pset]  # was wenn pset nicht vorhanden dann error
        complex_props = get_complex_props(actual_pset)
        # check if the target_pset has complex properties
        if len(complex_props) == 0:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(psets)
        #for complex_prop in complex_props

    """
        **********************!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        property should be in ALL complex layer
        if target_property in actual_pset:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(psets)
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


def eleclass_has_propertytype_of(
    context, target_ifcos_query, target_pset, target_property, target_propertytype
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # evtl. Ausgabe Anzahl elem und Anzahl elem die das attribut ueberhaupt angehaengt haben
    # Anzahl attrib macht keinen sinn wegen schichtattribute

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        elem_has_false_prop = False
        for propvaltyp in get_prop_values_and_types(elem, target_pset, target_property):
            if propvaltyp == []:
                # elem does not have this property attached
                continue
            actual_value, actual_propertytype = propvaltyp
            if actual_propertytype != target_propertytype:
                # print("{} is not value type {}".format(actual_value, target_propertytype))
                # ein elem koennte mehrmals ein False value type haben
                # das attribut kann in Schichten vorkommen
                # das attribut kann doppelt vorhanden sein (waere falsch, aber moeglich)
                # daher kann ein elem mehrmals zu falseelems hinzugefuegt werden
                elem_has_false_prop = True
                context.falseelems.append("{}, {}.{} = {}, {}:".format(
                    util.get_false_elem_string(elem, IfcStore.psets[elem.id()]),
                    target_pset,
                    target_property,
                    actual_value,
                    actual_propertytype
                    ))
        if elem_has_false_prop is True:
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseguids)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do not have the property value type: {parameter}."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do not have the property value type: {parameter}. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_propertytype
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_has_propertyvalue_of(
    context, target_ifcos_query, target_pset, target_property, target_value
):

    # print(target_value)
    # der wert innerhalb der "" wird an literal_eval uebergeben, daher "'ein wert'" in definition der pruefung
    if not target_value.startswith("'"):
        assert False, "The target value {} could not be evaluated. The target value should start with '. Example \"'A_Value'\"".format(target_value)
    from ast import literal_eval
    target_py_value = literal_eval(target_value)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # evtl. Ausgabe Anzahl elem die das attribut ueberhaupt angehaengt haben
    # Anzahl attrib macht keinen sinn wegen schichtattribute

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        elem_has_false_prop = False
        for propvaltyp in get_prop_values_and_types(elem, target_pset, target_property):
            if propvaltyp == []:
                # elem does not have this property attached
                continue
            actual_value, actual_propertytype = propvaltyp
            if actual_value != target_py_value:
                # print("{} != {}".format(actual_value, target_py_value))
                # ein elem koennte mehrmals ein False value type haben
                # das attribut kann in Schichten vorkommen
                # das attribut kann doppelt vorhanden sein (waere falsch, aber moeglich)
                # daher kann ein elem mehrmals zu falseelems hinzugefuegt werden
                elem_has_false_prop = True
                context.falseelems.append(
                    "{}, {}.{} = {} ({}), targettype eval = {}:"
                    .format(
                        util.get_false_elem_string(elem, IfcStore.psets[elem.id()]),
                        target_pset, target_property,
                        actual_value,
                        actual_propertytype,
                        type(target_py_value)
                    )
                )
        if elem_has_false_prop is True:
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseguids)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do not have the property value: {parameter}."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do not have the property value: {parameter}. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_value
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_not_has_propertyvalue_of(
    context, target_ifcos_query, target_pset, target_property, target_value
):

    # print(target_value)
    # der wert innerhalb der "" wird an literal_eval uebergeben, daher "'ein wert'" in definition der pruefung
    if not target_value.startswith("'"):
        assert False, "The target value {} could not be evaluated. The target value should start with '. Example \"'A_Value'\"".format(target_value)
    from ast import literal_eval
    target_py_value = literal_eval(target_value)
    print(target_py_value)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        elem_has_target_prop_value = False
        for propvaltyp in get_prop_values_and_types(elem, target_pset, target_property):
            if propvaltyp == []:
                # elem does not have this property attached
                continue
            actual_value, actual_propertytype = propvaltyp
            if actual_value == target_py_value:
                # print("{} == {}".format(actual_value, target_py_value))
                # siehe hinweise bei eleclass_has_propertyvalue_of
                elem_has_target_prop_value = True
                context.falseelems.append(
                    "{}, {}.{} = {} ({}), targettype eval = {}:"
                    .format(
                        util.get_false_elem_string(elem, IfcStore.psets[elem.id()]),
                        target_pset,
                        target_property,
                        actual_value,
                        actual_propertytype,
                        type(target_py_value)
                    )
                )
        if elem_has_target_prop_value is True:
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseguids)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do have the property value: {parameter}."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do have the property value: {parameter}. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_value
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_has_property_valuerange_of(
    context, target_ifcos_query, target_pset, target_property, target_valuerange, all_valuerangeitems_must_be_used=False
):

    # make the test fail if a value of the range is not attached to any object
    # the other way around, all values of range must have been used on at least one object to pass the test
    # may be it makes senst to have one test which has this requirement and one test which does not have
    # satzbau wird interessant, da all dies eindeutig in sprache ausgedrÃ¼ckt werden muss

    # print(target_valuerange)
    # der wert innerhalb der "" wird an literal_eval uebergeben, daher "['ein wert', 'weiterer wert']" in definition der pruefung
    if not target_valuerange.startswith("["):
        assert False, "The target value {} could not be evaluated. The target value should start with '. Example \"['a_value', another_value']\"".format(target_valuerange)
    from ast import literal_eval
    target_py_valuerange = literal_eval(target_valuerange)
    actual_py_valuerange =  []

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        elem_has_false_prop = False
        for propvaltyp in get_prop_values_and_types(elem, target_pset, target_property):
            if propvaltyp == []:
                # elem does not have this property attached
                continue
            actual_value, actual_propertytype = propvaltyp
            if actual_value in target_py_valuerange:
                if actual_value not in actual_py_valuerange:
                    actual_py_valuerange.append(actual_value)
            else:
                # print("{} not in {}".format(actual_value, target_py_valuerange))
                # ein elem koennte mehrmals ein False value type haben
                # das attribut kann in Schichten vorkommen
                # das attribut kann doppelt vorhanden sein (waere falsch, aber moeglich)
                # daher koennte ein elem mehrmals zu falseelems hinzugefuegt werden
                # sicher nur einmal hinzufuegen, sonst koennte falsecount > elemcount werden
                elem_has_false_prop = True
                context.falseelems.append(
                    "{}, {}.{} = {} ({}):"
                    .format(
                        util.get_false_elem_string(elem, IfcStore.psets[elem.id()]),
                        target_pset,
                        target_property,
                        actual_value,
                        actual_propertytype
                    )
                )
        if elem_has_false_prop is True:
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    # check if all target_py_valuerange have been used in the model
    # they must be in actual_py_valuerange
    not_used_target_value = list(set(target_py_valuerange) - set(actual_py_valuerange))
    if len(not_used_target_value) > 0 and all_valuerangeitems_must_be_used is True:
        # print(not_used_target_value)
        assert False, "These items of value range have not been used in the model. {}".format(not_used_target_value)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseguids)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do not have a property value out of: {parameter}."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do not have the property value out of: {parameter}. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_py_valuerange
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


"""
def eleclass_material_has_quantity_valuerange_of(
    context, ifc_class, material, target_quantity, target_valuerange
):

    # waende backstein nur 12.5, 15, 17.5, 20 dick

    # hier oder in eleclasses
    # da letztenendes ein quantity geprueft wir hier, oder in nochmals separates module
    # nur fuer quantities, das finde ich gut
    # weil zum Beispiel bei quantities das set nicht explizit angegeben wird
    # auch ist evtl. der quantity name nicht exakt gleich in gherkin und hier

    from ast import literal_eval
    target_py_valuerange = literal_eval(target_valuerange)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # evtl. Ausgabe Anzahl elem und Anzahl elem die das attribut ueberhaupt angehaengt haben
    # Anzahl attrib macht keinen sinn wegen schichtattribute

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        elem_has_false_prop = False
        for propvaltyp in get_prop_values_and_types(elem, target_pset, target_property):
            if propvaltyp == []:
                # elem does not have this property attached
                continue
            actual_value, actual_propertytype = propvaltyp
            if actual_value not in target_py_valuerange:
                # print("{} not in {}".format(actual_value, target_py_valuerange))
                # ein elem koennte mehrmals ein False value type haben
                # das attribut kann in Schichten vorkommen
                # das attribut kann doppelt vorhanden sein (waere falsch, aber moeglich)
                # daher kann ein elem mehrmals zu falseelems hinzugefuegt werden
                elem_has_false_prop = True
                context.falseelems.append(
                    "{}, {}.{} = {} ({}):"
                    .format(elem, target_pset, target_property, actual_value, actual_propertytype)
                )
        if elem_has_false_prop is True:
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    context.elemcount = len(elements)
    context.falsecount = len(context.falseguids)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do not have a property value out of: {parameter}."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do not have the property value out of: {parameter}. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_py_valuerange
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name
"""


def eleclass_hasnot_chars_in_property_value(
    context, target_ifcos_query, target_pset, target_property, target_chars
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        props = find_property_both(elem, target_pset, target_property)
        if props[0] is True:
            for prop in props[1]:
                actual_value, actual_propertytype = prop
                if target_chars in actual_value:
                    # FIXME ein elem koennte mehrmals hinzugefuegt werden
                    print("{} is in {}".format(target_chars, actual_value))
                    context.falseelems.append("{}, {}.{} = {}:".format(
                        util.get_false_elem_string(elem, IfcStore.psets[elem.id()]),
                        target_pset,
                        target_property,
                        actual_value
                    ))
                    context.falseguids.append(elem.GlobalId)
                    context.falseprops[elem.id()] = str(IfcStore.psets[elem.id()])

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do have these chars {parameter} in the property value."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do have these chars {parameter} in the property value. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_chars
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def propertyvalue1_equals_propertyvalue2(
        context,
        pset1,
        target_property1,
        pset2,
        target_property2,
):

    # TODO and FIXME this only works on direct properties
    # how should it work on element layer properties?
    # how it should work between element layer properties and layer properties
    # how about multiple layer

    falseelems = []
    falseguids = []
    falseprops = {}

    elements = IfcStore.file.by_type("IfcBuildingElement")
    for elem in elements:
        psets = IfcStore.psets[elem.id()]
        if (
            (pset1 in psets and target_property1 in psets[pset1])
            and (pset2 in psets and target_property2 in psets[pset2])
        ):
            # print(elem)
            prop_value1 = psets[pset1][target_property1]
            prop_value2 = psets[pset2][target_property2]
            if not prop_value1 == prop_value2:
                extend_eletext =  ": {}={} and {}={}".format(
                    target_property1,
                    prop_value1,
                    target_property2,
                    prop_value2,
                )
                falseelems.append(util.get_false_elem_string(elem, psets) + extend_eletext)
                falseguids.append(elem.GlobalId)
                falseprops[elem.id()] = str(psets)

    out_falseelems = "\n"
    for e in falseelems:
        out_falseelems += e + "\n"
    elemcount = len(elements)
    falsecount = len(falseelems)
    parameter = None
    message_all_falseelems = "All {} IfcBuildingElements elements do not have the equal property value for {} and {}.".format(elemcount, target_property1, target_property2)
    message_some_falseelems = "The following {} of {} IfcBuildingElements do not have the equal property value for {} and {}: \n{}".format(falsecount, elemcount, target_property1, target_property2, out_falseelems)
    message_no_elems = "There are no IfcBuildingElements elements in the IFC file."
    if elemcount > 0 and falsecount == 0:
        return  # Test OK
    elif elemcount == 0:
        assert False, message_no_elems + "\n"
    elif falsecount == elemcount:
        if parameter is None:
            assert False, message_all_falseelems + "\n"
        else:
            assert False, message_all_falseelems + "\n"
    elif falsecount > 0 and falsecount < elemcount:
        if parameter is None:
            assert False, message_some_falseelems + "\n"
        else:
            assert False, message_some_falseelems + "\n"
    else:
        assert False, _("Error in falsecount, something went wrong.") + "\n"
    # the pset name is missing in the failing message, but it is in the step test name


def propertyvalue1_equals_elementclassname(
    context,
    target_pset,
    target_property
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcStore.file.by_type("IfcBuildingElement")
    for elem in elements:
        psets = IfcStore.psets[elem.id()]
        if (target_property in psets and target_property in psets[target_property]):
            # print(elem)
            if not elem.Name == psets[target_property][target_property]:
                context.falseelems.append(str(elem))
                context.falseguids.append(elem.GlobalId)
                context.falseprops[elem.id()] = str(psets)

    out_falseelems = "\n"
    for e in context.falseelems:
        out_falseelems += e + "\n"
    elemcount = len(elements)
    falsecount = len(context.falseelems)
    parameter = None
    message_all_falseelems = "The {}.{} does not equals the class attribute Name for all {} IfcBuildingElements elements.".format(target_property, target_property, elemcount)
    message_some_falseelems = "The {}.{} does not equals the class attribute Name for the following {} of {} IfcBuildingElements: \n{}".format(target_property, target_property, falsecount, elemcount, out_falseelems)
    message_no_elems = "There are no IfcBuildingElements elements in the IFC file."
    if elemcount > 0 and falsecount == 0:
        return  # Test OK
    elif elemcount == 0:
        assert False, message_no_elems
    elif falsecount == elemcount:
        if parameter is None:
            assert False, message_all_falseelems
        else:
            assert False, message_all_falseelems
    elif falsecount > 0 and falsecount < elemcount:
        if parameter is None:
            assert False, message_some_falseelems
        else:
            assert False, message_some_falseelems
    else:
        assert False, _("Error in falsecount, something went wrong.")
    # the target_property name is missing in the failing message, but it is in the step test name


# ***************************************************************************************
# helper, may be move into separate module
# ***************************************************************************************
def has_elem_complex_props(elem):
    # if one pset (no matter which) has complex props True will be returned
    psets = IfcStore.psets[elem.id()]
    for pset in psets:
        for key in psets[pset].keys():
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


def get_prop_values_and_types(aelem, target_pset, target_property):
    """
    return all find value and data type 
    no matter if attached directly or to a element layer by complex property
    no matter if prperty is a dublicate
    [(value, value data type), (value, value data type)]
    an empty list is returned if the prop is not found
    """

    props = []
    actual_value = None
    actual_propertytype = None
    psets = IfcStore.psets[aelem.id()]
    if target_pset in psets:
        actual_pset = psets[target_pset]
        if target_property in actual_pset:
            actual_value = actual_pset[target_property]
            actual_propertytype = get_value_type(actual_value)
            props.append((actual_value, actual_propertytype))
        for key, val in actual_pset.items():
            if 'Object Layer Attributes' in key:
                if 'properties' in val:
                    if target_property in val['properties']:
                        actual_value = val['properties'][target_property]
                        actual_propertytype = get_value_type(actual_value)
                        props.append((actual_value, actual_propertytype))
    # TODO and FIXME, get the data type from ifc data directly
    return props


def get_value_type(prop_value):
    # workaround, use the Python datatyp
    # TODO get the data typ from ifc file
    # value type mapping
    if isinstance(prop_value, str):
        return "IfcText"
    elif isinstance(prop_value, bool):
        return "IfcBoolean"
    elif isinstance(prop_value, float):
        return "IfcReal"
    elif isinstance(prop_value, int):
        return "IfcInteger"
    else:
        return None


# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************
# evtl. ungueltig, nicht funktinierend, veraltet
# ***************************************************************************************
# ***************************************************************************************
def eleclass_with_material_has_property_in_pset(
        context,
        target_ifcos_query,
        target_material,
        target_pset,
        target_property
    ):
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get the elements with target material
    # print(target_material)
    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    # print(len(target_elements))
    elements = []
    for elem in target_elements:
        # wichtig, es hat pruefung stattgefunden, dass all elem direkt Materialname haben
        if eleutils.get_material(elem).Name == target_material:
            # print(eleutils.get_material(elem).Name)
            elements.append(elem)
    # print(len(elements))

    # check if they have the attribute
    for elem in elements:
        allpsets = IfcStore.psets[elem.id()]
        if target_pset not in allpsets:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(allpsets)
            continue
        actual_pset = allpsets[target_pset]
        if target_property not in actual_pset:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(allpsets)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_ctarget_elementslass,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {parameter} {ifc_class} elements are missing the property in the PSet."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {parameter} {ifc_class} elements are missing the property in the PSet: {falseelems}"),
        message_no_elems=_("There are no {parameter} {ifc_class} elements in the IFC file."),
        parameter=target_material
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_with_not_material_has_not_property_in_pset(
        context,
        target_ifcos_query,
        target_material,
        target_pset,
        target_property
    ):
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get the elements with target material
    # print(target_material)
    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    # print(len(target_elements))
    elements = []
    for elem in target_elements:
        # wichtig, es hat pruefung stattgefunden, dass all elem direkt Materialname haben
        if eleutils.get_material(elem).Name != target_material:
            # print(eleutils.get_material(elem).Name)
            elements.append(elem)
    # print(len(elements))

    # check if they have not the attribute
    for elem in elements:
        allpsets = IfcStore.psets[elem.id()]
        if target_pset not in allpsets:
            continue
        actual_pset = allpsets[target_pset]
        if target_property in actual_pset:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(allpsets)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} non {parameter} {ifc_class} elements have the property in the PSet."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} non {parameter} {ifc_class} elements have the property in the PSet: {falseelems}"),
        message_no_elems=_("There are no non {parameter} {ifc_class} elements in the IFC file."),
        parameter=target_material
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


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
            context.falseelems.append(str(elem))
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
            context.falseelems.append(str(elem))
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
            context.falseelems.append(str(elem))
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
            context.falseelems.append(str(elem))
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
    psets = eleutils.get_psets(aelem)
    if target_pset in psets:
        actual_pset = psets[target_pset]
        if target_property in actual_pset:
            found = True  # do not use continue, pset could not exist
            actual_value = actual_pset[target_property]
            actual_propertytype = get_value_type(actual_value)
            props.append((actual_value, actual_propertytype))
        for key, val in actual_pset.items():
            if 'Object Layer Attributes' in key:
                if 'properties' in val:
                    if target_property in val['properties']:
                        found = True
                        actual_value = val['properties'][target_property]
                        actual_propertytype = get_value_type(actual_value)
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
    psets = eleutils.get_psets(aelem)
    if target_pset in psets:
        actual_pset = psets[target_pset]
        if target_property in actual_pset:
            found = True
            actual_value = actual_pset[target_property]
            actual_propertytype = get_value_type(actual_value)
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
    psets = eleutils.get_psets(aelem)
    if target_pset in psets:
        actual_pset = psets[target_pset]
        for key, val in actual_pset.items():
            if 'Object Layer Attributes' in key:
                if 'properties' in val:
                    if target_property in val['properties']:
                        actual_value = val['properties'][target_property]
                        found = True
                        break
    actual_propertytype = get_value_type(actual_value)
    # TODO and FIXME, get the data type from ifc data directly
    return (found, actual_value, actual_propertytype)


# ------------------------------------------------------------------------
# STEPS with Regular Expression Matcher ("re")
# ------------------------------------------------------------------------
use_step_matcher("re")


@step(r"All (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property")
def step_impl(context, ifc_class, property_path):
    import re
    pset, aproperty = property_path.split(".")
    eleclass_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step(r'All (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property value matching the pattern "(?P<pattern>.*)"')
def step_impl(context, ifc_class, property_path, pattern):
    import re
    from ifcopenshell.util.element import get_psets

    pset_name, property_name = property_path.split(".")
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:

        psets = get_psets(element)

        if  not pset_name in psets:
            assert False
        
        pset = psets[pset_name]
        if not property_name in pset:
            assert False
        
        prop = pset[property_name]
        # get_psets returns just strings

        if not re.search(pattern, prop):
            assert False


# ************************************************************************************************
def eleclass_has_propertycount_in_pset(
    context, target_ifcos_query, target_attribut_count, target_pset
):
    
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}
    from ifcopenshell.util.element import get_psets

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        actual_psets = get_psets(elem)
        if target_pset in actual_psets:
            # IfcOS saves the pset id on one key in the dict, thus minus 1
            actual_attribut_count = str(len(actual_psets[target_pset]) - 1)
            # print(elem)
            # print(actual_attribut_count)
            if actual_attribut_count != target_attribut_count:
                context.falseelems.append(str(elem))
                context.falseguids.append(elem.GlobalId)
                context.falseprops[elem.id()] = str(actual_psets)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do not have exactly {parameter} attributes in the pset."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do not have exactly {parameter} in the pset: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_attribut_count
    )
    # evtl. als parameter die keys des dict, also die attributnamen, dann super fehlerausgabe
    # the pset name is missing in the failing message, but it is in the step test name

    return


def eleclass_has_property_in_pset(
    context, target_ifcos_query, pset, aproperty
):
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}
    from ifcopenshell.util.element import get_psets

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        psets = get_psets(elem)
        if not (pset in psets and aproperty in psets[pset]):
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(psets)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements are missing the property {parameter} in the pset."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements are missing the property {parameter} in the pset: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=aproperty
    )
    # the pset name is missing in the failing message, but it is in the step test name
