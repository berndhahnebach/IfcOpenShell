import json

import ifcopenshell
import ifcopenshell.util.element as eleutils
import ifcopenshell.validate
from ifcopenshell.util import selector  # needed for ifcopenshell.util.selector.filter_elements to work

from bimtester.lang import _
from bimtester.ifc import IfcStore


def by_types(ifc, ifc_types):
    elements = []
    for ifc_type in ifc_types.split(","):
        elements += ifc.by_type(ifc_type.strip())
    return elements


def validate(ifc):
    errors = []
    logger = ifcopenshell.validate.json_logger()
    try:
        ifcopenshell.validate.validate(ifc, logger)
        if logger.statements:
            for statement in logger.statements:
                errors.append(f"{json.dumps(statement, default=str)}")
    except RuntimeError as error:
        assert False, str(error)


def assert_guid(ifc, guid):
    try:
        return ifc.by_guid(guid)
    except:
        assert False, _("An element with the ID {} could not be found.").format(guid)


def assert_number(number):
    try:
        return float(number)
    except ValueError:
        assert False, _("A number should be specified, not {}").format(number)


def assert_type(element, ifc_class, is_exact=False):
    if is_exact:
        assert element.is_a() == ifc_class, _("The element {} is an {} instead of {}.").format(
            element, element.is_a(), ifc_class
        )
    else:
        assert element.is_a(ifc_class), _("The element {} is an {} instead of {}.").format(
            element, element.is_a(), ifc_class
        )


def assert_attribute(element, name, value=None):
    if not hasattr(element, name):
        assert False, _("The element {} does not have the attribute {}").format(element, name)
    if not value:
        if getattr(element, name) is None:
            assert False, _("The element {} does not have a value for the attribute {}").format(element, name)
        return getattr(element, name)
    if value == "NULL":
        value = None
    actual_value = getattr(element, name)
    if isinstance(value, list) and actual_value:
        actual_value = list(actual_value)
    assert actual_value == value, _('We expected a value of "{}" but instead got "{}" for the element {}').format(
        value, actual_value, element
    )


def assert_pset(element, pset_name, prop_name=None, value=None):
    if value == "NULL":
        value = None
    psets = eleutils.get_psets(site)
    if pset_name not in psets:
        assert False, _("The element {} does not have a property set named {}").format(element, pset_name)
    if prop_name is None:
        return psets[pset_name]
    if prop_name not in psets[pset_name]:
        assert False, _('The element {} does not have a property named "{}" in the pset "{}"').format(
            element, prop_name, pset_name
        )
    if value is None:
        return psets[pset_name][prop_name]
    actual_value = psets[pset_name][prop_name]
    assert actual_value == value, _('We expected a value of "{}" but instead got "{}" for the element {}').format(
        value, actual_value, element
    )


# TODO: what is this? ... a generic assert method
def assert_elements(
    ifc_class,
    elemcount,
    falsecount,
    falseelems,
    message_all_falseelems,
    message_some_falseelems,
    message_no_elems="",
    parameter=None
):
    # improve output of falselems
    out_falseelems = "\n\n"
    for e in sorted(falseelems):
        out_falseelems += e + "\n"

    # deprecated
    # elemcount == 0 creates a failed test, but should not
    # no elements of a ifc_class should not be a fail
    # if a ifc_class has to be exist, it should be in a own test
    # if elemcount > 0 and falsecount == 0:
    #     return # Test OK
    # elif elemcount == 0:
    #     assert False, (
    #         message_no_elems.format(
    #             ifc_class=ifc_class
    #         )
    #     )

    if falsecount == 0:
        return # test ok for elemcount == 0 and elemcount > 0
    elif falsecount == elemcount:
        if parameter is None:
            assert False, (
                message_all_falseelems.format(
                    elemcount=elemcount,
                    ifc_class=ifc_class
                ) + "\n"
            )
        else:
            assert False, (
                message_all_falseelems.format(
                    elemcount=elemcount,
                    ifc_class=ifc_class,
                    parameter=parameter
                ) + "\n"
            )
    elif falsecount > 0 and falsecount < elemcount:
        if parameter is None:
            assert False, (
                message_some_falseelems.format(
                    falsecount=falsecount,
                    elemcount=elemcount,
                    ifc_class=ifc_class,
                    falseelems=out_falseelems,
                ) + "\n"
            )
        else:
            assert False, (
                message_some_falseelems.format(
                    falsecount=falsecount,
                    elemcount=elemcount,
                    ifc_class=ifc_class,
                    falseelems=out_falseelems,
                    parameter=parameter
                ) + "\n"
            )
    else:
        assert False, _("Error in falsecount calculation, something went wrong.") + "\n"


def get_common_pset_name(ifc_class):
    return ifc_class.replace("Ifc", "Pset_") + "Common"


def assert_class(context, ifc_class):
    # Do I really need this? Why does it makes sense allow only special ifcclass in testing?
    # TODO: somehow get known ifc_classes from ifc schema from IfcOpenShell
    # some architecture are missing, IfcRoof
    # all MEP classes are missing as well
    # see FreeCAD importIFC or exportIFC module
    known_classes = [
        #
        # ohne Vererbung, daher alle enitties noetig die explizit in pruefungen verwendet werden
        #
        # Level 1
        # "IfcRoot",
        #
        # Level 2
        # "IfcObjectDefinition",
        #
        # Level 3
        # "IfcObject",
        #
        # Level 4
        "IfcProduct",
        #
        # Level 5
        "IfcAnnotation",
        "IfcElement",
        "IfcSpatialElement",
        #
        # Level 6
        # IfcElement
        "IfcBuildingElement",
        "IfcElementComponent",  # nur in ifc4
        "IfcFeatureElement",
        #
        #
        # IfcProduct
        # IfcElement
        # IfcBuildingElement
        "IfcBeam",
        "IfcBuildingElementComponent",  # (IFC2x3)
        "IfcBuildingElementProxy",
        "IfcColumn",
        "IfcCovering",
        "IfcFooting",
        "IfcMember",
        "IfcPile",
        "IfcPlate",
        "IfcRamp",
        "IfcRoof",
        "IfcRailing",
        "IfcSlab",
        "IfcStair",
        "IfcWall",
        #
        # IfcProduct
        # IfcElement
        # IfcElementComponent (IFC4)
        # IfcBuildingElement (IFC2x3)
        # IfcBuildingElementComponent(IFC2x3)
        # IfcReinforcingElement
        "IfcReinforcingBar",
        "IfcReinforcingMesh",
        "IfcTendon",
        "IfcTendonAnchor",
        #
        # IfcProduct
        # IfcElement
        # IfcFeatureElement
        # IfcFeatureElementSubtraction
        # children
        "IfcOpeningElement",
        #
        # IfcProduct
        # IfcSpatialElement
        # IfcSpatialStructureElement
        "IfcSpatialStructureElement",
        "IfcSite",
        "IfcBuilding",
        "IfcBuildingStorey",
        #
    ]
    if not ifc_class in known_classes:

        # -- SKIP: Remaining steps in current feature.
        context.feature.skip(_("Error in assert_class in utils module."))

        assert False, (_("Not known IFC class: '{}'. See list in utils module.").format(ifc_class))


def extract_ifc_classes(context, ifc_classes):
    # no error handling needed
    # if no comma or any other problem, the assert_class will fail
    # and give some feedback
    # print(ifc_classes)
    target_ifc_classes = ifc_classes.replace(" ","").split(",")
    # print(target_ifc_classes)
    for ifc_class in target_ifc_classes:
        # print(ifc_class)
        assert_class(context, ifc_class)
    return target_ifc_classes


def get_false_elem_string(elem, psets=None):

    if psets is None:
        if elem.is_a("IfcOpeningElement"):
            psets = eleutils.get_psets(elem)
        else:
            print("PSets not in IfcStore, have a look at utils module.")
            psets = eleutils.get_psets(elem)

    if "AllplanAttributes" in psets and "Allright_Bauteil_ID" in psets["AllplanAttributes"]:
        allplan_id = psets["AllplanAttributes"]["Allright_Bauteil_ID"]
    else:
        allplan_id = None

    false_elem_string = "{}, {}, {}, {}, {}".format(
        allplan_id,
        elem.GlobalId,
        elem.id(),
        elem.is_a(),
        elem.Name,
    )

    return false_elem_string


def get_elems(ifcfile, query):
    # https://community.osarch.org/discussion/comment/20637/#Comment_20637
    elems = ifcopenshell.util.selector.filter_elements(ifcfile, query.replace("'",'"'))
    return elems


# ********************************************************************************************
# Workaround
# to have access from all steps
# ********************************************************************************************
#
# ********************************************************************************************
def minus_elems_by_allplantype_and_name(elements, no_elemes_by_allplantype=[], no_elems_by_name=[]):


    for no_q_ele in no_elemes_by_allplantype:
        minus_query = "IfcBuildingElement, AllplanAttributes.Allright_Bauteil_ID=/[0-9]{4}" + no_q_ele + "[0-9]{10}/"
        minus_elements = get_elems(IfcStore.file, minus_query)

        elements = list(set(elements) - set(minus_elements))

    new_elems = []
    for elem in elements:
        for name_part in no_elems_by_name:
            if name_part in elem.Name:
                break
        else:
            new_elems.append(elem)

    return new_elems


# ************************************************************************************************
def minus_elems_without_volume(target_elements):
    new_elems = minus_elems_by_allplantype_and_name(
        target_elements,
        [],
        get_ele_nameparts_without_volume(),
    )
    return new_elems


# ************************************************************************************************
def minus_elems_without_quantities(target_elements):
    new_elems = minus_elems_by_allplantype_and_name(
        target_elements,
        get_ele_objtyps_without_quantity(),
        [],
    )
    return new_elems


# ************************************************************************************************
def get_ele_nameparts_without_volume():

    # minus_elements do not have volume
    # because they are faces elements
    # name parts are allowed as well

    # they do not have a volume
    # but they could have all the other errors as well, but should not
    # thus fine a better way, than just ignore them

    # TODO: long term ... move to Modellzuordnungen

    elems_names = [
        "AE nachträglich Versetzen",  # 20088
        "BGS_Boeschung_",
        "Nullkote",
        "Meereskote"
    ]

    return elems_names


# ************************************************************************************************
def get_ele_objtyps_without_quantity():

    # elems do not have any quantities, never (ATM) ... may be find out why?
    # allplan internal short cuts

    # die haben sowieso keine Quantities und wir rechnen auch keine dafuer
    # daher reicht das parsen der geometrie durch IfcOS als pruefung aus
    # einfach aktuell keine weiteren geom pruefungen

    # bei macros ist geometrie meist nebensache, hauptsache IFCOS kann es parsen
    # bsp Verkehrsschilder, Bohrgeraet, Autos, etc, aber pruefungen brauchen ewig

    # 3dF ... 3DFundament
    # Gel ... Gelaendertool (nur kein Volumen, Quantities werden exportiert, aber nur eine Laenge)
    # Kop ... Mengenkoerper, importierte Kragplattenanschluesse Schoeck
    # Mak ... Makro
    # PEb ... Acitop SmartPart Rueckbiegeanschluesse
    # Pyt ... Pythonpart (kontrolle, ob mit Quantities moeglich)
    # Sma ... SmartPart 3D-Text die sind riesig und brauchen im GeomTest ewig, wegen rundungen fallen die eh durch
                # aufpassen, es gibt unendlich SmartParts

    # TODO: long term ... move to Modellzuordnungen

    obj_typs = ["3dF", "Gel", "Kop", "Mak", "PEb", "Pyt", "Sma"]

    return obj_typs
