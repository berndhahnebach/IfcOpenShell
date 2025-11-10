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


@step('Alle "{ifc_class}" Bauteile mit einem zugeordneten Material haben einen der folgenden Materialnamen "{valuerange}"')
def step_impl(context, ifc_class, valuerange):
    context.execute_steps(f'* All "{ifc_class}" elements which have a material assigned use one of these material names "{valuerange}"')


@step('Alle "{ifc_class}" Bauteile haben ein zugeordnetes Material')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements have one material assigned')


@step('Kein "{ifc_class}" Bauteil hat ein Material mit dem Namen "{material_name}"')
def step_impl(context, ifc_class, material_name):
    context.execute_steps(f'* No "{ifc_class}" element has a material named "{material_name}"')
