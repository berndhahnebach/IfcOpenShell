from behave import step


@step('Alle "{ifc_class}" Bauteile mit einem zugeordneten Layer haben einen der folgenden Layernamen "{valuerange}"')
def step_impl(context, ifc_class, valuerange):
    context.execute_steps(f'* All "{ifc_class}" elements which have a layer assigned use one of these layer names "{valuerange}"')


@step('Alle "{ifc_class}" Bauteile haben einen zugeordneten Layer')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements have an layer assigned')


@step('Kein "{ifc_class}" Bauteil hat einen Layer mit dem Namen "{layer_name}"')
def step_impl(context, ifc_class, layer_name):
    context.execute_steps(f'* No "{ifc_class}" element has a layer named "{layer_name}"')
