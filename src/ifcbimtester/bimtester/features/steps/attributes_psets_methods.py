import gettext  # noqa
from ifcopenshell.util.element import get_psets

from utils import assert_elements
from utils import IfcFile


def eleclass_has_property_implement(
    context, ifc_class, target_property, target_pset
):
    pass


def eleclass_has_no_complex_property(
    context, ifc_class
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        if has_elem_complex_props(elem) is True:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements have complex properties."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements have complex properties: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
    )


def eleclass_has_property_in_pset(
    context, ifc_class, target_property, target_pset, minus_ifc_class=""
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get the elements
    all_elements = IfcFile.get().by_type(ifc_class)
    elements = []
    if minus_ifc_class == "":
        elements = all_elements
    else:
        minus_elements =  IfcFile.get().by_type(minus_ifc_class)
        for elem in all_elements:
            if elem not in minus_elements:
                 elements.append(elem)

    # check if they have the attribute
    for elem in elements:
        psets = get_psets(elem)
        actual_pset = psets[target_pset]  # was wenn pset nicht vorhanden dann error
        if target_property not in actual_pset:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
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


def eleclass_without_complexlayerattributes_has_property(
    context, ifc_class, target_property, target_pset
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get elements without complex layer properties in all psets
    all_elements = IfcFile.get().by_type(ifc_class)
    elements = []
    for elem in all_elements:
        if has_elem_complex_props(elem) is False:
            elements.append(elem)

    # check if they have the attribute
    for elem in elements:
        psets = get_psets(elem)
        actual_pset = psets[target_pset]  # was wenn pset nicht vorhanden dann error
        if target_property not in actual_pset:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
        ifc_class,
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
    context, ifc_class, target_property, target_pset
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get elements with complex layer properties in all psets
    all_elements = IfcFile.get().by_type(ifc_class)
    elements = []
    for elem in all_elements:
        if has_elem_complex_props(elem) is True:
            elements.append(elem)

    # check if they have the attribute
    for elem in elements:
        psets = get_psets(elem)
        actual_pset = psets[target_pset]  # was wenn pset nicht vorhanden dann error
        if target_property not in actual_pset:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
        ifc_class,
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
    context, ifc_class, target_property, target_pset
):
    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # get elements with complex layer properties in at least one psets
    all_elements = IfcFile.get().by_type(ifc_class)
    elements = []
    for elem in all_elements:
        if has_elem_complex_props(elem) is True:
            elements.append(elem)

    # check if they have the property in each complex layer
    for elem in elements:
        psets = get_psets(elem)
        actual_pset = psets[target_pset]  # was wenn pset nicht vorhanden dann error
        complex_props = get_complex_props(actual_pset)
        # check if the target_pset has complex properties
        if len(complex_props) == 0:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))
        #for complex_prop in complex_props

    """
        **********************!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        property should be in ALL complex layer
        if target_property in actual_pset:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))
    """

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
        ifc_class,
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
    context, ifc_class, target_property, target_pset, target_propertytype
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # evtl. Ausgabe Anzahl elem und Anzahl elem die das attribut ueberhaupt angehaengt haben
    # Anzahl attrib macht keinen sinn wegen schichtattribute

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        elem_has_false_prop = False
        for propvaltyp in get_prop_values_and_types(elem, target_property, target_pset):
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
                context.falseelems.append("{}, {}.{} = {}, {}:".format(elem, target_property, target_pset, actual_value, actual_propertytype))
        if elem_has_false_prop is True:
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseguids)
    assert_elements(
        ifc_class,
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
    context, ifc_class, target_property, target_pset, target_value
):

    from ast import literal_eval
    target_py_value = literal_eval(target_value)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # evtl. Ausgabe Anzahl elem und Anzahl elem die das attribut ueberhaupt angehaengt haben
    # Anzahl attrib macht keinen sinn wegen schichtattribute

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        elem_has_false_prop = False
        for propvaltyp in get_prop_values_and_types(elem, target_property, target_pset):
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
                    .format(elem, target_property, target_pset, actual_value, actual_propertytype, type(target_py_value))
                )
        if elem_has_false_prop is True:
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseguids)
    assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do not have the property value: {parameter}."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do not have the property value: {parameter}. False elements: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=target_value
    )
    # improve output, the pset name is missing in the failing message, but it is in the step test name


def eleclass_has_property_valuerange_of(
    context, ifc_class, target_property, target_pset, target_valuerange
):

    from ast import literal_eval
    target_py_valuerange = literal_eval(target_valuerange)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # evtl. Ausgabe Anzahl elem und Anzahl elem die das attribut ueberhaupt angehaengt haben
    # Anzahl attrib macht keinen sinn wegen schichtattribute

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        elem_has_false_prop = False
        for propvaltyp in get_prop_values_and_types(elem, target_property, target_pset):
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
                    "{}, {}.{} = {} ({}), targetrange eval = {}:"
                    .format(elem, target_property, target_pset, actual_value, actual_propertytype, target_py_valuerange)
                )
        if elem_has_false_prop is True:
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseguids)
    assert_elements(
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


def eleclass_hasnot_chars_in_property_value(
    context, ifc_class, target_property, target_pset, target_chars
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        props = find_property_both(elem, target_property, target_pset)
        if props[0] is True:
            for prop in props[1]:
                actual_value, actual_propertytype = prop
                if target_chars in actual_value:
                    # FIXME ein elem koennte mehrmals hinzugefuegt werden
                    print("{} is in {}".format(target_chars, actual_value))
                    context.falseelems.append("{}, {}.{} = {}:".format(elem, target_property, target_pset, actual_value))
                    context.falseguids.append(elem.GlobalId)
                    context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
        ifc_class,
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
        target_property1,
        pset1,
        target_property2,
        pset2
):

    # TODO and FIXME this only works on direct properties
    # how should it work on element layer properties?
    # how it should work between element layer properties and layer properties
    # how about multiple layer

    falseelems = []
    falseguids = []
    falseprops = {}

    elements = IfcFile.get().by_type("IfcBuildingElement")
    for elem in elements:
        psets = get_psets(elem)
        if (
            (pset1 in psets and target_property1 in psets[pset1])
            and (pset2 in psets and target_property2 in psets[pset2])
        ):
            # print(elem)
            prop_value1 = psets[pset1][target_property1]
            prop_value2 = psets[pset2][target_property2]
            if not prop_value1 == prop_value2:
                falseelems.append(str(elem))
                falseguids.append(elem.GlobalId)
                falseprops[elem.id()] = str(get_psets(elem))


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
    # the pset name is missing in the failing message, but it is in the step test name


def propertyvalue1_equals_elementclassname(
    context,
    target_property,
    pset
):

    falseelems = []
    falseguids = []
    falseprops = {}

    elements = IfcFile.get().by_type("IfcBuildingElement")
    for elem in elements:
        psets = get_psets(elem)
        if (pset in psets and target_property in psets[pset]):
            # print(elem)
            if not elem.Name == psets[pset][target_property]:
                falseelems.append(str(elem))
                falseguids.append(elem.GlobalId)
                falseprops[elem.id()] = str(get_psets(elem))

    out_falseelems = "\n"
    for e in falseelems:
        out_falseelems += e + "\n"
    elemcount = len(elements)
    falsecount = len(falseelems)
    parameter = None
    message_all_falseelems = "The {}.{} does not equals the class attribute Name for all {} IfcBuildingElements elements.".format(target_property, pset, elemcount)
    message_some_falseelems = "The {}.{} does not equals the class attribute Name for the following {} of {} IfcBuildingElements: \n{}".format(target_property, pset, falsecount, elemcount, out_falseelems)
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
    # the pset name is missing in the failing message, but it is in the step test name


# ***************************************************************************************
# helper, may be move into separate module
# ***************************************************************************************
def has_elem_complex_props(elem):
    # if one pset (no matter which) has complex props True will be returned
    psets = get_psets(elem)
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


def get_prop_values_and_types(aelem, target_property, target_pset):
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
    psets = get_psets(aelem)
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
def eleclass_has_property_directly_in_pset(
    context, ifc_class, target_property, target_pset
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        found, actual_value, actual_datatype = find_property_directly(elem, target_property, target_pset)
        if found is False:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
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
    context, ifc_class, target_property, target_pset
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        found, actual_value, actual_datatype = find_property_directly(elem, target_property, target_pset)
        if found is True:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
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
    context, ifc_class, target_property, target_pset
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        found, actual_value, actual_datatype = find_property_directly(elem, target_property, target_pset)
        if found is True:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
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
    context, ifc_class, target_property, target_pset
):

    # property has to be in the layer not directly at the element

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    elements = IfcFile.get().by_type(ifc_class)
    for elem in elements:
        found, actual_value, actual_datatype = find_property_elemlayer(elem, target_property, target_pset)
        if found is False:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(get_psets(elem))

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    assert_elements(
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


def find_property_both(aelem, target_property, target_pset):
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
    psets = get_psets(aelem)
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


def find_property_directly(aelem, target_property, target_pset):
    """
    return True if the property is directly attached to the element
    (True or False, value, value data type)
    we need to return True or False because None is a valid property value
    """
    # sofort bei ersten finden return
    found = False
    actual_value = None
    actual_propertytype = None
    psets = get_psets(aelem)
    if target_pset in psets:
        actual_pset = psets[target_pset]
        if target_property in actual_pset:
            found = True
            actual_value = actual_pset[target_property]
            actual_propertytype = get_value_type(actual_value)
            return (found, actual_value, actual_propertytype)
    return (found, actual_value, actual_propertytype)


def find_property_elemlayer(aelem, target_property, target_pset):
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
    psets = get_psets(aelem)
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
