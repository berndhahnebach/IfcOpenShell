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


@step('All "{ifc_class}" elements must have a geometric representation without errors')
def step_impl(context, ifc_class):
    eleclass_has_geometric_representation_without_errors(context, ifc_class)


#`************************************************************************************************
# helper
import gettext  # noqa


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


def eleclass_has_geometric_representation_without_errors(
    context,
    ifc_class
):

    context.falseelems = []
    context.falseguids = []
    context.falseprops = {}

    # FreeCAD is needed
    # TODO import FreeCAD, to be able to run from outside FreeCAD
    try:
        import FreeCAD
        False if FreeCAD.__name__ else True  # flake8
    except Exception:
        assert False, (
            "FreeCAD python module could not be imported. "
            "Thus the test was not performed."
        )

    # bernds geometry check is needed
    # TODO move into FreeCAD main source
    try:
        from bimstatiktools import geomchecks
        # from importlib import reload
        # reload(geomchecks)
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

    elements = IfcStore.file.by_type("IfcBuildingElement")
    for elem in elements:
        # TODO: some print and update gui and or flush, this could take time
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
            error = geomchecks.checkSolidGeometry(shape)
        else:
            error = "  IfcOS failed to process the geometric representation."
        if error != "":
            # the error is printed in the geomchecks method allready
            # print(error)
            Part.show(shape)
            context.falseelems.append(str(elem))
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
