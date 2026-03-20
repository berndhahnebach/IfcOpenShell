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


@step('Mindestens ein "{ifcos_query}" Bauteil ist ein "{geom_typ}" und hat keine "{prop_typ}" (Bauteilschichtattribute) angehängt')
def step_impl(context, ifcos_query, geom_typ, prop_typ):
    context.execute_steps(f'* At least one "{ifcos_query}" element is a "{geom_typ}" and has no "{prop_typ}" (element layer properties)')


@step('Alle "{ifcos_query}" Bauteile haben keine Bauteilschichtattribute (IfcComplexProperty) angehängt')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements have no element layer properties (IfcComplexProperty)')


"""
# ***************************************************************************************************************
# TODO make a englisch one, ATM not in use
@step('Alle "{ifcos_query}" Bauteile ohne Bauteilschichtattribute haben das Attribut.PSet "{pset}.{aproperty}" angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
    apm.eleclass_without_complexlayerattributes_has_property(
        context,
        ifcos_query,
        aproperty,
        pset
    )


@step('Alle "{ifcos_query}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{pset}.{aproperty}" angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
    apm.eleclass_with_complexlayerattributes_has_property(
        context,
        ifcos_query,
        aproperty,
        pset
    )


# ***************************************************************************************************************
# TODO finish method
@step('Alle "{ifcos_query}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{pset}.{aproperty}" in allen Schichten angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
    apm.eleclass_with_complexlayerattributes_has_property_in_all_layer(
        context,
        ifcos_query,
        aproperty,
        pset
    )


# ***************************************************************************************************************
# TODO implement methods
@step('Alle "{ifcos_query}" Bauteile ohne Bauteilschichtattribute haben das Attribut.PSet "{pset}.{aproperty}" nicht angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
        context,
        ifcos_query,
        aproperty,
        pset
    )


@step('Alle "{ifcos_query}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{pset}.{aproperty}" nicht angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
    apm.eleclass_has_property_implement(
        context,
        ifcos_query,
        aproperty,
        pset
    )


@step('Alle "{ifcos_query}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{pset}.{aproperty}" nicht in irgendeiner Schicht angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
    apm.eleclass_has_property_implement(
        context,
        ifcos_query,
        aproperty,
        pset
    )


# ***************************************************************************************************************
# TODO, Beginn old, pruefen was funktioniert
@step('Alle "{ifcos_query}" Bauteile haben das Attribut.PSet "{pset}.{aproperty}" ausschliesslich direkt angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
    apm.eleclass_has_property_directly_in_pset(
        context,
        ifcos_query,
        aproperty,
        pset
    )


@step('Alle "{ifcos_query}" Bauteile haben das Attribut.PSet "{pset}.{aproperty}" nicht direkt angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
    apm.eleclass_has_not_property_directly_in_pset(
        context,
        ifcos_query,
        aproperty,
        pset
    )


@step('Alle "{ifcos_query}" Bauteilschichten haben das Attribut.PSet "{pset}.{aproperty}" angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
    apm.eleclass_matlayer_has_property_in_pset(
        context,
        ifcos_query,
        aproperty,
        pset
    )

@step('Bis auf "{minus_ifcos_query}" Bauteile haben alle "{ifcos_query}" das Attribut.PSet "{pset}.{aproperty}" direkt angehängt')
def step_impl(context, ifcos_query, minus_ifcos_query, pset, aproperty):
    apm.eleclass_has_property_in_pset(
        context,
        ifcos_query,
        aproperty,
        pset,
        minus_ifcos_query # different oder!
    )


@step('Alle "{ifcos_query}" Bauteile haben das Attribut.PSet "{pset}.{aproperty}" in einer Bauteilschicht angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
    apm.eleclass_has_property_in_layer_in_pset(
        context,
        ifcos_query,
        aproperty,
        pset
    )
# Ende old, pruefen was funktioniert
# *************************************
"""
