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


# see layer_and_style, features for layer are similar


@step('Alle "{ifcos_query}" Bauteile haben ein zugeordnetes Material')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements have one material assigned')


@step('Kein "{ifcos_query}" Bauteil hat ein Material mit dem Namen "{material_name}"')
def step_impl(context, ifcos_query, material_name):
    context.execute_steps(f'* No "{ifcos_query}" element has a material named "{material_name}"')


@step('Alle "{ifcos_query}" Bauteile mit einem zugeordneten Material haben einen der folgenden Materialnamen "{valuerange}"')
def step_impl(context, ifcos_query, valuerange):
    context.execute_steps(f'* All "{ifcos_query}" elements which have a material assigned use one of these material names "{valuerange}"')
