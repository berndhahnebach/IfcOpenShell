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

from bimtester.features.steps.eleclasses_attributes import steptools


@step('All "{ifcos_query}" objects do have a valid value assigned for the attribut Name')
def step_impl(context, ifcos_query):
    steptools.name_attribut_has_valid_value(
        context,
        ifcos_query,
    )


@step('All "{ifcos_query}" objects do have a valid value assigned for the attribut Description')
def step_impl(context, ifcos_query):
    steptools.description_attribut_has_valid_value(
        context,
        ifcos_query,
    )


@step('There are "{ifcos_query}" elements only inside all "{ifc_entity_class}" elements')
def step_impl(context, ifcos_query, ifc_entity_class):
    steptools.entityclass_only(
        context,
        ifcos_query,
        ifc_entity_class,
    )


@step('There are no "{ifcos_query}" elements inside all "{ifc_entity_class}" elements')
def step_impl(context, ifcos_query, ifc_entity_class):
    steptools.no_eleclass(
        context,
        ifcos_query,
        ifc_entity_class,
    )


@step('There are precisely "{count_exact}" "{ifcos_query}" objects')
def step_impl(context, count_exact, ifcos_query):
    steptools.entityclass_count_exact(
        context,
        ifcos_query,
        count_exact,
    )


@step('There are between "{count_min}" and "{count_max}" "{ifcos_query}" objects')
def step_impl(context, count_min, count_max, ifcos_query):
    steptools.entityclass_count_range(
        context,
        ifcos_query,
        count_min,
        count_max,
    )


@step('There are no "{ifcos_query}" elements because "{reason}"')
def step_impl(context, ifcos_query, reason):
    steptools.no_eleclass(
        context,
        ifcos_query,
    )


@step('All "{ifcos_query}" elements class attributes have a value')
def step_impl(context, ifcos_query):
    steptools. eleclass_have_class_attributes_with_a_value(
        context,
        ifcos_query,
    )


@step('All "{ifcos_query}" elements have a Name matching the pattern "{pattern}"')
def step_impl(context, ifcos_query, pattern):
    steptools.eleclass_has_name_matching_pattern(
        context,
        ifcos_query,
        pattern,
    )


@step('All "{ifcos_query}" elements have a Description matching the pattern "{pattern}"')
def step_impl(context, ifcos_query, pattern):
    steptools.eleclass_has_description_matching_pattern(
        context,
        ifcos_query,
        pattern,
    )


@step('All "{ifcos_query}" elements have one of these names "{valuerange}"')
def step_impl(context, ifcos_query, valuerange):
    steptools.eleclass_has_name_valuerange_of(
        context,
        ifcos_query,
        valuerange,
    )
