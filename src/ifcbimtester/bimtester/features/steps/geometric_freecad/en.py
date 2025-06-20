from os.path import join

import ifcopenshell.util.element as eleutils

from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


std_allplan_psets = "AllplanAttributes"


@step('All "{ifcos_query}" elements must have a Allplan volume greater than 0.0.')
def step_impl(context, ifcos_query):
    eleclass_has_allplan_volume_greater_zero(
        context,
        ifcos_query,
    )


@step('All "{ifcos_query}" elements must have a geometric representation which could be parsed')
def step_impl(context, ifcos_query):
    eleclass_has_geometric_representation_parsed_by_ifcos(context, ifcos_query)


@step('All "{ifcos_query}" elements with existing geometry have no errors')
def step_impl(context, ifcos_query):
    eleclass_existing_geometric_representation_has_no_errors(context, ifcos_query)


@step('All "{ifcos_query}" elements must have a maximum edge length of "{max_edge_length}" mm in their geometry')
def step_impl(context, ifcos_query, max_edge_length):
    eleclass_existing_geometric_representation_has_max_edge_length(context, ifcos_query, max_edge_length)


@step('All "{ifcos_query}" elements must have a geometry consisting only one volume solid')
def step_impl(context, ifcos_query):
    eleclass_existing_geometric_representation_has_single_solid(context, ifcos_query)


@step('All "{ifcos_query}" elements must have a geometry which is not empty just becaause of a opening bigger than the element')
def step_impl(context, ifcos_query):
    eleclass_existing_geometric_representation_has_not_opening_bigger_than_element(context, ifcos_query)


@step('All "{ifcos_query}" elements must have a Allplan volume to FreeCAD volume ratio between 99 und 101 prozent.')
def step_impl(context, ifcos_query):
    eleclass_has_given_allplan_to_freecad_volumen_ratio(
        context,
        ifcos_query
    )


# ich baue doch den zur wandpruefung mit geomtest um
@step('All "{ifcos_query}" elements do only have the "{aquantity}" value range of "{valuerange}"')
def step_impl(context, ifcos_query, aquantity, valuerange):
    eleclass_has_wall_thickness_valuerange_of(
        context,
        ifcos_query,
        aquantity,
        valuerange
    )


# deprecated
@step('All "{ifcos_query}" elements must have a geometric representation without errors')
def step_impl(context, ifcos_query):
    depricated_eleclass_has_geometric_representation_without_errors(context, ifcos_query)


# ************************************************************************************************
# test methods
def eleclass_has_allplan_volume_greater_zero(
    context,
    target_ifcos_query
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    target_elements = util.minus_elems_without_quantities(target_elements)
    target_elements = util.minus_elems_without_volume(target_elements)

    for elem in target_elements:
        vol_ap = None
        allpsets = IfcStore.psets[elem.id()]
        if (
            std_allplan_psets in allpsets
            and "Allplanvolumen" in allpsets[std_allplan_psets]
        ):
            vol_ap = allpsets[std_allplan_psets]["Allplanvolumen"]
            # print(vol_ap)

        # None is not a failing. No Property Allplan_Volumen is not a fail either
        # None and no Allplan_Volumen should never happen
        # should have been found earlier, or there is a error in BT in setting the Allplan_Volumen
        if vol_ap is None:
            print("")
            print("")
            print(elem)
            print(vol_ap)
            print("")
            print("")

        # Allplan even is able to export a negative volume. A volume smaller than 0 
        # a Allplanvolumen == 0 and < 0 is a fail thus <=
        if vol_ap <= 0:  # falls vol_ap None ist gibt es eine Exception die von Behave gefangen wird
            context.falseelems.append("{}, volume = {}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]), vol_ap))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(allpsets)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        # TODO: Translate these messages into other languages
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do have a Allplan volume of 0.0."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do have a Allplan volume of 0.0: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=None
    )
    # the pset name is missing in the failing message, but it is in the step test name


def eleclass_has_geometric_representation_parsed_by_ifcos(
    context,
    target_ifcos_query
):

    # IfcOpenShell returns a brep which does include geometric eles
    # at least one Vertex should be in there
    # I need a FreeCAD shape to test this

    # return
    extended_prints = False
    if "geom" in context.ifcfile_basename:
        extended_prints = True
        import sys
        print("Because auf word geom in ifc file name extended prints in geom pruefungen.")

    # IDEE !!!
    # wenn geom, dann erstelle ein errorifc fuer jedes elem und schreib es
    # das wird dann beim naechsten elem ueberschrieben
    # bei absturz wird es nicht ueberschrieben
    # geht nicht smart, da das ja in tmp im bimtester run verzeichnis erstellt wird
    
    context.falseelems = []
    context.falseguids = []

    # FreeCAD is needed
    try_to_import_freecad()

    # create file to save broken geometry in there
    geom_ifc = get_new_ifc_file(IfcStore)
    save_geom_ifc = False

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)

    # break if more than max_geom_elelen elements, run time ...
    max_geom_elelen = 10000
    context.elemcount = len(target_elements)
    print("")
    print("******************Geom test maxim. element length: {}******************".format(max_geom_elelen))
    print("******************Geom test actual element length: {}******************".format(context.elemcount))
    print("")
    if context.elemcount > max_geom_elelen:
        context.falsecount = context.elemcount
        util.assert_elements(
            target_ifcos_query,
            context.elemcount,
            context.falsecount,
            [],
            message_all_falseelems=_("There are {elemcount} {ifc_class} elements < %d {ifc_class} = max elements for geometry parsing." % (max_geom_elelen)),
            message_some_falseelems= "",
            message_no_elems=_("There are no {ifc_class} elements in the IFC file.")
        )

    for elem in target_elements:

        if extended_prints is True:
            print(elem)
            sys.stdout.flush()  # if BIMTester crashes, it is seen on which file
            # continue

        brep = get_brep_from_ifc_elem(elem)
        shape = get_fc_shape_from_ifcos_brep(brep)

        # init shape errors to None
        IfcStore.geom_has_errors[elem.id()] = None
        error = ""

        if brep is None:
            IfcStore.geom_has_elements[elem.id()] = None
            error = "The parser failed at all to process the geometric representation."
            # add it to the broken geom ifc file
            geom_ifc.add(IfcStore.file[elem.id()])
            save_geom_ifc = True

        if extended_prints is True:
            print("brep creation did not crash.")
            sys.stdout.flush()  # if BIMTester crashes it is seen on which file

        if brep is not None and shape.isNull():
            # geht das denn ueberhaupt, brep is not None, aber Shape is Nullshape
            # Nullshape ist leere Shapeinstanz von FreeCAD
            error = "Nullshape"
            IfcStore.geom_has_elements[elem.id()] = False
        elif brep is not None and not shape.isNull() and not shape.Vertexes:
            error = "No Vertexes"
            IfcStore.geom_has_elements[elem.id()] = False
            # siehe separate methode
            # eleclass_existing_geometric_representation_has_not_opening_bigger_than_element()
            # haeufiges problem "Oeffnung groesser als Objekt, daher keine Geometrie."
        else:
            IfcStore.geom_has_elements[elem.id()] = True

        IfcStore.geom_freecad_shape[elem.id()] = shape

        if error != "":
            context.falseelems.append("{}: {}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]), error))
            context.falseguids.append(elem.GlobalId)

    # write geometry ifc
    if save_geom_ifc:
        name_ifc = "geometry_broken_in_ifcos.ifc"
        path_ifc = join(context.outpath, name_ifc)  # change hardcoded in bimtester_run.py
        print("Save error ifc to: {}".format(path_ifc))
        geom_ifc.write(path_ifc)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The geometry of all {elemcount} {ifc_class} elements have errors."),
        message_some_falseelems=_("The geometry of {falsecount} out of all {elemcount} {ifc_class} elements have errors: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file.")
    )


def eleclass_existing_geometric_representation_has_no_errors(
    context,
    target_ifcos_query
):

    # es wir davon ausgegangen das eine Geometrie vorhanden ist
    # heisst brep is nicht None und nicht "" siehe test vorher
    # wenn keine Geometrie da ist ist das keine Fehler
    # nur eine fehlerhafte Geometrie ist ein Fehler
    #
    # FreeCAD BOP check
    # einige eigene weiterfuehrende checks wie
    # alle kanten haben exakt zwei flaechen (kann oft durch loeschen der flaechen repariert werden)
    # volumen > 10 mm3 wuerfel kantelaenge 2.154 mm
    # kante > 0.2 mm

    # brep aus IfcStore auslesen
    # FreeCAD Part.Shape in IfcStore reinschreiben

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # FreeCAD is needed
    try_to_import_freecad()
    # bernds geometry check is needed
    try:
        from bimstatiktools import geomchecks
    except Exception:
        assert False, (
            "BIMStatik geom check module could not be imported."
            "Thus the test was not performed."
        )

    # create file to save error geometry in there
    geom_ifc = get_new_ifc_file(IfcStore)
    save_geom_ifc = False

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    target_elements = util.minus_elems_without_quantities(target_elements)
    target_elements = util.minus_elems_without_volume(target_elements)

    for elem in target_elements:
        if elem.id() not in IfcStore.geom_freecad_shape:
            # finish test if there is no geometry even for only one object
            finish_test_by_assert_because_no_geometry_data()
        sh = IfcStore.geom_freecad_shape[elem.id()]
        if sh is not None and IfcStore.geom_has_elements[elem.id()] is True:
            error = geomchecks.check_a_geometry_with_elements(sh, tol_length=0.2, tol_volume=10.0)
        else:
            IfcStore.geom_has_errors[elem.id()] = None  # if there is no Shape it can not have errors
            error = ""
            continue

        if error == "":
            IfcStore.geom_has_errors[elem.id()] = False
        else:
            error = error.replace("\n","")  # get rid of middle newlines if more than one error per shape
            IfcStore.geom_has_errors[elem.id()] = True
            # the error is printed in the geomchecks method allready
            # context.falseelems.append(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]))
            # workaround: context.falseprops is not in html report
            # additional spaces in html: https://www.computerhope.com/issues/ch001662.htm geht nicht
            # context.falseelems.append(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]) + "\n &nbsp;&nbsp;&nbsp;&nbsp; Geom. Error: " + error)
            context.falseelems.append("{}: {}".format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]), error))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = error
            # add it to the geom ifc file
            geom_ifc.add(IfcStore.file[elem.id()])
            save_geom_ifc = True

    # write geometry ifc
    if save_geom_ifc:
        name_ifc = "geometry_with_errors.ifc"
        path_ifc = join(context.outpath, name_ifc)  # change hardcoded in bimtester_run.py
        print("Save error ifc to: {}".format(path_ifc))
        geom_ifc.write(path_ifc)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The geometry of all {elemcount} {ifc_class} elements have errors."),
        message_some_falseelems=_("The geometry of {falsecount} out of all {elemcount} {ifc_class} elements have errors: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file.")
    )


def eleclass_existing_geometric_representation_has_max_edge_length(
    context,
    target_ifcos_query,
    str_max_edge_length
):

    max_edge_length = float(str_max_edge_length)

    # es wir davon ausgegangen das eine fehlerfreie Geometrie vorhanden ist
    # heisst brep is nicht None und nicht "" siehe test vorher
    # has errors ist nicht None und nicht True

    # shape aus IfcStore auslesen

    context.falseelems = []
    context.falseguids = []

    # FreeCAD is needed
    try_to_import_freecad()
    try:
        from bimstatiktools import geomchecks
    except Exception:
        assert False, (
            "BIMStatik geom check module could not be imported."
            "Thus the test was not performed."
        )

    # create file to save max edge length geometry in there
    geom_ifc = get_new_ifc_file(IfcStore)
    save_geom_ifc = False

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    target_elements = util.minus_elems_without_quantities(target_elements)
    target_elements = util.minus_elems_without_volume(target_elements)

    for elem in target_elements:
        if elem.id() not in IfcStore.geom_freecad_shape:
            # finish test if there is no geometry even for only one object
            finish_test_by_assert_because_no_geometry_data()
        sh = IfcStore.geom_freecad_shape[elem.id()]
        has_errors = IfcStore.geom_has_errors[elem.id()]
        if sh is not None and has_errors is False:
            if geomchecks.has_short_edges(sh, max_edge_length):
                context.falseelems.append(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]))
                context.falseguids.append(elem.GlobalId)
                # add it to the geom ifc file
                geom_ifc.add(IfcStore.file[elem.id()])
                save_geom_ifc = True

    # write geometry ifc
    if save_geom_ifc:
        name_ifc = "geometry_max_edge_len.ifc"
        path_ifc = join(context.outpath, name_ifc)  # change hardcoded in bimtester_run.py
        print("Save error ifc to: {}".format(path_ifc))
        geom_ifc.write(path_ifc)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The geometry of all {elemcount} {ifc_class} elements have a edge length shorter than {parameter} mm."),
        message_some_falseelems=_("The geometry of {falsecount} out of all {elemcount} {ifc_class} elements have a edge length shorter than {parameter} mm: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=max_edge_length
    )


def eleclass_existing_geometric_representation_has_single_solid(
    context,
    target_ifcos_query
):

    # es wir davon ausgegangen das eine fehlerfreie Geometrie vorhanden ist
    # heisst brep is nicht None und nicht "" siehe test vorher
    # has errors ist nicht None und nicht True

    context.falseelems = []
    context.falseguids = []

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    target_elements = util.minus_elems_without_quantities(target_elements)
    target_elements = util.minus_elems_without_volume(target_elements)

    for elem in target_elements:
        if elem.id() not in IfcStore.geom_freecad_shape:
            # finish test if there is no geometry even for only one object
            finish_test_by_assert_because_no_geometry_data()
        sh = IfcStore.geom_freecad_shape[elem.id()]
        has_errors = IfcStore.geom_has_errors[elem.id()]
        if sh is not None and has_errors is False:
            if len(sh.Solids) > 1:
                context.falseelems.append(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]))
                # context.falseelems.append((str(elem)).replace("\r", " "))
                # happend inside description of vectorworks export
                # print(repr(str(elem)))  # to print the special characters
                context.falseguids.append(elem.GlobalId)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The geometry of all {elemcount} {ifc_class} elements consists of more than one solid."),
        message_some_falseelems=_("The geometry of {falsecount} out of all {elemcount} {ifc_class} elements consists of more than one solid: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file.")
    )


def eleclass_existing_geometric_representation_has_not_opening_bigger_than_element(
    context,
    target_ifcos_query
):

    context.falseelems = []
    context.falseguids = []

    # FreeCAD is needed
    try_to_import_freecad()

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    target_elements = util.minus_elems_without_quantities(target_elements)
    target_elements = util.minus_elems_without_volume(target_elements)

    for elem in target_elements:
        if elem.id() not in IfcStore.geom_freecad_shape:
            # finish test if there is no geometry even for only one object
            finish_test_by_assert_because_no_geometry_data()
        error = ""
        sh = IfcStore.geom_freecad_shape[elem.id()]
        # if sh is not None and len(sh.Vertexes) and IfcStore.geom_has_elements[elem.id()] is False:
        if sh is not None and IfcStore.geom_has_elements[elem.id()] is False:
            # wenn Shape nicht None ist, aber auch keine Elemente hat
            # try without openings
            # wenn eine oeffnung so gross oder groesser als eine wand ist,
            # dann wird eine geometrie ohne inhalt, aber nicht Nullshape
            # zurueckgegeben. dann hat es keine Vertexes
            # bei Archmodellen durchaus ueblich bei Fassaden mit grossen Fenstern
            # habe auch ein bsp von uns wand in wand mit oeffnung, ganz komisch
            # daher aber gut!!!
            brep = get_brep_without_openings_from_ifc_elem(elem)
            if brep:
                shape = get_fc_shape_from_ifcos_brep(brep)
                if shape.Vertexes:
                    context.falseelems.append(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]))
                    context.falseguids.append(elem.GlobalId)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The geometry of all {elemcount} {ifc_class} elements have a geometry which is empty just becaause of a opening bigger than the element."),
        message_some_falseelems=_("The geometry of {falsecount} out of all {elemcount} {ifc_class} elements have a geometry which is  empty just becaause of a opening bigger than the element: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file.")
    )


# ********************************************************************************************
def eleclass_has_given_allplan_to_freecad_volumen_ratio(
    context,
    target_ifcos_query
):
    # es wir davon ausgegangen das eine fehlerfreie Geometrie vorhanden ist
    # heisst brep is nicht None und nicht "" siehe test vorher
    # has errors ist nicht None und nicht True

    context.falseelems = []
    context.falseguids = []

    # create file to save geometry in there
    geom_ifc = get_new_ifc_file(IfcStore)
    save_geom_ifc = False

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:
        if elem.id() not in IfcStore.geom_freecad_shape:
            # finish test if there is no geometry even for only one object
            finish_test_by_assert_because_no_geometry_data()
        sh = IfcStore.geom_freecad_shape[elem.id()]
        has_errors = IfcStore.geom_has_errors[elem.id()]

        # FreeCAD Volumen
        vol_fc = None
        if sh is not None and has_errors is False:
            vol_fc = sh.Volume  # mm3 mit Kommastellen
            vol_fc = round(vol_fc * 1E-9, 6) # in allplan export 6 stellen genauigkeit eingestellt = 1cm3

        # Allplan Volumen
        vol_ap = None
        allpsets = IfcStore.psets[elem.id()]
        # print(allpsets.keys())
        # print(allpsets[std_allplan_psets])
        # print(allpsets[std_allplan_psets]["Allplanvolumen"])
        if (
            std_allplan_psets in allpsets
            and "Allplanvolumen" in allpsets[std_allplan_psets]
        ):
            vol_ap = allpsets[std_allplan_psets]["Allplanvolumen"]

        # datenkontrolle
        # print(elem)
        # print(vol_fc)
        # print(vol_ap)
        if (
            vol_fc is None
            or vol_ap is None
            or vol_fc == 0
            or vol_ap == 0
        ):
            continue
            # das ist kein error, weil das vorhandensein und das Nullsein
            # des Volumen wurde separat geprueft

        # ratio pruefung
        ratio = round(vol_ap / vol_fc, 3)
        # print(ratio)
        if ratio < 0.99 or ratio > 1.01:
            context.falseelems.append(
                "{}, ratio = {}, volume Allplan = {}, volume FreeCAD = {}"
                .format(util.get_false_elem_string(elem, IfcStore.psets[elem.id()]), ratio, vol_ap, vol_fc)
            )
            context.falseguids.append(elem.GlobalId)
            # print(elem)
            # print(vol_fc)
            # print(vol_ap)
            # print(ratio)
            # print("")
            # add it to the geom ifc file
            geom_ifc.add(IfcStore.file[elem.id()])
            save_geom_ifc = True
        else:
            pass
            # separate pruefung

    # write geometry ifc
    if save_geom_ifc:
        name_ifc = "geometry_vol_ratio_Allplan_FreeCAD.ifc"
        path_ifc = join(context.outpath, name_ifc)  # change hardcoded in bimtester_run.py
        print("Save error ifc to: {}".format(path_ifc))
        geom_ifc.write(path_ifc)

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements do have a Allplan volume to FreeCAD volume ration between 99 and 101 prozent."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements do have a Allplan volume to FreeCAD volume ration between 99 and 101 prozent: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=None
    )


def eleclass_has_wall_thickness_valuerange_of(
    context, target_ifcos_query, target_quantity, target_valuerange
):

    # prueft nur den wertebereich, nicht das vorhandensein
    # wenn quantity fehlt ist pruefung bestanden
    #
    # in geompruefung wandeln, oder die geom hinzufuegen, bei geom einfach alle dicken sind fix auf 5 mm exakte zahl
    
    from ast import literal_eval
    target_py_valuerange = literal_eval(target_valuerange)

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    target_qset = "Qto_WallBaseQuantities"
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
                    util.get_false_elem_string(elem, IfcStore.psets[elem.id()]),
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


# ********************************************************************************************
def depricated_eleclass_has_geometric_representation_without_errors(
    context,
    target_ifcos_query
):

    # for history reasons ...

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # FreeCAD is needed
    try_to_import_freecad()

    # bernds geometry check is needed
    try:
        from bimstatiktools import geomchecks
    except Exception:
        assert False, (
            "BIMStatik geom check module could not be imported."
            "Thus the test was not performed."
        )

    target_elements = util.get_elems(IfcStore.file, target_ifcos_query)
    for elem in target_elements:

        shape = get_fc_shape_from_ifc_elem(elem)
        if shape.isNull():
            error = "  IfcOS failed to process the geometric representation."
            print(error)
        else:
            error = geomchecks.check_solid_geometry(shape)

        if error != "":
            # the error is printed in the geomchecks method allready
            # print(error)
            # Part.show(shape)
            #
            # context.falseelems.append(str(elem))
            # problem1
            # context.falseelems.append((str(elem)).replace("\r", " "))
            # happend inside description of vectorworks export
            # print(repr(str(elem)))  # to print the special characters
            #
            # problem2
            # workaround: context.falseprops is not in html report
            # additional spaces in html: https://www.computerhope.com/issues/ch001662.htm geht nicht
            # context.falseelems.append(str(elem) + "\n &nbsp;&nbsp;&nbsp;&nbsp; Geom. Error: " + error)
            # 
            # context.falseelems.append("{} --> {}".format(util.get_false_elem_string(elem), error))
            # context.falseelems.append("Geom. Error: " + error + "\n" + util.get_false_elem_string(elem) + "\n")
            #
            context.falseelems.append("Geom. Error: {}\n{}\n".format(error, util.get_false_elem_string(elem, IfcStore.psets[elem.id()])))

            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = error

    context.elemcount = len(target_elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        target_ifcos_query,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The geometry of all {elemcount} {ifc_class} elements have errors."),
        message_some_falseelems=_("The geometry of {falsecount} out of all {elemcount} {ifc_class} elements have errors: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file.")
    )


# ********************************************************************************************
# ********************************************************************************************
# ********************************************************************************************
# helper


# ********************************************************************************************
def try_to_import_freecad():

    # FreeCAD is needed
    try:
        import FreeCAD
        False if FreeCAD.__name__ else True  # flake8
    except Exception:
        assert False, (
            "FreeCAD python module could not be imported. "
            "Thus the test was not performed."
        )


# ********************************************************************************************
def finish_test_by_assert_because_no_geometry_data():
    # nur der Hauptgeometriecheck erstellt und speichert die geparste Geometrie
    # alle anderen funktionieren nur wenn der auch durchgefuehrt wurde
    assert False, (
        "Index not found in geometry container. "
        "Has main geometry check been activated in feature file?\n"
        "This one:\n"
        'Alle "{ifc_class}" Bauteile haben überhaupt eine Geometrie, die verarbeitet werden kann.\n'
        'All "{ifc_class}" elements must have a geometric representation which could be parsed'
    )


# ********************************************************************************************
def get_new_ifc_file(IfcStore):

   # create new ifc file
    from ifcopenshell import file as init_newifcfile
    new_ifc_file = init_newifcfile(schema=IfcStore.file.schema)
    new_ifc_file.add(IfcStore.file.by_type("IfcProject")[0])
    return new_ifc_file


# ************************************************************************************************
def get_fc_shape_from_ifc_elem(elem):

    brep = get_brep_from_ifc_elem(elem)
    shape = get_fc_shape_from_ifcos_brep(brep)

    return shape


# ************************************************************************************************
def get_fc_shape_from_ifcos_brep(brep):

    import Part
    shape = Part.Shape()  # empty shape (Nullshape)

    if brep:
        shape.importBrepFromString(brep)
        shape.scale(1000.0)  # IfcOpenShell always outputs in meters

    # if brep is None a Nullshape will be returned
    # Nullshape has 0  (Null) solids, but None would give a error if tried to get the solids
    # thus we return a Nullshape

    return shape


# ************************************************************************************************
def get_brep_from_ifc_elem(elem):

    settings = get_ifcos_geom_settings()
    brep = get_brep_from_ifcrepresentation(elem, settings)

    return brep


# ************************************************************************************************
def get_brep_without_openings_from_ifc_elem(elem):

    settings = get_ifcos_geom_settings(substract_openings=True)
    brep = get_brep_from_ifcrepresentation(elem, settings)

    return brep


# ************************************************************************************************
def get_brep_from_ifcrepresentation(elem, settings):

    # TODO: some print and update gui (wir sind in console mode) and or flush

    from ifcopenshell import geom as ifcgeom

    # print("Start reading brep.")
    try:
        # TODO distinguish if there is not representation
        # or ifcos does not return a valid representation
        cr = ifcgeom.create_shape(settings, elem)
        brep = cr.geometry.brep_data
        # print(brep[:75])
    except Exception:
        brep = None
        print("Failed to read the brep. {}".format(elem))

    # keep in mind brep is in m, since ifcopenshell returns in m even if the file in mm

    return brep


# ************************************************************************************************
def get_ifcos_geom_settings(substract_openings=True):

    import ifcopenshell
    from ifcopenshell import geom as ifcgeom
    settings = ifcgeom.settings()

    # get version
    try:
        version = ifcopenshell.version
    except AttributeError:
        version = "not known"
    # print("IfcOpenShell version: {}".format(version))

    # set settings
    if (
        "0.7." in version
        or hasattr(settings, "SEW_SHELLS")  # setting only in 0.7.x available
    ):
        # IfcOpenShell 0.7.0
        settings.set(settings.USE_BREP_DATA, True)
        settings.set(settings.SEW_SHELLS, True)
        settings.set(settings.USE_WORLD_COORDS, True)
        if substract_openings is True:
            settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, False)  # normaly no need to set this
        else:
            settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)  # returns the parent body only

    elif (
        "0.8." in version
        or hasattr(settings, "REORIENT_SHELLS")  # setting only in 0.8.x available
    ):
        # IfcOpenShell 0.8.0
        settings.set('iterator-output', ifcopenshell.ifcopenshell_wrapper.SERIALIZED)
        settings.set('reorient-shells', True)
        settings.set('use-world-coords', True)
        if substract_openings is True:
            settings.set('disable-opening-subtractions', False)  # normaly no need to set this
        else:
            settings.set('disable-opening-subtractions', True)  # returns the parent body only

    else:
        print(
            "IfcOpenShell version is neither 0.7.x nor 0.8.x "
            "You are using a version which this code is not made for. "
            "An empty shape will be returned."
        )

    # output_settings(settings)
    return settings


# ************************************************************************************************
def output_settings(settings):
    for setting in sorted(settings.setting_names()):
        try:
            value = settings.get(setting)
        except Exception:
            value = "not set"
        print("{} --> {}".format(setting, value))
    print("")
