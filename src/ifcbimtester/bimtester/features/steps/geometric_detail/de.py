from behave import step


@step('Alle "{ifc_class}" Bauteile müssen eine geometrische Repräsentation der Klasse "{representation_class}" verwenden')
def step_impl(context, ifc_class, representation_class):
    context.execute_steps(f'* All {ifc_class} elements have an "{representation_class}" representation')


@step('Alle "{ifc_class}" Bauteile müssen geometrische Repräsentationen ohne Fehler haben')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements must have a geometric representation without errors')
