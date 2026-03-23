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



@step('Alle "{ifcos_query}" Objekte haben einen gültigen Wert für das Attribut Name zugewiesen')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" objects do have a valid value assigned for the attribut Name')


@step('Alle "{ifcos_query}" Objekte haben einen gültigen Wert für das Attribut Description zugewiesen')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" objects do have a valid value assigned for the attribut Description')


@step('Es sind nur "{ifcos_query}" Objekte innerhalb der "{ifc_entity_class}" Objekte vorhanden')
def step_impl(context, ifcos_query, ifc_entity_class):
    context.execute_steps(f'* There are "{ifcos_query}" elements only inside all "{ifc_entity_class}" elements')


@step('Es sind keine "{ifcos_query}" Objekte innerhalb der "{ifc_entity_class}" Objekte vorhanden')
def step_impl(context, ifcos_query, ifc_entity_class):
    context.execute_steps(f'* There are no "{ifcos_query}" elements inside all "{ifc_entity_class}" elements')


@step('Es sind gar keine "{ifcos_query}" Objekte vorhanden. Das hat foldenden Grund: {reason}')
def step_impl(context, ifcos_query, reason):
    context.execute_steps(f'* There are no "{ifcos_query}" elements because "{reason}"')


@step('Es gibt exakt "{count_exact}" "{ifcos_query}" Objekte')
def step_impl(context, count_exact, ifcos_query):
    context.execute_steps(f'* There are precisely "{count_exact}" "{ifcos_query}" objects')


@step('Es gibt zwischen "{count_min}" und "{count_max}" "{ifcos_query}" Objekte')
def step_impl(context, count_min, count_max, ifcos_query):
    context.execute_steps(f'* There are between "{count_min}" and "{count_max}" "{ifcos_query}" objects')


@step('Alle "{ifcos_query}" Bauteile haben einen der folgenden Namen "{valuerange}"')
def step_impl(context, ifcos_query, valuerange):
    context.execute_steps(f'* All "{ifcos_query}" elements have one of these names "{valuerange}"')


@step('Alle "{ifcos_query}" Bauteile haben einen Namen mit dem Muster "{pattern}"')
def step_impl(context, ifcos_query, pattern):
    context.execute_steps(f'* All "{ifcos_query}" elements have a name matching the pattern "{pattern}"')
