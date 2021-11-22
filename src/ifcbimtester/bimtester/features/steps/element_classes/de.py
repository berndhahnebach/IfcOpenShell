from behave import step

import bimtester.features.steps.element_classes.en as the_methods


@step('Es sind ausschliesslich "{ifc_classes}" Bauteile vorhanden')
def step_impl(context, ifc_classes):
    # context.execute_steps(f'* There are exclusively "{ifc_class}" elements only')
    the_methods.only_eleclasses(
        context,
        ifc_classes
    )


@step('Es sind keine "{ifc_class}" Bauteile vorhanden')
def step_impl(context, ifc_class):
    context.execute_steps(f'* There are no "{ifc_class}" elements')


@step('Aus folgendem Grund gibt es keine "{ifc_class}" Bauteile: {reason}')
def step_impl(context, ifc_class, reason):
    context.execute_steps(f'* There are no "{ifc_class}" elements because "{reason}"')


@step('Alle "{ifc_class}" Bauteilklassenattribute haben einen Wert')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements class attributes have a value')


@step('Bei allen "{ifc_class}" Bauteilen ist der Name angegeben')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements have a name given')


@step('Bei allen "{ifc_class}" Bauteilen ist die Beschreibung angegeben')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements have a description given')


@step('Alle "{ifc_class}" Bauteile haben einen zugeordneten Layer')
def step_impl(context, ifc_class):
    # context.execute_steps(f'* All "{ifc_class}" elements have an layer assigned')
    the_methods.eleclass_has_layer_assigned(
        context,
        ifc_class
    )


@step('Kein "{ifc_class}" Bauteil hat einen Layer mit dem Namen "{layer_name}"')
def step_impl(context, ifc_class, layer_name):
    # context.execute_steps(f'* No "{ifc_class}" element has a layer named "{layer_name}"')
    the_methods.eleclass_has_not_layer_with_name(
        context,
        ifc_class,
        layer_name
    )


@step('Alle "{ifc_class}" Bauteile haben ein zugeordnetes Material')
def step_impl(context, ifc_class):
    # context.execute_steps(f'* All "{ifc_class}" elements have a material assigned')
    the_methods.eleclass_has_material_assigned(
        context,
        ifc_class
    )


@step('Kein "{ifc_class}" Bauteil hat ein Material mit dem Namen "{material_name}"')
def step_impl(context, ifc_class, material_name):
    # context.execute_steps(f'* No "{ifc_class}" element has a material named "{material_name}"')
    the_methods.eleclass_has_not_material_with_name(
        context,
        ifc_class,
        material_name
    )
