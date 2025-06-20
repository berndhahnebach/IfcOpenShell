from behave import step


@step('Alle "{ifcos_query}" Bauteile haben einen zugeordneten Layer')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements have an layer assigned')


# Alle "{ifcos_query}" Bauteile mit einem zugeordneten Layer, haben nicht den Layeramen "{layer_name}"
@step('Kein "{ifcos_query}" Bauteil hat einen Layer mit dem Namen "{layer_name}"')
def step_impl(context, ifcos_query, layer_name):
    context.execute_steps(f'* No "{ifcos_query}" element has a layer named "{layer_name}"')


@step('Alle "{ifcos_query}" Bauteile mit einem zugeordneten Layer haben den Layernamen "{layer_name}"')
def step_impl(context, ifcos_query, layer_name):
    context.execute_steps(f'* All "{ifcos_query}" elements that have a layer assigned use the layer name "{layer_name}"')


@step('Alle "{ifcos_query}" Bauteile mit einem zugeordneten Layer haben einen der folgenden Layernamen "{valuerange}"')
def step_impl(context, ifcos_query, valuerange):
    context.execute_steps(f'* All "{ifcos_query}" elements that have a layer assigned use one of these layer names "{valuerange}"')
