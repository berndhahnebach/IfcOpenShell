from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('All elements must be under "{number}" polygons')
def step_impl(context, number):
    number = int(number)
    errors = []
    for element in IfcStore.file.by_type("IfcElement"):
        if not element.Representation:
            continue
        total_polygons = 0
        tree = IfcStore.file.traverse(element.Representation)
        for e in tree:
            if e.is_a("IfcFace"):
                total_polygons += 1
            elif e.is_a("IfcPolygonalFaceSet"):
                total_polygons += len(e.Faces)
            elif e.is_a("IfcTriangulatedFaceSet"):
                total_polygons += len(e.CoordIndex)
        if total_polygons > number:
            errors.append((total_polygons, element))
    if errors:
        message = "The following {} elements are over 500 polygons:\n".format(len(errors))
        for error in errors:
            message += "Polygons: {} - {}\n".format(error[0], error[1])
        assert False, message


@step('All "{ifc_class}" elements have an "{representation_class}" representation')
def step_impl(context, ifc_class, representation_class):
    eleclass_has_geometric_representation_of_specific_class(
        context,
        ifc_class,
        representation_class
    )


@step('All "{ifc_class}" elements must have a geometric representation which could be parsed')
def step_impl(context, ifc_class):
    eleclass_has_geometric_representation_parsed_by_ifcos(context, ifc_class)


@step('All "{ifc_class}" elements with existing geometry have no errors')
def step_impl(context, ifc_class):
    eleclass_existing_geometric_representation_has_no_errors(context, ifc_class)


@step('All "{ifc_class}" elements must have a maximum edge length of "{max_edge_length}" mm in their geometry')
def step_impl(context, ifc_class, max_edge_length):
    eleclass_existing_geometric_representation_has_max_edge_length(context, ifc_class, max_edge_length)


@step('All "{ifc_class}" elements must have a geometry consisting only one volume solid')
def step_impl(context, ifc_class):
    eleclass_existing_geometric_representation_has_single_solid(context, ifc_class)


@step('All "{ifc_class}" elements must have a geometry which is not empty just becaause of a opening bigger than the element')
def step_impl(context, ifc_class):
    eleclass_existing_geometric_representation_has_not_opening_bigger_than_element(context, ifc_class)


# deprecated
@step('All "{ifc_class}" elements must have a geometric representation without errors')
def step_impl(context, ifc_class):
    depricated_eleclass_has_geometric_representation_without_errors(context, ifc_class)


# ************************************************************************************************
# helper
def eleclass_has_geometric_representation_of_specific_class(
    context,
    ifc_class,
    representation_class
):

    def is_item_a_representation(item, representation):
        if "/" in representation:
            for cls in representation.split("/"):
                if item.is_a(cls):
                    return True
        elif item.is_a(representation):
            return True

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}
    rep = None

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        if not elem.Representation:
            continue
        has_representation = False
        for representation in elem.Representation.Representations:
            for item in representation.Items:
                if item.is_a("IfcMappedItem"):
                    # We only check one more level deep.
                    for item2 in item.MappingSource.MappedRepresentation.Items:
                        if is_item_a_representation(item2, representation_class):
                            has_representation = True
                        rep = item2
                else:
                    if is_item_a_representation(item, representation_class):
                        has_representation = True
                    rep = item
        if not has_representation:
            context.falseelems.append(str(elem))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = str(rep)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("All {elemcount} {ifc_class} elements are not a {parameter} representation."),
        message_some_falseelems=_("The following {falsecount} of {elemcount} {ifc_class} elements are not a {parameter} representation: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file."),
        parameter=representation_class
    )


def eleclass_has_geometric_representation_parsed_by_ifcos(
    context,
    ifc_class
):

    # IfcOpenShell returns a brep which does include geometric elements
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

    from ifcopenshell import geom as ifcgeom
    settings = ifcgeom.settings()
    settings.set(settings.USE_BREP_DATA, True)
    settings.set(settings.SEW_SHELLS, True)
    settings.set(settings.USE_WORLD_COORDS, True)

    # FreeCAD is needed
    try:
        import FreeCAD
        False if FreeCAD.__name__ else True  # flake8
    except Exception:
        assert False, (
            "FreeCAD python module could not be imported. "
            "Thus the test was not performed."
        )
    import Part

    # create file to save bad geometry in there
    from ifcopenshell import file as init_newifcfile
    error_ifc = init_newifcfile(schema=IfcStore.file.schema)
    error_ifc.add(IfcStore.file.by_type("IfcProject")[0])
    save_error_ifc = False

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:

        if extended_prints is True:
            print(elem)
            sys.stdout.flush()  # if BIMTester crashes it is seen on which file
            # continue

        error = ""
        try:
            cr = ifcgeom.create_shape(settings, elem)
            brep = cr.geometry.brep_data
        except Exception:
            brep = None
            shape = None
            IfcStore.geom_has_elements[elem.id()] = None
            error = "The parser failed at all to process the geometric representation."
            # add it to the error ifc file
            error_ifc.add(IfcStore.file[elem.id()])
            save_error_ifc = True

        if extended_prints is True:
            print("brep creation did not crash.")
            sys.stdout.flush()  # if BIMTester crashes it is seen on which file

        if brep is not None:
            shape = Part.Shape()
            shape.importBrepFromString(brep)
            # bei den obigen koennte es auch probleme geben, das waren dann aber ifcos oder fc probleme
            shape.scale(1000.0)  # IfcOpenShell always outputs in meters
            if shape.isNull():
                error = "Nullshape"  # ich glaube das geht gar nicht, ifcos gibt nie eine Nullshape zurück
                IfcStore.geom_has_elements[elem.id()] = False
            elif not shape.Vertexes:
                error = "No Vertexes"
                IfcStore.geom_has_elements[elem.id()] = False
                # try without openings
                # wenn eine oeffnung so gross oder groesser als eine wand ist,
                # dann wird eine geometrie ohne inhalt, aber nicht Nullshape
                # zurueckgegeben. dann hat es keine Vertexes
                # bei Archmodellen durchaus ueblich bei Fassaden mit grossen Fenstern
                # habe auch ein bsp von uns wand in wand mit oeffnung, ganz komisch
                # daher aber gut!!!
                # TODO: separaten Test erstellen fuer leere Geometrieen und Aussparungen
                settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)
                try:
                    cr = ifcgeom.create_shape(settings, elem)
                    brep = cr.geometry.brep_data
                except Exception:
                    brep = None
                if brep:
                    shape = Part.Shape()
                    shape.importBrepFromString(brep)
                    shape.scale(1000.0)  # IfcOpenShell always outputs in meters
                    if shape.Vertexes:
                        error = ""
                        # error = "Oeffnung groesser als Objekt, daher keine Geometrie."
                # set back to triangulate with openings
                settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, False)
            else:
                IfcStore.geom_has_elements[elem.id()] = True

        IfcStore.geom_freecad_shape[elem.id()] = shape

        if error != "":
            context.falseelems.append("{},{} --> {}".format(elem.GlobalId, elem.is_a(), error))
            context.falseguids.append(elem.GlobalId)

    # write error ifc
    if save_error_ifc:
        from os.path import join
        path_error_ifc = join(context.outpath, "errorlog_geometry_parse_ifcos.ifc")
        print("Save error ifc to: {}".format(path_error_ifc))
        error_ifc.write(path_error_ifc)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The geometry of all {elemcount} {ifc_class} elements have errors."),
        message_some_falseelems=_("The geometry of {falsecount} out of all {elemcount} {ifc_class} elements have errors: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file.")
    )


def eleclass_existing_geometric_representation_has_no_errors(
    context,
    ifc_class
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
    try:
        import FreeCAD
        False if FreeCAD.__name__ else True  # flake8
    except Exception:
        assert False, (
            "FreeCAD python module could not be imported. "
            "Thus the test was not performed."
        )
    # bernds geometry check is needed
    try:
        from bimstatiktools import geomchecks
    except Exception:
        assert False, (
            "BIMStatik geom check module could not be imported."
            "Thus the test was not performed."
        )

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
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
            # context.falseelems.append(str(elem))
            # workaround: context.falseprops is not in html report
            # additional spaces in html: https://www.computerhope.com/issues/ch001662.htm geht nicht
            # context.falseelems.append(str(elem) + "\n &nbsp;&nbsp;&nbsp;&nbsp; Geom. Error: " + error)
            context.falseelems.append("{},{} --> {}".format(elem.GlobalId, elem.is_a(), error))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = error

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The geometry of all {elemcount} {ifc_class} elements have errors."),
        message_some_falseelems=_("The geometry of {falsecount} out of all {elemcount} {ifc_class} elements have errors: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file.")
    )


def eleclass_existing_geometric_representation_has_max_edge_length(
    context,
    ifc_class,
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
    try:
        import FreeCAD
        False if FreeCAD.__name__ else True  # flake8
    except Exception:
        assert False, (
            "FreeCAD python module could not be imported. "
            "Thus the test was not performed."
        )
    try:
        from bimstatiktools import geomchecks
    except Exception:
        assert False, (
            "BIMStatik geom check module could not be imported."
            "Thus the test was not performed."
        )

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        if elem.id() not in IfcStore.geom_freecad_shape:
            # finish test if there is no geometry even for only one object
            finish_test_by_assert_because_no_geometry_data()
        sh = IfcStore.geom_freecad_shape[elem.id()]
        has_errors = IfcStore.geom_has_errors[elem.id()]
        if sh is not None and has_errors is False:
            if geomchecks.has_short_edges(sh, max_edge_length):
                context.falseelems.append((str(elem)).replace("\r", " "))
                # happend inside description of vectorworks export
                # print(repr(str(elem)))  # to print the special characters
                context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
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
    ifc_class
):

    # es wir davon ausgegangen das eine fehlerfreie Geometrie vorhanden ist
    # heisst brep is nicht None und nicht "" siehe test vorher
    # has errors ist nicht None und nicht True

    context.falseelems = []
    context.falseguids = []

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        if elem.id() not in IfcStore.geom_freecad_shape:
            # finish test if there is no geometry even for only one object
            finish_test_by_assert_because_no_geometry_data()
        sh = IfcStore.geom_freecad_shape[elem.id()]
        has_errors = IfcStore.geom_has_errors[elem.id()]
        if sh is not None and has_errors is False:
            if len(sh.Solids) > 1:
                context.falseelems.append((str(elem)).replace("\r", " "))
                # happend inside description of vectorworks export
                # print(repr(str(elem)))  # to print the special characters
                context.falseguids.append(elem.GlobalId)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The geometry of all {elemcount} {ifc_class} elements consists of more than one solid."),
        message_some_falseelems=_("The geometry of {falsecount} out of all {elemcount} {ifc_class} elements consists of more than one solid: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file.")
    )


def eleclass_existing_geometric_representation_has_not_opening_bigger_than_element(
    context,
    ifc_class
):

    context.falseelems = []
    context.falseguids = []

    from ifcopenshell import geom as ifcgeom
    settings = ifcgeom.settings()
    settings.set(settings.USE_BREP_DATA, True)
    settings.set(settings.SEW_SHELLS, True)
    settings.set(settings.USE_WORLD_COORDS, True)

    # FreeCAD is needed
    try:
        import FreeCAD
        False if FreeCAD.__name__ else True  # flake8
    except Exception:
        assert False, (
            "FreeCAD python module could not be imported. "
            "Thus the test was not performed."
        )
    import Part

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        if elem.id() not in IfcStore.geom_freecad_shape:
            # finish test if there is no geometry even for only one object
            finish_test_by_assert_because_no_geometry_data()
        error = ""
        sh = IfcStore.geom_freecad_shape[elem.id()]
        if sh is not None and len(sh.Vertexes) and IfcStore.geom_has_elements[elem.id()] is False:
            # try without openings
            # wenn eine oeffnung so gross oder groesser als eine wand ist,
            # dann wird eine geometrie ohne inhalt, aber nicht Nullshape
            # zurueckgegeben. dann hat es keine Vertexes
            # bei Archmodellen durchaus ueblich bei Fassaden mit grossen Fenstern
            # habe auch ein bsp von uns wand in wand mit oeffnung, ganz komisch
            # daher aber gut!!!
            settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)
            try:
                cr = ifcgeom.create_shape(settings, elem)
                brep = cr.geometry.brep_data
            except Exception:
                brep = None
            if brep:
                shape = Part.Shape()
                shape.importBrepFromString(brep)
                shape.scale(1000.0)  # IfcOpenShell always outputs in meters
                if shape.Vertexes:
                    context.falseelems.append((str(elem)).replace("\r", " "))
                    # happend inside description of vectorworks export
                    # print(repr(str(elem)))  # to print the special characters
                    context.falseguids.append(elem.GlobalId)
            # set back to triangulate with openings
            settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, False)

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The geometry of all {elemcount} {ifc_class} elements have a geometry which is empty just becaause of a opening bigger than the element."),
        message_some_falseelems=_("The geometry of {falsecount} out of all {elemcount} {ifc_class} elements have a geometry which is  empty just becaause of a opening bigger than the element: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file.")
    )


# ********************************************************************************************
def depricated_eleclass_has_geometric_representation_without_errors(
    context,
    ifc_class
):

    # for history reasons ...

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # FreeCAD is needed
    try:
        import FreeCAD
        False if FreeCAD.__name__ else True  # flake8
    except Exception:
        assert False, (
            "FreeCAD python module could not be imported. "
            "Thus the test was not performed."
        )

    # bernds geometry check is needed
    try:
        from bimstatiktools import geomchecks
    except Exception:
        assert False, (
            "BIMStatik geom check module could not be imported."
            "Thus the test was not performed."
        )

    import Part
    from ifcopenshell import geom as ifcgeom
    settings = ifcgeom.settings()
    settings.set(settings.USE_BREP_DATA, True)
    settings.set(settings.SEW_SHELLS, True)
    settings.set(settings.USE_WORLD_COORDS, True)

    elements = IfcStore.file.by_type(ifc_class)
    for elem in elements:
        # TODO: some print and update gui (wir sind in console mode) and or flush
        try:
            # TODO distinguish if there is not representation
            # or ifcos does not return a valid representation
            cr = ifcgeom.create_shape(settings, elem)
            brep = cr.geometry.brep_data
        except Exception:
            brep = None
        if brep:
            shape = Part.Shape()
            shape.importBrepFromString(brep)
            shape.scale(1000.0)  # IfcOpenShell always outputs in meters
            error = geomchecks.check_solid_geometry(shape)
        else:
            error = "  IfcOS failed to process the geometric representation."
        if error != "":
            # the error is printed in the geomchecks method allready
            # print(error)
            Part.show(shape)
            # context.falseelems.append(str(elem))
            # workaround: context.falseprops is not in html report
            # additional spaces in html: https://www.computerhope.com/issues/ch001662.htm geht nicht
            # context.falseelems.append(str(elem) + "\n &nbsp;&nbsp;&nbsp;&nbsp; Geom. Error: " + error)
            # context.falseelems.append("Geom. Error: " + error + "\n" + str(elem) + "\n")
            context.falseelems.append("{},{} --> {}".format(elem.GlobalId, elem.is_a(), error))
            context.falseguids.append(elem.GlobalId)
            context.falseprops[elem.id()] = error

    context.elemcount = len(elements)
    context.falsecount = len(context.falseelems)
    util.assert_elements(
        ifc_class,
        context.elemcount,
        context.falsecount,
        context.falseelems,
        message_all_falseelems=_("The geometry of all {elemcount} {ifc_class} elements have errors."),
        message_some_falseelems=_("The geometry of {falsecount} out of all {elemcount} {ifc_class} elements have errors: {falseelems}"),
        message_no_elems=_("There are no {ifc_class} elements in the IFC file.")
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
