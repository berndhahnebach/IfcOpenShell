from behave import step

import bimtester.features.steps.attributes_qsets.en as the_methods

@step('Alle "{ifc_class}" Bauteile aus dem Material "{material}" haben ausschliesslich eine "{geometryproperty}" der Werte "{valuerange}" Meter')
def step_impl(context, ifc_class, material, geometryproperty, valuerange):
    # context.execute_steps(f'* all "{ifc_class}" elements made from material "{material}" do only have the "{geometryproperty}" value range "{valuerange}" meter')
    the_methods.eleclass_material_has_quantity_valuerange_of(
        context,
        ifc_class,
        material,
        geometryproperty,
        valuerange
    )
