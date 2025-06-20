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

from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('The IFC file must be exported by application full name "{fullname}"')
def step_impl(context, fullname):

    real_fullname = IfcStore.file.by_type("IfcApplication")[0].ApplicationFullName
    assert  real_fullname == fullname , (
        "The IFC file was not exported by application full name {} "
        "instead it was exported by application full name {}"
        .format(fullname, real_fullname)
    )


@step('The IFC file must be exported by application identifier "{identifier}"')
def step_impl(context, identifier):

    real_identifier = IfcStore.file.by_type("IfcApplication")[0].ApplicationIdentifier
    assert  real_identifier == identifier , (
        "The IFC file was not exported by application identifier {} "
        "instead it was exported by identifier {}"
        .format(identifier, real_identifier)
    )


@step('The IFC file must be exported by the application version "{version}"')
def step_impl(context, version):

    real_version = IfcStore.file.by_type("IfcApplication")[0].Version
    assert  real_version == version , (
        "The IFC file was not exported by application version {} "
        "instead it was exported by version {}"
        .format(version, real_version)
    )


@step('IFC data header must have a file description of "{header_file_description}"')
def step_impl(context, header_file_description):

    actual_header_file_description = str(IfcStore.file.wrapped_data.header.file_description.description)
    assert  actual_header_file_description == header_file_description , (
        "The file was not exported by the new ifc exporter in Allplan. File description header: {}"
        .format(actual_header_file_description)
    )


@step('The ifc file has been exported with the new Allplan ifc exporter. This means the ifc file data header description is as follows: "{target_header_file_description}"')
def step_impl(context, target_header_file_description):

    actual_header_file_description = str(IfcStore.file.wrapped_data.header.file_description.description)
    # print(len(actual_header_file_description))
    # print(actual_header_file_description)
    # print(len(target_header_file_description))
    # print(target_header_file_description)

    if actual_header_file_description != target_header_file_description:
        # -- SKIP: Remaining steps in current feature.
        context.feature.skip("Deprecated Allplan ifc exporter, abort.")

    assert actual_header_file_description == target_header_file_description, (
        _("The ifc data has not been exported with the updatodate Allplan ifc exporter. Ifc data header description: {} != {}: target ifc data header description")
        .format(actual_header_file_description, target_header_file_description)
    )
