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


@step('Alle "{ifcos_query}" Bauteile haben exakt "{attribut_count}" Attribute im PSet "{pset}" angehängt')
def step_impl(context, ifcos_query, attribut_count, pset):
    context.execute_steps(f'* All "{ifcos_query}" elements have exactly "{attribut_count}" in the pset "{pset}"')


@step('Alle "{ifcos_query}" Bauteile haben das Attribut "{aproperty}" im PSet "{pset}"')
def step_impl(context, ifcos_query, pset, aproperty):
    context.execute_steps(f'* All "{ifcos_query}" elements have an "{aproperty}" property in the "{pset}" pset')


@step('Alle "{ifcos_query}" Bauteile haben das PSet.Attribut "{pset}.{aproperty}" angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
    context.execute_steps(f'* All "{ifcos_query}" elements have a "{pset}.{aproperty}" property')


@step('Alle "{ifcos_query}" Bauteile haben das PSet.Attribut "{pset}.{aproperty}" nicht angehängt')
def step_impl(context, ifcos_query, pset, aproperty):
    context.execute_steps(f'* All "{ifcos_query}" elements have not a "{pset}.{aproperty}" property')


@step('Alle "{ifcos_query}" Bauteile haben das Attribut "{aproperty}" im Common PSet angehängt')
def step_impl(context, ifcos_queryes, aproperty):
    context.execute_steps(f'* All "{ifcos_query}" elements have a property "{aproperty}" in the Common pset')


@step('Alle "{ifcos_query}" Bauteile mit dem Attribut "{pset}.{aproperty}" haben den Attributtyp "{propertytyp}"')
def step_impl(context, ifcos_query, pset, aproperty, propertytyp):
    context.execute_steps(f'* All "{ifcos_query}" elements with a "{pset}.{aproperty}" are of type "{propertytyp}"')


@step('Alle "{ifcos_query}" Bauteile mit dem Attribut "{pset}.{aproperty}" haben den Attributwert "{propertyvalue}"')
def step_impl(context, ifcos_query, pset, aproperty, propertyvalue):
    context.execute_steps(f'* All "{ifcos_query}" elements with a "{pset}.{aproperty}" have a value of "{propertyvalue}"')


@step('Alle "{ifcos_query}" Bauteile mit dem Attribut "{pset}.{aproperty}" haben nicht den Attributwert "{propertyvalue}"')
def step_impl(context, ifcos_query, pset, aproperty, propertyvalue):
    context.execute_steps(f'* All "{ifcos_query}" elements with a "{pset}.{aproperty}" do not have a value of "{propertyvalue}"')


# depricated (TODO: replace in all feature files)
@step('Alle "{ifcos_query}" Bauteile mit dem Attribut "{pset}.{aproperty}" haben einen Attributwert aus dem Bereich von "{valuerange}"')
def step_impl(context, ifcos_query, pset, aproperty, valuerange):
    context.execute_steps(f'* All "{ifcos_query}" elements with a "{pset}.{aproperty}" have a value range of "{valuerange}"')


@step('Alle "{ifcos_query}" Bauteile mit dem Attribut "{pset}.{aproperty}" haben a einen Attributwert mit dem Muster "{pattern}"')
def step_impl(context, ifcos_query, pset, aproperty, pattern):
    context.execute_steps(f'* All "{ifcos_query}" elements  with a "{pset}.{aproperty}" have a value matching the pattern "{pattern}"')


@step('Alle "{ifcos_query}" Bauteile mit dem angehängten Attribut "{pset}.{aproperty}" verwenden eines der Attributwerte "{valuerange}"')
def step_impl(context, ifcos_query, pset, aproperty, valuerange):
    context.execute_steps(f'* All "{ifcos_query}" elements with a "{pset}.{aproperty}" have a value range of "{valuerange}"')


@step('Alle "{ifcos_query}" Bauteile mit dem angehängten Attribut "{pset}.{aproperty}" nutzten eines der Attributwerte. Alle vorgegebenen Attributwerte werden verwendet. "{valuerange}"')
def step_impl(context, ifcos_query, pset, aproperty, valuerange):
    context.execute_steps(f'* All "{ifcos_query}" elements with a "{pset}.{aproperty}" have a attribute value out of value range. All items of value range have been used "{valuerange}"')


@step('Alle "{ifcos_query}" Bauteile mit dem Attribut "{pset}.{aproperty}" haben die Zeichenfolge "{some_chars}" nicht im Attributwert"')
def step_impl(context, ifcos_query, pset, aproperty, some_chars):
    context.execute_steps(f'* All "{ifcos_query}" elements with a "{pset}.{aproperty}" have the chars "{some_chars}" not in the property value"')


@step('Der Attributewert von "{aproperty1}.{pset1}" stimmt mit dem Attributewert von "{aproperty2}.{pset2}" überein')
def step_impl(context, aproperty1, pset1, aproperty2, pset2):
    context.execute_steps(f'* The attribute value of "{aproperty1}.{pset1}" equals the attribute value of "{aproperty2}.{pset2}" if both are given')
    # "if both are given" im engl. text ist falsch, das sollte in extra tests vorher geprueft werden


@step('Der Wert des Attributes "{pset}.{aproperty}" ist gleich dem Wert des Bauteilattributes Name')
def step_impl(context, pset, aproperty):
    context.execute_steps(f'* The attribute value of "{pset}.{aproperty}" equals the class attribute Name')


@step('Mindestens ein "{ifcos_query}" Bauteil ist ein "{geom_typ}" und hat keine "{prop_typ}" (Bauteilschichtattribute) angehängt')
def step_impl(context, ifcos_query, geom_typ, prop_typ):
    context.execute_steps(f'* At least one "{ifcos_query}" element is a "{geom_typ}" and has no "{prop_typ}" (element layer properties)')


@step('Alle "{ifcos_query}" Bauteile haben keine Bauteilschichtattribute (IfcComplexProperty) angehängt')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements have no element layer properties (IfcComplexProperty)')


# attributvorhandensein in abhangigkeit von material
@step('Alle "{ifcos_query}" Bauteile mit dem Material "{material}" haben das PSet.Attribut "{pset}.{property}" angehängt')
def step_impl(context, ifcos_query, material, pset, property):
    context.execute_steps(f'* All "{ifcos_query}" elements with the material named "{material}" have a "{pset}.{property}" property')


@step('Alle "{ifcos_query}" Bauteile die NICHT das Material "{material}" haben, haben das Attribut.PSet "{pset}.{property}" NICHT angehängt')
def step_impl(context, ifcos_query, material, pset, property):
    context.execute_steps(f'* All "{ifcos_query}" elements which do not have a material named "{material}" have not a "{pset}.{property}" property')


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
