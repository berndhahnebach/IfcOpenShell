from behave import step


@step('Alle "{ifc_class}" Bauteile verwenden eine geometrische ReprĂ¤sentation der Klasse "{representation_class}"')
def step_impl(context, ifc_class, representation_class):
    context.execute_steps(f'* All "{ifc_class}" elements have an "{representation_class}" representation')


@step('Alle "{ifc_class}" Bauteile haben überhaupt eine Geometrie, die verarbeitet werden kann.')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements must have a geometric representation which could be parsed')


@step('Alle "{ifc_class}" Bauteile haben eine Geometrie ohne Fehler.')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements with existing geometry have no errors')


@step('Alle "{ifc_class}" Bauteile haben in ihrer Geometrie eine maximale Kantenlänge von "{max_edge_length}" mm.')
def step_impl(context, ifc_class, max_edge_length):
    context.execute_steps(f'* All "{ifc_class}" elements must have a maximum edge length of "{max_edge_length}" mm in their geometry')


@step('Alle "{ifc_class}" Bauteile haben eine Geometrie welche nur aus einem Volumenkörper besteht.')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements must have a geometry consisting only one volume solid')


@step('Alle "{ifc_class}" Bauteile haben eine Geometrie die nicht leer ist, weil eine Öffnung das gesamte Bauteil beinhaltet.')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements must have a geometry which is not empty just becaause of a opening bigger than the element')


# deprecated
@step('Alle "{ifc_class}" Bauteile haben eine geometrische Repräentation ohne Fehler')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements must have a geometric representation without errors')
