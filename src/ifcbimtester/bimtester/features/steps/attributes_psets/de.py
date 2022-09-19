from behave import step


@step('Alle "{ifc_class}" Bauteile haben exakt "{attribut_count}" Attribute im PSet "{pset}" angehängt')
def step_impl(context, ifc_class, attribut_count, pset):
    context.execute_steps(f'* All "{ifc_class}" elements have exactly "{attribut_count}" in the pset "{pset}"')


@step('Alle "{ifc_class}" Bauteile haben das Attribut "{aproperty}" im PSet "{pset}"')
def step_impl(context, ifc_class, pset, aproperty):
    context.execute_steps(f'* All "{ifc_class}" elements have an "{aproperty}" property in the "{pset}" pset')


@step('Alle "{ifc_class}" Bauteile haben das PSet.Attribut "{pset}.{aproperty}" angehängt')
def step_impl(context, ifc_class, pset, aproperty):
    context.execute_steps(f'* All "{ifc_class}" elements have a "{pset}.{aproperty}" property')


@step('Alle "{ifc_class}" Bauteile haben das PSet.Attribut "{pset}.{aproperty}" nicht angehängt')
def step_impl(context, ifc_class, pset, aproperty):
    context.execute_steps(f'* All "{ifc_class}" elements have not a "{pset}.{aproperty}" property')


@step('Alle "{ifc_classes}" Bauteile haben das Attribut "{aproperty}" im Common PSet angehängt')
def step_impl(context, ifc_classes, aproperty):
    context.execute_steps(f'* All "{ifc_classes}" elements have a property "{aproperty}" in the Common pset')


@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{pset}.{aproperty}" haben den Attributtyp "{propertytyp}"')
def step_impl(context, ifc_class, pset, aproperty, propertytyp):
    context.execute_steps(f'* All "{ifc_class}" elements with a "{pset}.{aproperty}" are of type "{propertytyp}"')


@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{pset}.{aproperty}" haben den Attributwert "{propertyvalue}"')
def step_impl(context, ifc_class, pset, aproperty, propertyvalue):
    context.execute_steps(f'* All "{ifc_class}" elements with a "{pset}.{aproperty}" have a value of "{propertyvalue}"')


@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{pset}.{aproperty}" haben einen Attributwert aus dem Bereich von "{valuerange}"')
def step_impl(context, ifc_class, pset, aproperty, valuerange):
    context.execute_steps(f'* All "{ifc_class}" elements with a "{pset}.{aproperty}" have a value range of "{valuerange}"')


@step('Alle "{ifc_class}" Bauteile mit dem Attribut "{pset}.{aproperty}" haben die Zeichenfolge "{some_chars}" nicht im Attributwert"')
def step_impl(context, ifc_class, pset, aproperty, some_chars):
    context.execute_steps(f'* All "{ifc_class}" elements with a "{pset}.{aproperty}" have the chars "{some_chars}" not in the property value"')


@step('Der Attributewert von "{aproperty1}.{pset1}" stimmt mit dem Attributewert von "{aproperty2}.{pset2}" überein')
def step_impl(context, aproperty1, pset1, aproperty2, pset2):
    context.execute_steps(f'* The attribute value of "{aproperty1}.{pset1}" equals the attribute value of "{aproperty2}.{pset2}" if both are given')
    # "if both are given" im engl. text ist falsch, das sollte in extra tests vorher geprueft werden


@step('Der Wert des Attributes "{pset}.{aproperty}" ist gleich dem Wert des Bauteilattributes Name')
def step_impl(context, pset, aproperty):
    context.execute_steps(f'* The attribute value of "{pset}.{aproperty}" equals the class attribute Name')


@step('Alle "{ifc_class}" Bauteile haben keine Bauteilschichtattribute (IfcComplexProperty) angehängt')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements have no element layer properties (IfcComplexProperty)')


# attributvorhandensein in abhangigkeit von material
@step('Alle "{ifc_class}" Bauteile mit dem Material "{material}" haben das PSet.Attribut "{pset}.{property}" angehängt')
def step_impl(context, ifc_class, material, pset, property):
    context.execute_steps(f'* All "{ifc_class}" elements with the material named "{material}" have a "{pset}.{property}" property')


@step('Alle "{ifc_class}" Bauteile die NICHT das Material "{material}" haben, haben das Attribut.PSet "{pset}.{property}" NICHT angehängt')
def step_impl(context, ifc_class, material, pset, property):
    context.execute_steps(f'* All "{ifc_class}" elements which do not have a material named "{material}" have not a "{pset}.{property}" property')


"""
# ***************************************************************************************************************
# TODO make a englisch one, ATM not in use
@step('Alle "{ifc_class}" Bauteile ohne Bauteilschichtattribute haben das Attribut.PSet "{pset}.{aproperty}" angehängt')
def step_impl(context, ifc_class, pset, aproperty):
    apm.eleclass_without_complexlayerattributes_has_property(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{pset}.{aproperty}" angehängt')
def step_impl(context, ifc_class, pset, aproperty):
    apm.eleclass_with_complexlayerattributes_has_property(
        context,
        ifc_class,
        aproperty,
        pset
    )


# ***************************************************************************************************************
# TODO finish method
@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{pset}.{aproperty}" in allen Schichten angehängt')
def step_impl(context, ifc_class, pset, aproperty):
    apm.eleclass_with_complexlayerattributes_has_property_in_all_layer(
        context,
        ifc_class,
        aproperty,
        pset
    )


# ***************************************************************************************************************
# TODO implement methods
@step('Alle "{ifc_class}" Bauteile ohne Bauteilschichtattribute haben das Attribut.PSet "{pset}.{aproperty}" nicht angehängt')
def step_impl(context, ifc_class, pset, aproperty):
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{pset}.{aproperty}" nicht angehängt')
def step_impl(context, ifc_class, pset, aproperty):
    apm.eleclass_has_property_implement(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile mit Bauteilschichtattributen haben das Attribut.PSet "{pset}.{aproperty}" nicht in irgendeiner Schicht angehängt')
def step_impl(context, ifc_class, pset, aproperty):
    apm.eleclass_has_property_implement(
        context,
        ifc_class,
        aproperty,
        pset
    )


# ***************************************************************************************************************
# TODO, Beginn old, pruefen was funktioniert
@step('Alle "{ifc_class}" Bauteile haben das Attribut.PSet "{pset}.{aproperty}" ausschliesslich direkt angehängt')
def step_impl(context, ifc_class, pset, aproperty):
    apm.eleclass_has_property_directly_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteile haben das Attribut.PSet "{pset}.{aproperty}" nicht direkt angehängt')
def step_impl(context, ifc_class, pset, aproperty):
    apm.eleclass_has_not_property_directly_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )


@step('Alle "{ifc_class}" Bauteilschichten haben das Attribut.PSet "{pset}.{aproperty}" angehängt')
def step_impl(context, ifc_class, pset, aproperty):
    apm.eleclass_matlayer_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )

@step('Bis auf "{minus_ifc_class}" Bauteile haben alle "{ifc_class}" das Attribut.PSet "{pset}.{aproperty}" direkt angehängt')
def step_impl(context, ifc_class, minus_ifc_class, pset, aproperty):
    apm.eleclass_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset,
        minus_ifc_class # different oder!
    )


@step('Alle "{ifc_class}" Bauteile haben das Attribut.PSet "{pset}.{aproperty}" in einer Bauteilschicht angehängt')
def step_impl(context, ifc_class, pset, aproperty):
    apm.eleclass_has_property_in_layer_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )
# Ende old, pruefen was funktioniert
# *************************************
"""
