from behave import step
from behave import use_step_matcher

import bimtester.features.steps.attributes_psets.en as the_methods

# since en module is imported and the expression matcher is changed there
# it needs to explicit set here once again after the import
use_step_matcher("parse")


@step('Alle "{ifc_class}" Bauteile haben das Attribut "{aproperty}" im PSet "{pset}"')
def step_impl(context, ifc_class, aproperty, pset):
    context.execute_steps(f'* All "{ifc_class}" elements have an "{aproperty}" property in the "{pset}" pset')


@step('Alle "{ifc_class}" Bauteile haben das Attribut.PSet "{aproperty}.{pset}" angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    # context.execute_steps(f'* All "{ifc_class}" elements have a "{aproperty}.{pset}" property')
    the_methods.eleclass_minus_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )

@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{aproperty}.{pset}" haben den Attributtyp "{propertytyp}"')
def step_impl(context, ifc_class, aproperty, pset, propertytyp):
    context.execute_steps(f'* All "{ifc_class}" elements with a "{aproperty}.{pset}" are of type "{propertytyp}"')


@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{aproperty}.{pset}" haben den Attributwert "{propertyvalue}"')
def step_impl(context, ifc_class, aproperty, pset, propertyvalue):
    context.execute_steps(f'* All "{ifc_class}" elements with a "{aproperty}.{pset}" have a value of "{propertyvalue}"')


@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{aproperty}.{pset}" haben einen Attributwert aus dem Bereich von "{valuerange}"')
def step_impl(context, ifc_class, aproperty, pset, valuerange):
    context.execute_steps(f'* All "{ifc_class}" elements with a "{aproperty}.{pset}" have a value range of "{valuerange}"')


@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{aproperty}.{pset}" haben die Zeichenfolge "{some_chars}" nicht im Attributwert"')
def step_impl(context, ifc_class, aproperty, pset, some_chars):
    context.execute_steps(f'* All "{ifc_class}" elements with a "{aproperty}.{pset}" have the chars "{some_chars}" not in the property value"')


@step('Der Attributewert von "{aproperty1}.{pset1}" stimmt mit dem Attributewert von "{aproperty2}.{pset2}" überein')
def step_impl(context, aproperty1, pset1, aproperty2, pset2):
    context.execute_steps(f'* The attribute value of "{aproperty1}.{pset1}" equals the attribute value of "{aproperty2}.{pset2}" if both are given')
    # if both are given ist falsch, das sollte in extra tests vorher geprueft werden


@step('Der Wert des Attributes "{aproperty}.{pset}" ist gleich dem Wert Bauteilattributes Name')
def step_impl(context, aproperty, pset):
    context.execute_steps(f'* The attribute value of "{aproperty}.{pset}" equals the class attribute Name')


@step('Alle "{ifc_class}" Bauteile haben keine Bauteilschichtattribute (IfcComplexProperty) angehängt')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements have no element layer properties (IfcComplexProperty)')



"""
# ***************************************************************************************************************
# TODO make a englisch one, ATM not in use
@step('Alle "{ifc_class}" Bauteile ohne Bauteilschichtattribute haben das Attribut.PSet "{aproperty}.{pset}" angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    apm.eleclass_without_complexlayerattributes_has_property(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{aproperty}.{pset}" angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    apm.eleclass_with_complexlayerattributes_has_property(
        context,
        ifc_class,
        aproperty,
        pset
    )


# ***************************************************************************************************************
# TODO finish method
@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{aproperty}.{pset}" in allen Schichten angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    apm.eleclass_with_complexlayerattributes_has_property_in_all_layer(
        context,
        ifc_class,
        aproperty,
        pset
    )


# ***************************************************************************************************************
# TODO implement methods
@step('Alle "{ifc_class}" Bauteile ohne Bauteilschichtattribute haben das Attribut.PSet "{aproperty}.{pset}" nicht angehängt')
def step_impl(context, ifc_class, aproperty, pset):
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{aproperty}.{pset}" nicht angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    apm.eleclass_has_property_implement(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{aproperty}.{pset}" nicht in irgendeiner Schicht angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    apm.eleclass_has_property_implement(
        context,
        ifc_class,
        aproperty,
        pset
    )


# ***************************************************************************************************************
# TODO, Beginn old, pruefen was funktioniert
@step('Alle "{ifc_class}" Bauteile haben das Attribut.PSet "{aproperty}.{pset}" ausschliesslich direkt angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    apm.eleclass_has_property_directly_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile haben das Attribut.PSet "{aproperty}.{pset}" nicht direkt angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    apm.eleclass_has_not_property_directly_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteilschichten haben das Attribut.PSet "{aproperty}.{pset}" angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    apm.eleclass_matlayer_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )

@step('Bis auf "{minus_ifc_class}" Bauteile haben alle "{ifc_class}" das Attribut.PSet "{aproperty}.{pset}" direkt angehängt')
def step_impl(context, ifc_class, minus_ifc_class, aproperty, pset):
    apm.eleclass_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset,
        minus_ifc_class # different oder!
    )


@step('Alle "{ifc_class}" Bauteile haben das Attribut.PSet "{aproperty}.{pset}" in einer Bauteilschicht angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    apm.eleclass_has_property_in_layer_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )
# Ende old, pruefen was funktioniert
# *************************************
"""
