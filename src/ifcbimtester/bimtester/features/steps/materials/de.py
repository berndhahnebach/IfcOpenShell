from behave import step


@step('Alle "{ifc_class}" Bauteile mit einem zugeordneten Material haben einen der folgenden Materialnamen "{valuerange}"')
def step_impl(context, ifc_class, valuerange):
    context.execute_steps(f'* All "{ifc_class}" elements which have a material assigned use one of these material names "{valuerange}"')


@step('Alle "{ifc_class}" Bauteile haben ein zugeordnetes Material')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements have one material assigned')


@step('Kein "{ifc_class}" Bauteil hat ein Material mit dem Namen "{material_name}"')
def step_impl(context, ifc_class, material_name):
    context.execute_steps(f'* No "{ifc_class}" element has a material named "{material_name}"')
