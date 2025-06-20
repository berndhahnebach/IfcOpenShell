from behave import step


@step('Alle "{ifcos_query}" Bauteile haben eine Repräsentation (Geometrie) zugewiesen.')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements must have a representation (geometry) assigned')


@step('Alle "{ifcos_query}" Bauteile verwenden eine geometrische Repräsentation der Klasse "{representation_class}"')
def step_impl(context, ifcos_query, representation_class):
    context.execute_steps(f'* All "{ifcos_query}" elements have an "{representation_class}" representation')


@step('Alle "{ifcos_query}" Bauteile verwenden explixit nicht eine geometrische Repräsentation der Klasse "{representation_class}"')
def step_impl(context, ifcos_query, representation_class):
    context.execute_steps(f'* All "{ifcos_query}" elements do not have an "{representation_class}" representation')
