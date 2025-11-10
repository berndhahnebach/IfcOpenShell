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


@step('Alle "{ifcos_query}" Bauteile haben eine Repräsentation (Geometrie) zugewiesen.')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements must have a representation (geometry) assigned')


@step('Alle "{ifcos_query}" Bauteile verwenden eine geometrische Repräsentation der Klasse "{representation_class}"')
def step_impl(context, ifcos_query, representation_class):
    context.execute_steps(f'* All "{ifcos_query}" elements have an "{representation_class}" representation')


@step('Alle "{ifcos_query}" Bauteile verwenden explixit nicht eine geometrische Repräsentation der Klasse "{representation_class}"')
def step_impl(context, ifcos_query, representation_class):
    context.execute_steps(f'* All "{ifcos_query}" elements do not have an "{representation_class}" representation')
