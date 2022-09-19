from behave import step

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('IFC data must use the "{schema}" schema')
def step_impl(context, schema):
    has_ifcdata_specific_schema(context, schema)


@step('The ifc data uses exact "{unit_count}" units of unit type "{unit_type}"')
def step_impl(context, unit_count, unit_type):
    has_ifcdata_specific_unit_type_count(context, unit_count, unit_type)


@step('A "{unit_type}" is of type "{ifc_type}" and is named "{unit_name}"')
def step_impl(context, unit_type, ifc_type, unit_name):
    has_a_unit_spcific_type_and_name(context, unit_type, ifc_type, unit_name)


@step('A "{unit_type}" named "{unit_name}" uses the prefix "{unit_prefix}"')
def step_impl(context, unit_type, unit_name, unit_prefix):
    has_a_unit_type_and_name_a_spcific_prefix(context, unit_type, unit_name, unit_prefix)


@step("The IFC file must be valid")
def step_impl(context):
    errors = util.validate(IfcStore.file)
    assert not errors, "Errors occured:\n{}".format("\n".join(errors))


@step('The IFC file "{file}" is exempt from being provided')
def step_impl(context, file):
    pass


@step('No further requirements are specified because "{reason}"')
def step_impl(context, reason):
    pass


@step('The project must have an identifier of "{guid}"')
def step_impl(context, guid):
    util.assert_attribute(IfcStore.file.by_type("IfcProject")[0], "GlobalId", guid)


@step('The project name, code, or short identifier must be "{value}"')
def step_impl(context, value):
    util.assert_attribute(IfcStore.file.by_type("IfcProject")[0], "Name", value)


@step('The project must have a longer form name of "{value}"')
def step_impl(context, value):
    util.assert_attribute(IfcStore.file.by_type("IfcProject")[0], "LongName", value)


@step('The project must be described as "{value}"')
def step_impl(context, value):
    util.assert_attribute(IfcStore.file.by_type("IfcProject")[0], "Description", value)


@step('The project must be categorised under "{value}"')
def step_impl(context, value):
    util.assert_attribute(IfcStore.file.by_type("IfcProject")[0], "ObjectType", value)


@step('The project must contain information about the "{value}" phase')
def step_impl(context, value):
    util.assert_attribute(IfcStore.file.by_type("IfcProject")[0], "Phase", value)


@step("The project must contain 3D geometry representing the shape of objects")
def step_impl(context):
    assert get_subcontext("Body", "Model", "MODEL_VIEW")


@step("The project must contain 3D geometry representing clearance zones")
def step_impl(context):
    assert get_subcontext("Clearance", "Model", "MODEL_VIEW")


@step("The project must contain 3D geometry representing the center of gravity of objects")
def step_impl(context):
    assert get_subcontext("CoG", "Model", "MODEL_VIEW")


@step("The project must contain 3D geometry representing the object bounding boxes")
def step_impl(context):
    assert get_subcontext("Box", "Model", "MODEL_VIEW")


def get_subcontext(identifier, type, target_view):
    project = IfcStore.file.by_type("IfcProject")[0]
    for rep_context in project.RepresentationContexts:
        for subcontext in rep_context.HasSubContexts:
            if (
                subcontext.ContextIdentifier == identifier
                and subcontext.ContextType == type
                and subcontext.TargetView == target_view
            ):
                return True
    assert False, "The subcontext with identifier {}, type {}, and target view {} could not be found".format(
        identifier, type, target_view
    )


@step('the project has a {attribute_name} attribute with a value of "{attribute_value}"')
def step_impl(context, attribute_name, attribute_value):
    project = IfcStore.file.by_type("IfcProject")[0]
    assert getattr(project, attribute_name) == attribute_value


# ************************************************************************************************
# helper
def has_ifcdata_specific_schema(context, target_schema):

    actual_schema = IfcStore.file.schema

    if actual_schema != target_schema:
        # -- SKIP: Remaining steps in current feature.
        context.feature.skip("Wrong IFC-Schema, abort.")

    assert actual_schema == target_schema, (
        _("We expected a schema of {} but instead got {}")
        .format(target_schema, actual_schema)
    )


def has_ifcdata_specific_unit_type_count(context, target_unit_count, target_unit_type):

    print("has_ifcdata_specific_unit_type_count")


def has_a_unit_spcific_type_and_name(context, target_unit_type, target_ifc_type, target_unit_name):

    print("has_a_unit_spcific_type_and_name")


def has_a_unit_type_and_name_a_spcific_prefix(context, target_unit_type, target_unit_name, target_unit_prefix):

    print("has_a_unit_type_and_name_a_spcific_prefix")



# ************************************************************************************************
# ************************************************************************************************
# https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/ifcmeasureresource/lexical/ifcsiunit.htm
"""
Am besten alles separat abfragen
#12=IfcSIUnit(*,.LENGTHUNIT.,$,.METRE.)
id --> 12
type --> IfcSIUnit
Dimensions --> None
UnitType --> LENGTHUNIT
Prefix --> None
Name --> METRE

Die IFC-Daten haben genau "1" Einheit(en) des Einheitentypes "LENGTHUNIT"
Eine "LENGTHUNIT" hat den Typ "IfcSIUnit" und den Namen "METRE"
Eine "LENGTHUNIT" mit dem Namen "METRE" hat den Prefix ""
"""

