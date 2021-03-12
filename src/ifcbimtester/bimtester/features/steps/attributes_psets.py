import gettext
from behave import step

import attributes_psets_methods as apm
from utils import assert_elements
from utils import IfcFile
from utils import switch_locale


the_lang = "en"


@step('All "{ifc_class}" elements have a "{aproperty}.{pset}" property')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('All "{ifc_class}" elements with the property "{aproperty}.{pset}" should have the value of "{value}"')
def step_impl(context, ifc_class, aproperty, pset, value):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_value_of(
        context,
        ifc_class,
        aproperty,
        pset,
        value
    )


@step('All "{ifc_class}" elements with the property "{aproperty}.{pset}" should have the value type of "{valuetype}"')
def step_impl(context, ifc_class, aproperty, pset, valuetype):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_valuetype_of(
        context,
        ifc_class,
        aproperty,
        pset,
        valuetype
    )


@step('The attribute value of "{aproperty1}.{pset1}" equals the attribute value of "{aproperty2}.{pset2}" if both are given')
def step_impl(context, aproperty1, pset1, aproperty2, pset2):
    switch_locale(context.localedir, the_lang)
    apm.propertyvalue1_equals_propertyvalue2(
        context,
        aproperty1,
        pset1,
        aproperty2,
        pset2
    )


@step('The attribute value of "{aproperty}.{pset}" equals the class attribute Name')
def step_impl(context, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.propertyvalue1_equals_elementclassname(
        context,
        aproperty,
        pset
    )


# ------------------------------------------------------------------------
# STEPS with Regular Expression Matcher ("re")
# ------------------------------------------------------------------------
use_step_matcher("re")


@step("all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property")
def step_impl(context, ifc_class, property_path):
    pset_name, property_name = property_path.split(".")
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        if not IfcFile.get_property(element, pset_name, property_name):
            assert False


@step(
    'all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property value matching the pattern "(?P<pattern>.*)"'
)
def step_impl(context, ifc_class, property_path, pattern):
    import re

    pset_name, property_name = property_path.split(".")
    elements = IfcFile.get().by_type(ifc_class)
    for element in elements:
        prop = IfcFile.get_property(element, pset_name, property_name)
        if not prop:
            assert False
        # For now, we only check single values
        if prop.is_a("IfcPropertySingleValue"):
            if not (prop.NominalValue and re.search(pattern, prop.NominalValue.wrappedValue)):
                assert False
