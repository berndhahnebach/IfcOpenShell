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
import ifcopenshell.util.element as eleutils

from behave import step
from behave import use_step_matcher

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('Die IFC-Datei wurde mit dem neuen Allplan Exporter erstellt. Das heisst der data header description hot folgenden Inhalt: "{target_header_file_description}"')
def step_impl(context, target_header_file_description):
    context.execute_steps(f'* The ifc file has been exported with the new Allplan ifc exporter. This means the ifc file data header description is as follows: "{target_header_file_description}"')
