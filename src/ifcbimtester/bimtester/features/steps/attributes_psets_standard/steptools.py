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

from bimtester import helpertools
from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


def eleclass_has_property_value_matching_pattern(
    context, target_ifcos_query, target_pset, target_property, target_pattern
):

    import re

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    # print(target_ifcos_query)
    # print(target_elements)
    for elem in target_elements:
        # print("")
        # print(elem)
        propvaltyps = get_prop_values_and_types(elem, target_pset, target_property)
        # print(propvaltyps)
        if len(propvaltyps) == 0:
            print(elem)
            print("Either target prop: {} or target pset: {} or value not found, which is not a failing test.".format(target_property, target_pset))
            # on cad repair pruefen wir den wert des teilbildnamens, aber der ist an vielen objekten garnicht vorhandnen
            # der wird durch cad repair erst angehangen
            print("")
            continue
        elif len(propvaltyps) > 1:
            print("Property more than once. Not handled case.")
            ele_allpsets = IfcStore.psets[elem.id()]
            context.falseelems.append("{}, prop more than once on elem: {}".format(util.get_false_elem_string(elem, ele_allpsets), propvaltyps))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(ele_allpsets)
            continue
        elif len(propvaltyps) == 1:
            # print("Found one property value with type :-)")
            actual_value, actual_propertytype = propvaltyps[0]
        # print(actual_value)
        # print(actual_propertytype)
        # print(target_pattern, flush=True)
        if not re.fullmatch(target_pattern, actual_value):
            # https://docs.python.org/3/library/re.html#re.fullmatch
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


def eleclass_has_property_in_pset(
    context, target_ifcos_query, target_pset, target_property
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get the elements
    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)

    # check if they have the attribute
    for elem in target_elements:
        ele_allpsets = IfcStore.psets[elem.id()]
        if target_pset not in ele_allpsets:
            context.falseelems.append(util.get_false_elem_string(elem, ele_allpsets))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(ele_allpsets)
            continue
        actual_pset = ele_allpsets[target_pset]
        if target_property not in actual_pset:
            context.falseelems.append(util.get_false_elem_string(elem, ele_allpsets))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(ele_allpsets)

    context.elemcount = len(target_elements)
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


def eleclass_has_not_property_in_pset(
    context, target_ifcos_query, target_pset, target_property
):
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get the elements
    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)

    # check if they have not the attribute
    for elem in target_elements:
        ele_allpsets = IfcStore.psets[elem.id()]
        if target_pset not in ele_allpsets:
            continue
        actual_pset = ele_allpsets[target_pset]
        if target_property in actual_pset:
            context.falseelems.append(util.get_false_elem_string(elem, ele_allpsets))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(ele_allpsets)

    context.elemcount = len(target_elements)
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
        ele_allpsets = IfcStore.psets[elem.id()]
        target_pset_name = util.get_common_pset_name(a_ifc_class)
        if target_pset_name not in ele_allpsets:
            context.falseelems.append("{}".format(util.get_false_elem_string(elem, ele_allpsets)))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(ele_allpsets)
            continue
        actual_pset = ele_allpsets[target_pset_name]
        if target_property not in actual_pset:
            context.falseelems.append(util.get_false_elem_string(elem, ele_allpsets))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(ele_allpsets)
        # print(ele_allpsets[target_pset_name][target_property])

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
                print("{} is not value type {}. It ist of type: {}".format(actual_value, target_propertytype, actual_propertytype))
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
        ele_allpsets = IfcStore.psets[elem.id()]
        if (
            (pset1 in ele_allpsets and target_property1 in ele_allpsets[pset1])
            and (pset2 in ele_allpsets and target_property2 in ele_allpsets[pset2])
        ):
            # print(elem)
            prop_value1 = ele_allpsets[pset1][target_property1]
            prop_value2 = ele_allpsets[pset2][target_property2]
            if not prop_value1 == prop_value2:
                extend_eletext =  ": {}={} and {}={}".format(
                    target_property1,
                    prop_value1,
                    target_property2,
                    prop_value2,
                )
                falseelems.append(util.get_false_elem_string(elem, ele_allpsets) + extend_eletext)
                falseguids.append(elem.GlobalId)
                falseprops[elem.id()] = str(ele_allpsets)

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
        ele_allpsets = IfcStore.psets[elem.id()]
        if (target_pset in ele_allpsets and target_property in ele_allpsets[target_pset]):
            # print(elem)
            if not elem.Name == ele_allpsets[target_pset][target_property]:
                context.falseelems.append("{}".format(util.get_false_elem_string(elem, ele_allpsets)))
                context.falseguids.append(elem.GlobalId)
                context.falseprops[elem.id()] = str(ele_allpsets)

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
    ele_allpsets = IfcStore.psets[aelem.id()]
    # print(ele_allpsets)
    if target_pset in ele_allpsets:
        actual_pset = ele_allpsets[target_pset]
        if target_property in actual_pset:
            actual_value = actual_pset[target_property]
            # HAAAACK
            # helps to overcome type pruefung
            # value pruefung could be deactivated or edited
            # but on adding such a enum list property value on IFC4, ifcos will give a error
            # but I will keep the hack anyway
            # print(actual_value)
            # print(type(actual_value))
            # on ifc4
            # #26064=IFCPROPERTYENUMERATEDVALUE('Status',$,(IFCLABEL('EXISTING')),$);
            # ifcos returns ['EXISTING'] as property value
            if isinstance(actual_value, list) and len(actual_value) == 1:
                print("found one item list: {}. The first list item {} ist used.".format(actual_value, actual_value[0]))
                actual_value = actual_value[0]
            # print(actual_value)
            actual_propertytype = helpertools.get_value_type(actual_value)
            props.append((actual_value, actual_propertytype))
        for key, val in actual_pset.items():
            if 'Object Layer Attributes' in key:
                if 'properties' in val:
                    if target_property in val['properties']:
                        actual_value = val['properties'][target_property]
                        actual_propertytype = helpertools.get_value_type(actual_value)
                        props.append((actual_value, actual_propertytype))
    # TODO and FIXME, get the data type from ifc data directly
    return props


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
    ele_allpsets = IfcStore.psets[aelem.id()]
    if target_pset in ele_allpsets:
        actual_pset = ele_allpsets[target_pset]
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


def eleclass_has_propertycount_in_pset(
    context, target_ifcos_query, target_attribut_count, target_pset
):
    
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        ele_allpsets = IfcStore.psets[elem.id()]
        if target_pset in ele_allpsets:
            # IfcOS saves the pset id on one key in the dict, thus minus 1
            actual_attribut_count = str(len(ele_allpsets[target_pset]) - 1)
            # print(elem)
            # print(actual_attribut_count)
            if actual_attribut_count != target_attribut_count:
                context.falseelems.append("{}, {} properties".format(
                        util.get_false_elem_string(elem, ele_allpsets), actual_attribut_count
                ))
                context.falseguids.append(elem.GlobalId)
                context.falseprops[elem.id()] = str(ele_allpsets)

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

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        ele_allpsets = IfcStore.psets[elem.id()]
        if not (pset in ele_allpsets and aproperty in ele_allpsets[pset]):
            context.falseelems.append("{}".format(util.get_false_elem_string(elem, ele_allpsets)))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(ele_allpsets)

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
