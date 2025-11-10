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


@step('Es sind nur "{ifcos_query}" Objekte innerhalb der "{ifc_entity_class}" Objekte vorhanden')
def step_impl(context, ifcos_query, ifc_entity_class):
    context.execute_steps(f'* There are "{ifcos_query}" elements only inside all "{ifc_entity_class}" elements')


@step('Es sind keine "{ifcos_query}" Objekte innerhalb der "{ifc_entity_class}" Objekte vorhanden')
def step_impl(context, ifcos_query, ifc_entity_class):
    context.execute_steps(f'* There are no "{ifcos_query}" elements inside all "{ifc_entity_class}" elements')


@step('Im Modell sind exakt "{count_exact}" "{ifc_entity_class}" Objekte vorhanden')
def step_impl(context, count_exact, ifc_entity_class):
    context.execute_steps(f'* In the model are precisely "{count_exact}" "{ifc_entity_class}" objects available')


@step('Im Modell sind zwischen "{count_min}" und "{count_max}" "{ifc_entity_class}" Objekte vorhanden')
def step_impl(context, count_min, count_max, ifc_entity_class):
    context.execute_steps(f'* In the model are between "{count_min}" and "{count_max}" "{ifc_entity_class}" objects available')


@step('Alle "{ifcos_query}" Bauteile haben einen der folgenden Namen "{valuerange}"')
def step_impl(context, ifcos_query, valuerange):
    context.execute_steps(f'* All "{ifcos_query}" elements have one of these names "{valuerange}"')


@step('Aus folgendem Grund gibt es keine "{ifcos_query}" Bauteile: {reason}')
def step_impl(context, ifcos_query, reason):
    context.execute_steps(f'* There are no "{ifcos_query}" elements because "{reason}"')


@step('Alle "{ifcos_query}" Bauteilklassenattribute haben einen Wert')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements class attributes have a value')


@step('Alle "{ifcos_query}" Bauteile haben einen Namen')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements have a name given')


@step('Bei allen "{ifcos_query}" Bauteilen ist die Beschreibung angegeben')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements have a description given')


@step('Alle "{ifcos_query}" Bauteile haben einen Namen mit dem Muster "{pattern}"')
def step_impl(context, ifcos_query, pattern):
    context.execute_steps(f'* All "{ifcos_query}" elements have a name matching the pattern "{pattern}"')
