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


# ToDo, switch from Attribut to Property
# link good german artikle


# ************************************************************************************************
# vorhandensein von Properties


@step('Alle "{ifcos_query}" Bauteile haben exakt "{attribut_count}" Attribute im PSet "{pset}" angehängt')
def step_impl(context, ifcos_query, attribut_count, pset):
    context.execute_steps(f'* All "{ifcos_query}" elements have exactly "{attribut_count}" in the pset "{pset}"')


# doppelt
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


# ************************************************************************************************
# datentyp der Propertywerte


@step('Alle "{ifcos_query}" Bauteile mit dem Attribut "{pset}.{aproperty}" haben den Attributtyp "{propertytyp}"')
def step_impl(context, ifcos_query, pset, aproperty, propertytyp):
    context.execute_steps(f'* All "{ifcos_query}" elements with a "{pset}.{aproperty}" are of type "{propertytyp}"')


# ************************************************************************************************
# Propertywerte


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


# ************************************************************************************************
# Vergleich Propertywerte


@step('Der Attributewert von "{aproperty1}.{pset1}" stimmt mit dem Attributewert von "{aproperty2}.{pset2}" überein')
def step_impl(context, aproperty1, pset1, aproperty2, pset2):
    context.execute_steps(f'* The attribute value of "{aproperty1}.{pset1}" equals the attribute value of "{aproperty2}.{pset2}" if both are given')
    # "if both are given" im engl. text ist falsch, das sollte in extra tests vorher geprueft werden


@step('Der Wert des Attributes "{pset}.{aproperty}" ist gleich dem Wert des Bauteilattributes Name')
def step_impl(context, pset, aproperty):
    context.execute_steps(f'* The attribute value of "{pset}.{aproperty}" equals the class attribute Name')
