from behave import step

import attributes_psets_methods as apm
from utils import switch_locale


the_lang = "de"

@step('Alle "{ifc_class}" Bauteile haben keine Bauteilschichtattribute (IfcComplexProperty) angehängt')
def step_impl(context, ifc_class):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_no_complex_property(
        context,
        ifc_class,
    )


@step('Alle "{ifc_class}" Bauteile haben das Attribut.PSet "{aproperty}.{pset}" angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile ohne Bauteilschichtattribute haben das Attribut.PSet "{aproperty}.{pset}" angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_without_complexlayerattributes_has_property(
        context,
        ifc_class,
        aproperty,
        pset
    )


# TODO implement method
@step('Alle "{ifc_class}" Bauteile ohne Bauteilschichtattribute haben das Attribut.PSet "{aproperty}.{pset}" nicht angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_implement(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{aproperty}.{pset}" angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_with_complexlayerattributes_has_property(
        context,
        ifc_class,
        aproperty,
        pset
    )


# TODO implement method
@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{aproperty}.{pset}" nicht angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_implement(
        context,
        ifc_class,
        aproperty,
        pset
    )


# TODO finish
@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{aproperty}.{pset}" in allen Schichten angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_with_complexlayerattributes_has_property_in_all_layer(
        context,
        ifc_class,
        aproperty,
        pset
    )


# TODO implement method
@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{aproperty}.{pset}" nicht in irgendeiner Schicht angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_implement(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{aproperty}.{pset}" haben den Attributtyp "{propertytyp}"')
def step_impl(context, ifc_class, aproperty, pset, propertytyp):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_propertytype_of(
        context,
        ifc_class,
        aproperty,
        pset,
        propertytyp
    )


@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{aproperty}.{pset}" haben den Attributwert "{propertyvalue}"')
def step_impl(context, ifc_class, aproperty, pset, propertyvalue):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_propertyvalue_of(
        context,
        ifc_class,
        aproperty,
        pset,
        propertyvalue
    )

@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{aproperty}.{pset}" haben einen Attributwert aus dem Bereich von "{valuerange}"')
def step_impl(context, ifc_class, aproperty, pset, valuerange):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_valuerange_of(
        context,
        ifc_class,
        aproperty,
        pset,
        valuerange
    )


@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{aproperty}.{pset}" haben die Zeichenfolge "{some_chars}" nicht im Attributwert"')
def step_impl(context, ifc_class, aproperty, pset, some_chars):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_hasnot_chars_in_property_value(
        context,
        ifc_class,
        aproperty,
        pset,
        some_chars
    )


@step('Der Attributewert von "{aproperty1}.{pset1}" stimmt mit dem Attributewert von "{aproperty2}.{pset2}" überein')
def step_impl(context, aproperty1, pset1, aproperty2, pset2):
    switch_locale(context.localedir, the_lang)
    apm.propertyvalue1_equals_propertyvalue2(
        context,
        aproperty1,
        pset1,
        aproperty2,
        pset2
    )


@step('Der Wert des Attributes "{aproperty}.{pset}" ist gleich dem Wert Bauteilattributes Name')
def step_impl(context, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.propertyvalue1_equals_elementclassname(
        context,
        aproperty,
        pset
    )


# ***************************************************************************************************************
# ***************************************************************************************************************
# ***************************************************************************************************************
# Beginn old, pruefen was funktioniert
@step('Alle "{ifc_class}" Bauteile haben das Attribut.PSet "{aproperty}.{pset}" ausschliesslich direkt angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_directly_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile haben das Attribut.PSet "{aproperty}.{pset}" nicht direkt angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_not_property_directly_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteilschichten haben das Attribut.PSet "{aproperty}.{pset}" angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_matlayer_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )

@step('Bis auf "{minus_ifc_class}" Bauteile haben alle "{ifc_class}" das Attribut.PSet "{aproperty}.{pset}" direkt angehängt')
def step_impl(context, ifc_class, minus_ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset,
        minus_ifc_class # different oder!
    )


@step('Alle "{ifc_class}" Bauteile haben das Attribut.PSet "{aproperty}.{pset}" in einer Bauteilschicht angehängt')
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_in_layer_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )
# Ende old, pruefen was funktioniert
# *************************************

