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


@step('Alle "{ifcos_query}" Bauteile haben im Allplan-Volumen einen Propertywert der grösser als 0.0 ist.')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements must have a Allplan volume greater than 0.0.')
    # Allplan volume is hard coded


@step('Alle "{ifcos_query}" Bauteile haben überhaupt eine Geometrie, die verarbeitet werden kann.')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements must have a geometric representation which could be parsed')


@step('Alle "{ifcos_query}" Bauteile haben eine Geometrie ohne Fehler.')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements with existing geometry have no errors')


@step('Alle "{ifcos_query}" Bauteile haben in ihrer Geometrie eine maximale Kantenlänge von "{max_edge_length}" mm.')
def step_impl(context, ifcos_query, max_edge_length):
    context.execute_steps(f'* All "{ifcos_query}" elements must have a maximum edge length of "{max_edge_length}" mm in their geometry')


@step('Alle "{ifcos_query}" Bauteile haben eine Geometrie welche nur aus einem Volumenkörper besteht.')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements must have a geometry consisting only one volume solid')


@step('Alle "{ifcos_query}" Bauteile haben eine Geometrie die nicht leer ist, weil eine Öffnung das gesamte Bauteil beinhaltet.')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements must have a geometry which is not empty just becaause of a opening bigger than the element')


@step('Alle "{ifcos_query}" Bauteile haben ein Allplan-Volumen zu FreeCAD-Volumen ratio zwischen 99 und 101 Prozent.')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements must have a Allplan volume to FreeCAD volume ratio between 99 und 101 prozent.')
    # Allplan volume is hard coded


@step('Alle "{ifcos_query}" Bauteile haben ausschliesslich eine "{aquantity}" der Werte "{valuerange}"')
def step_impl(context, ifcos_query, aquantity, valuerange):
    context.execute_steps(f'* All "{ifcos_query}" elements do only have the "{aquantity}" value range of "{valuerange}"')


# deprecated
@step('Alle "{ifcos_query}" Bauteile haben eine geometrische Repräsentation ohne Fehler')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements must have a geometric representation without errors')
