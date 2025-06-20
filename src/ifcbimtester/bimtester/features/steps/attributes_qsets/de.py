from behave import step


@step('Alle "{ifcos_query}" Bauteile haben mindestens ein Quantity Volumen angehängt.')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements must have at least one volume quantity attached.')
    # list of possible quantity property names for volume is hard coded


@step('Mindestens ein "{ifcos_query}" Bauteil hat mindestens ein Quantity in einem Mengen-PSet angehängt (IFC-Exporteinstellung mit Mengen)')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* At least one "{ifcos_query}" element does have a quantity in a QSet (export setting for quantities)')


@step('Alle "{ifcos_query}" Bauteile haben mindestens ein Quantity in einem Mengen-PSet angehängt (Alle Bauteile haben Mengen exportiert)')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements have at least one quantity in a quantity pset (all elements do have quantities exported)')


@step('Alle "{ifcos_query}" Bauteile haben ausschliesslich Quantitywerte ungleich 0.0')
def step_impl(context, ifcos_query):
    context.execute_steps(f'* All "{ifcos_query}" elements do only have non-zero quantity values')


@step('Alle "{ifcos_query}" Bauteile haben den Geometriewert QuantitySet.Quantity "{aqset}.{aquantity}" angehängt')
def step_impl(context, ifcos_query, aqset, aquantity):
    context.execute_steps(f'* All "{ifcos_query}" elements have a "{aqset}.{aquantity}" quantity')


@step('Alle "{ifcos_query}" Bauteile mit dem Geometriewert "{aqset}.{aquantity}" haben ausschliesslich Werte aus dem Wertebereich "{valuerange}"')
def step_impl(context, ifcos_query, aqset, aquantity, valuerange):
    context.execute_steps(f'* All "{ifcos_query}" elements with "{aqset}.{aquantity}" attached do only use the value range of "{valuerange}"')
