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


@step('Alle "{ifcos_query}" Bauteile haben einen zugeordneten Layer')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements have an layer assigned')


# Alle "{ifcos_query}" Bauteile mit einem zugeordneten Layer, haben nicht den Layeramen "{layer_name}"
@step('Kein "{ifcos_query}" Bauteil hat einen Layer mit dem Namen "{layer_name}"')
def step_impl(context, ifcos_query, layer_name):
    context.execute_steps(f'* No "{ifcos_query}" element has a layer named "{layer_name}"')


@step('Alle "{ifcos_query}" Bauteile mit einem zugeordneten Layer haben den Layernamen "{layer_name}"')
def step_impl(context, ifcos_query, layer_name):
    context.execute_steps(f'* All "{ifcos_query}" elements that have a layer assigned use the layer name "{layer_name}"')


@step('Alle "{ifcos_query}" Bauteile mit einem zugeordneten Layer haben einen der folgenden Layernamen "{valuerange}"')
def step_impl(context, ifcos_query, valuerange):
    context.execute_steps(f'* All "{ifcos_query}" elements that have a layer assigned use one of these layer names "{valuerange}"')
