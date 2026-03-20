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

from bimtester.features.steps.attributes_psets_standard import steptools


@step('All "{ifcos_query}" elements have exactly "{attribut_count}" in the pset "{pset}"')
def step_impl(context, ifcos_query, attribut_count, pset):
    steptools.eleclass_has_propertycount_in_pset(
        context,
        ifcos_query,
        attribut_count,
        pset
    )


@step('All "{ifcos_query}" elements have an "{aproperty}" property in the "{pset}" pset')
def step_impl(context, ifcos_query, pset, aproperty):
    steptools.eleclass_has_property_in_pset(
        context,
        ifcos_query,
        pset,
        aproperty
    )


@step('All "{ifcos_query}" elements have a "{pset}.{aproperty}" property')
def step_impl(context, ifcos_query, pset, aproperty):
    steptools.eleclass_has_property_in_pset(
        context,
        ifcos_query,
        pset,
        aproperty
    )


@step('All "{ifcos_query}" elements have not a "{pset}.{aproperty}" property')
def step_impl(context, ifcos_query, pset, aproperty):
    steptools.eleclass_has_not_property_in_pset(
        context,
        ifcos_query,
        pset,
        aproperty
    )


@step('All "{ifcos_querye}" elements have a property "{aproperty}" in the Common pset')
def step_impl(context, ifcos_querye, aproperty):
    steptools.eleclass_has_property_in_common_pset(
        context,
        ifcos_query,
        aproperty,
    )


@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" are of type "{propertytyp}"')
def step_impl(context, ifcos_query, pset, aproperty, propertytyp):
    steptools.eleclass_has_propertytype_of(
        context,
        ifcos_query,
        pset,
        aproperty,
        propertytyp
    )


@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" have a value of "{propertyvalue}"')
def step_impl(context, ifcos_query, pset, aproperty, propertyvalue):
    steptools.eleclass_has_propertyvalue_of(
        context,
        ifcos_query,
        pset,
        aproperty,
        propertyvalue
    )


@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" do not have a value of "{propertyvalue}"')
def step_impl(context, ifcos_query, pset, aproperty, propertyvalue):
    steptools.eleclass_not_has_propertyvalue_of(
        context,
        ifcos_query,
        pset,
        aproperty,
        propertyvalue 
    )


@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" have a value range of "{valuerange}"')
def step_impl(context, ifcos_query, pset, aproperty, valuerange):
    steptools.eleclass_has_property_valuerange_of(
        context,
        ifcos_query,
        pset,
        aproperty,
        valuerange
    )


@step('All "{ifcos_query}" elements  with a "{pset}.{aproperty}" have a value matching the pattern "{pattern}"')
def step_impl(context, ifcos_query, pset, aproperty, pattern):
    steptools.eleclass_has_property_value_matching_pattern(
        context,
        ifcos_query,
        pset,
        aproperty,
        pattern,
    )


@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" have a attribute value out of value range. All items of value range have been used "{valuerange}"')
def step_impl(context, ifcos_query, pset, aproperty, valuerange):
    steptools.eleclass_has_property_valuerange_of(
        context,
        ifcos_query,
        pset,
        aproperty,
        valuerange,
        all_valuerangeitems_must_be_used=True
    )


# could be used for direkt and layer properties
@step('All "{ifcos_query}" elements with a "{pset}.{aproperty}" have the chars "{some_chars}" not in the property value"')
def step_impl(context, ifcos_query, pset, aproperty, some_chars):
    steptools.eleclass_hasnot_chars_in_property_value(
        context,
        ifcos_query,
        pset,
        aproperty,
        some_chars
    )


@step('The attribute value of "{pset1}.{aproperty1}" equals the attribute value of "{pset2}.{aproperty2}" if both are given')
def step_impl(context, pset1, aproperty1, pset2, aproperty2):
    steptools.propertyvalue1_equals_propertyvalue2(
        context,
        pset1,
        aproperty1,
        pset2,
        aproperty2
    )


@step('The attribute value of "{pset}.{aproperty}" equals the class attribute Name')
def step_impl(context, pset, aproperty):
    steptools.propertyvalue1_equals_elementclassname(
        context,
        pset,
        aproperty
    )


# ************************************************************************************************
# ************************************************************************************************
# ------------------------------------------------------------------------
# STEPS with Regular Expression Matcher ("re")
# ------------------------------------------------------------------------
# TODO ... Steps sind aehnlich, aber nicht identisch ??????

import re

import ifcopenshell.util.element as eleutils
from ifcopenshell.util.element import get_psets

from bimtester.ifc import IfcStore


use_step_matcher("re")


@step("all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property")
def step_impl(context, ifc_class, property_path):
    pset_name, property_name = property_path.split(".")
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        if not IfcStore.get_property(element, pset_name, property_name):
            assert False


@step('all (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property value matching the pattern "(?P<pattern>.*)"')
def step_impl(context, ifc_class, property_path, pattern):

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


@step(r"All (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property")
def step_impl(context, ifc_class, property_path):

    pset, aproperty = property_path.split(".")
    steptools.eleclass_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step(r'All (?P<ifc_class>.*) elements have an? (?P<property_path>.*\..*) property value matching the pattern "(?P<pattern>.*)"')
def step_impl(context, ifc_class, property_path, pattern):

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
